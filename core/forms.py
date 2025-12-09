from django import forms
from .models import Group, Expense, Currency


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "members"]
        widgets = {
            "members": forms.CheckboxSelectMultiple,
        }


class ExpenseForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta:
        model = Expense
        fields = [
            "group",
            "description",
            "amount",
            "currency",
            "paid_by",
            "beneficiaries",
            "date",
        ]
        widgets = {
            "beneficiaries": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        group = kwargs.pop("group", None)  # we’ll pass this from the view
        super().__init__(*args, **kwargs)

        if group is not None:
            # Fix the group to this one and hide the field
            self.fields["group"].initial = group
            self.fields["group"].widget = forms.HiddenInput()

            # Limit choices to this group
            self.fields["currency"].queryset = group.currencies.all()
            self.fields["paid_by"].queryset = group.members.all()
            self.fields["beneficiaries"].queryset = group.members.all()

            # Optional: default beneficiaries = all members
            if not self.is_bound:  # only for GET, not POST
                self.fields["beneficiaries"].initial = group.members.all()


class CurrencyForm(forms.ModelForm):
        class Meta:
            model = Currency
            fields = ["code", "name", "rate_to_eur"]
