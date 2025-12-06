from django.urls import path
from .views import *

app_name ="Wool"
urlpatterns = [
    path('WoolSupplierList/', WoolSupplierList.as_view(), name="WoolSupplierList"),
    path('WoolSupplierTrashList/', WoolSupplierTrashList.as_view(), name="WoolSupplierTrashList"),
    path('WoolSupplierCreate/', WoolSupplierCreate.as_view(), name="WoolSupplierCreate"),
    path('WoolSupplierUpdate/<int:pk>/', WoolSupplierUpdate.as_view(), name="WoolSupplierUpdate"),
    path('WoolSupplierDelete/<int:pk>/', WoolSupplierDelete.as_view(), name="WoolSupplierDelete"),
    path('WoolSupplierRestore/<int:pk>/', WoolSupplierRestore.as_view(), name="WoolSupplierRestore"),
    path('WoolSupplierSuperDelete/<int:pk>/', WoolSupplierSuperDelete.as_view(), name="WoolSupplierSuperDelete"),

    path('WoolSupplierQuantity/<int:pk>/', WoolSupplierQuantityDetail, name="WoolSupplierQuantity"),
    path('AddWoolSupplierQuantity/<int:pk>/', AddWoolSupplierQuantity, name="AddWoolSupplierQuantity"),
    path('DelWoolSupplierQuantity/<int:pk>/', DelWoolSupplierQuantity, name="DelWoolSupplierQuantity"),

    path('WoolSupplierPayment/<int:pk>/', WoolSupplierPaymentDetail, name="WoolSupplierPayment"),
    path('AddWoolSupplierPayment/<int:pk>/', AddWoolSupplierPayment, name="AddWoolSupplierPayment"),
    path('DelWoolSupplierPayment/<int:pk>/', DelWoolSupplierPayment, name="DelWoolSupplierPayment"),
    path('wool_supplier/all/print/<int:pk>/', PrintWoolSupplierAll, name="PrintWoolSupplierAll"),
]