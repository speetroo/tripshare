from django.contrib import admin
from .models import Group, Currency, Expense


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    filter_horizontal = ("members",)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "group", "rate_to_eur")
    list_filter = ("group", "code")
    search_fields = ("code", "name")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("description", "group", "amount", "currency", "paid_by", "date")
    list_filter = ("group", "currency", "paid_by")
    search_fields = ("description",)
    filter_horizontal = ("beneficiaries",)
