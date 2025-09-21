from django.urls import path
from .views import *
app_name = "transactions"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("reports/", ReportView.as_view(), name="reports"),
    path("transactions/", TransactionListCreateView.as_view(), name="transaction-list"),
    path("transactions/<int:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("accounts/", AccountListCreateView.as_view(), name="account-list"),
    path("accounts/<int:pk>/", AccountDetailView.as_view(), name="account-detail"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
]

