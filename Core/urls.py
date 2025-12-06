from django.urls import path 
from . import views

app_name = 'Core'
urlpatterns = [
    path('', views.Index, name='index'),
    path('systemInfoCreate/', views.SystemInfoCreate.as_view(), name='SystemInfoCreate'),
    path('systemInfoUpdate/<int:pk>/', views.SystemInfoUpdate.as_view(), name='SystemInfoUpdate'),
    path('factory_search/', views.FactorySearch.as_view(), name='FactorySearch'),
    path('product_search/', views.ProductSearch.as_view(), name='ProductSearch'),
    path('seller_search/', views.SellerSearch.as_view(), name='SellerSearch'),
    path('worker_search/', views.WorkerSearch.as_view(), name='WorkerSearch'),
    path('invoice_search/', views.InvoiceSearch.as_view(), name='InvoiceSearch'),
    path('treasury_search/', views.TreasurySearch.as_view(), name='TreasurySearch'),
    path('sp_invoice_search/<int:type>/', views.SpInvoiceSearch.as_view(), name='SpInvoiceSearch'),
    path('sp_supplier_search/<int:type>/', views.SpSupplierSearch.as_view(), name='SpSupplierSearch'),
    path('seller_invoice_search/<int:type>/', views.SellerInvoiceSearch.as_view(), name='SellerInvoiceSearch'),
    path('client_invoice_search/<int:type>/', views.ClientInvoiceSearch.as_view(), name='ClientInvoiceSearch'),
    path('wool_supplier_search/', views.WoolSupplierSearch.as_view(), name='WoolSupplierSearch'),
    path('system_statistics/', views.SystemStatistics, name='system_statistics'),

    path('manual_backup/', views.manual_backup_to_drive, name='manual_backup'),
]
