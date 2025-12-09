from decimal import Decimal

from django.contrib.auth import logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect

from .models import Group, Currency, compute_settlement_operations_from_balances
from .forms import GroupForm, ExpenseForm, CurrencyForm

from collections import defaultdict

def home(request):
    if request.user.is_authenticated:
        return redirect("group_list")
    else:
        return redirect("login")
    
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # log the user in directly after registration
            auth_login(request, user)
            return redirect("group_list")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, "core/group_list.html", {"groups": groups})


@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    balances = group.get_user_balances()
    balances_items = sorted(balances.items(), key=lambda item: item[0].username)
    settlements = group.get_settlement_operations()
    return render(
        request,
        "core/group_detail.html",
        {
            "group": group,
            "balances_items": balances_items,
            "settlements": settlements,
        },
    )



@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            return redirect("group_detail", pk=group.pk)
    else:
        form = GroupForm()
    return render(request, "core/create_group.html", {"form": form})

# Currently unused, generic create_expense function
@login_required
def create_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save()
            return redirect("group_detail", pk=expense.group.pk)
    else:
        form = ExpenseForm()
    return render(request, "core/create_expense.html", {"form": form})


@login_required
def create_expense_for_group(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if request.method == "POST":
        form = ExpenseForm(request.POST, group=group)
        if form.is_valid():
            expense = form.save()
            return redirect("group_detail", pk=group.pk)
    else:
        form = ExpenseForm(group=group)

    return render(
        request,
        "core/create_expense.html",
        {"form": form, "group": group},
    )


@login_required
def add_currency_to_group(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if request.method == "POST":
        form = CurrencyForm(request.POST)
        if form.is_valid():
            currency = form.save(commit=False)
            currency.group = group  # attach to this group
            currency.save()
            return redirect("group_detail", pk=group.pk)
    else:
        form = CurrencyForm()

    return render(
        request,
        "core/add_currency.html",
        {"form": form, "group": group},
    )


@login_required
def my_status(request):
    user = request.user
    groups = user.expense_groups.all()  # groups where this user is a member

    rows = []

    for group in groups:
        balances = group.get_user_balances()
        my_balance = balances.get(user, Decimal("0.00"))

        # Total paid by this user in this group, converted to EUR
        total_paid = Decimal("0.00")
        expenses_paid = group.expenses.filter(paid_by=user).select_related("currency")
        for expense in expenses_paid:
            total_paid += expense.amount * expense.currency.rate_to_eur

        rows.append(
            {
                "group": group,
                "total_paid_eur": total_paid,
                "net_balance_eur": my_balance,
            }
        )

    return render(request, "core/my_status.html", {"rows": rows})


@login_required
def global_clearing(request):
    """
    Global clearing across all groups:
    - Compute each user's global net balance in EUR
    - Compute settlement operations across all groups together
    """
    global_balances = defaultdict(lambda: Decimal("0.00"))

    for group in Group.objects.all():
        balances = group.get_user_balances()
        for user, bal in balances.items():
            global_balances[user] += bal

    # Convert defaultdict to normal dict
    global_balances = dict(global_balances)

    settlements = compute_settlement_operations_from_balances(global_balances)
    balances_items = sorted(global_balances.items(), key=lambda item: item[0].username)

    context = {
        "balances_items": balances_items,
        "settlements": settlements,
    }
    return render(request, "core/global_clearing.html", context)



@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("group_list")

