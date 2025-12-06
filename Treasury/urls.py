from django.urls import path
from .views import *

app_name ="Treasury"
urlpatterns = [
    path('list/', TreasuryList.as_view(), name="TreasuryList"),
    path('trach/', TreasuryTrachList.as_view(), name="TreasuryTrachList"),
    path('create/', TreasuryCreate.as_view(), name="TreasuryCreate"),
    path('update/<int:pk>/', TreasuryUpdate.as_view(), name="TreasuryUpdate"),
    path('details/<int:pk>/', TreasuryDetails.as_view(), name="TreasuryDetails"),
    path('details_div/<int:pk>/', TreasuryOperationDiv.as_view(), name="TreasuryOperationDiv"),
    path('delete/<int:pk>', TreasuryDelete.as_view(), name="TreasuryDelete"),
    path('restore/<int:pk>', TreasuryRestore.as_view(), name="TreasuryRestore"),
    path('superDelete/<int:pk>', TreasurySuperDelete.as_view(), name="TreasurySuperDelete"),
    path('create/operation_in/<int:pk>/', OperationInCreate.as_view(), name="OperationInCreate"),
    path('creat/operation_out/<int:pk>/', OperationOutCreate.as_view(), name="OperationOutCreate"),
    path('opertation_superDelete/<int:pk>/', OperationSuperDelete.as_view(), name="OperationSuperDelete"),
    path('treasury_report/<int:pk>/', TreasuryReport, name="TreasuryReport"),
]