from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), 
    path("register/", views.register, name="register"),
    path("my-status/", views.my_status, name="my_status"),
    path("clearing/", views.global_clearing, name="global_clearing"),

    path("groups/", views.group_list, name="group_list"),
    path("groups/new/", views.create_group, name="create_group"),
    path("groups/<int:pk>/", views.group_detail, name="group_detail"),
    path(
        "groups/<int:pk>/expenses/new/",
        views.create_expense_for_group,
        name="create_expense_for_group",
    ),
    path(
        "groups/<int:pk>/currencies/new/",
        views.add_currency_to_group,
        name="add_currency_to_group",
    ),

    path("expenses/new/", views.create_expense, name="create_expense"), # generic expense, currently unused

    path("logout/", views.logout_view, name="logout"),
]
