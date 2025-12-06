from django.urls import path 
from .views import *

app_name = 'Invoices'
urlpatterns = [
    path('InvoiceList/<int:type>/', InvoiceList.as_view(), name="InvoiceList"),
    path('InvoiceTrashList/<int:type>/', InvoiceTrashList.as_view(), name="InvoiceTrashList"),
    path('InvoiceCreate/<int:type>/', InvoiceCreate.as_view(), name="InvoiceCreate"),
    path('InvoiceUpdate/<int:pk>/', InvoiceUpdate.as_view(), name="InvoiceUpdate"),
    path('InvoiceSave/<int:pk>/', InvoiceSave.as_view(), name="InvoiceSave"),
    path('InvoiceClose/<int:pk>/', InvoiceClose.as_view(), name="InvoiceClose"),
    path('InvoiceBack/<int:pk>/', InvoiceBack.as_view(), name="InvoiceBack"),
    path('InvoiceRestore/<int:pk>/', InvoiceRestore.as_view(), name="InvoiceRestore"),
    path('InvoiceSuperDelete/<int:pk>/', InvoiceSuperDelete.as_view(), name="InvoiceSuperDelete"),
    path('InvoiceDelete/<int:pk>/', InvoiceDelete.as_view(), name="InvoiceDelete"),
    path('AllInvoiceDelete/', AllInvoiceDelete, name="AllInvoiceDelete"),
    path('InvoiceDetail/<int:pk>/', InvoiceDetail, name="InvoiceDetail"),
    path('AddProductInvoice/<int:pk>/', AddProductInvoice, name='AddProductInvoice'),
    path('get_item_price/', get_item_price, name='get_item_price'),
    path('InvoiceProductsUpdate/<int:pk>/<int:id>/', InvoiceProductsUpdate.as_view(), name='InvoiceProductsUpdate'),
    path('InvoiceProductsDelete/<int:pk>/<int:id>/', InvoiceProductsDelete.as_view(), name='InvoiceProductsDelete'),
    path('PrintInvoice/<int:id>/', PrintInvoice, name='PrintInvoice'),
    # path('InvoiceReturn/', InvoiceReturn, name='InvoiceReturn'),
    # path('InvoiceReturnProduct/', InvoiceReturnProduct, name='InvoiceReturnProduct'),
    # path('get_item_return_price/', get_item_return_price, name='get_item_return_price'),
    # path('ReturnProductInvoice/<int:pk>/', ReturnProductInvoice, name='ReturnProductInvoice'),
]