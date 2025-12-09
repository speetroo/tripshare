from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User

def compute_settlement_operations_from_balances(balances):
    """
    balances: dict {user: Decimal balance_in_eur}
    Positive -> user should receive money.
    Negative -> user should pay money.

    Returns a list of operations:
    {"from": user_who_pays, "to": user_who_receives, "amount": Decimal_in_eur}
    """
    creditors = []  # users who should receive
    debtors = []    # users who should pay

    for user, bal in balances.items():
        if bal > 0:
            creditors.append([user, bal])
        elif bal < 0:
            debtors.append([user, -bal])  # store positive owed amount

    if not creditors or not debtors:
        return []

    # sort so we roughly match largest amounts first
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)

    ops = []
    i = j = 0

    while i < len(debtors) and j < len(creditors):
        debtor, d_amount = debtors[i]
        creditor, c_amount = creditors[j]

        pay = min(d_amount, c_amount)

        if pay > 0:
            ops.append(
                {
                    "from": debtor,
                    "to": creditor,
                    "amount": pay,
                }
            )

        d_amount -= pay
        c_amount -= pay

        if d_amount == 0:
            i += 1
        else:
            debtors[i][1] = d_amount

        if c_amount == 0:
            j += 1
        else:
            creditors[j][1] = c_amount

    return ops


# Group – a trip/event with members
class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(
        User,
        related_name="expense_groups",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_user_balances(self):
        """
        Returns a dict {user: net_balance_in_eur}
        Positive -> user should receive money
        Negative -> user should pay money
        """
        # start all balances at 0
        balances = {user: Decimal("0.00") for user in self.members.all()}
        
        expenses = (
            self.expenses
            .select_related("currency", "paid_by")
            .prefetch_related("beneficiaries")
        )
        
        for expense in expenses:
            amount_eur = expense.amount * expense.currency.rate_to_eur
            beneficiaries = list(expense.beneficiaries.all())
            
            if not beneficiaries:
                # if nobody is marked as beneficiary, skip this expense
                continue
            
            share = amount_eur / len(beneficiaries)
            
            # payer gets credited the full amount
            if expense.paid_by in balances:
                balances[expense.paid_by] += amount_eur
            
            # each beneficiary owes their share
            for user in beneficiaries:
                if user in balances:
                    balances[user] -= share
        
        return balances
    
    def get_settlement_operations(self):
        """
        Returns a list of settlement operations, each as:
        {"from": user_who_pays, "to": user_who_receives, "amount": Decimal_in_eur}
        """
        balances = self.get_user_balances()
        return compute_settlement_operations_from_balances(balances)


# Currency – currency + rate to EUR, per group
class Currency(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="currencies",
    )
    code = models.CharField(max_length=10)  # e.g. "EUR", "USD"
    name = models.CharField(max_length=50, blank=True)  # optional nice name
    rate_to_eur = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="1 unit of this currency is worth how many EUR?",
    )

    def __str__(self):
        return f"{self.code} ({self.group.name})"

# Expense – who paid what, in which group & currency
class Expense(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="expenses",
    )
    paid_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="paid_expenses",
    )
    beneficiaries = models.ManyToManyField(
        User,
        related_name="benefit_expenses",
        blank=True,
        help_text="Who enjoyed this expense?",
    )
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount} {self.currency.code}"
