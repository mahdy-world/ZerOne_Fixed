from django.urls import path 
from . import views

app_name = 'Core'
urlpatterns = [
    path('', views.Index, name='index'),
    path('systemInfoCreate/', views.SystemInfoCreate.as_view(), name='SystemInfoCreate'),
    path('ColorCreate/', views.ColorCreate.as_view(), name='ColorCreate'),
    path('ColorUpdate/<int:pk>/', views.ColorUpdate.as_view(), name='ColorUpdate'),
    path('ColorDelete/<int:pk>/', views.ColorDelete.as_view(), name='ColorDelete'),
    path('ColorList/', views.ColorList.as_view(), name='ColorList'),
    path('ExpensessTypeList/', views.ExpensessTypeList.as_view(), name='ExpensessTypeList'),
    path('ExpensessTypeCreate/', views.ExpensessTypeCreate.as_view(), name='ExpensessTypeCreate'),
    path('ExpensessTypeDelete/<int:pk>/', views.ExpensessTypeDelete.as_view(), name='ExpensessTypeDelete'),
    path('systemInfoUpdate/<int:pk>/', views.SystemInfoUpdate.as_view(), name='SystemInfoUpdate'),
    path('factory_search/', views.FactorySearch.as_view(), name='FactorySearch'),
    path('product_search/', views.ProductSearch.as_view(), name='ProductSearch'),
    path('ProductSearch_size/', views.ProductSearch_size.as_view(), name='ProductSearch_size'),
    path('seller_search/', views.SellerSearch.as_view(), name='SellerSearch'),
    path('worker_search/', views.WorkerSearch.as_view(), name='WorkerSearch'),
    path('invoice_search/', views.InvoiceSearch.as_view(), name='InvoiceSearch'),
    path('treasury_search/', views.TreasurySearch.as_view(), name='TreasurySearch'),
    path('sp_invoice_search/<int:type>/', views.SpInvoiceSearch.as_view(), name='SpInvoiceSearch'),
    path('sp_supplier_search/<int:type>/', views.SpSupplierSearch.as_view(), name='SpSupplierSearch'),
    path('seller_invoice_search/<int:type>/', views.SellerInvoiceSearch.as_view(), name='SellerInvoiceSearch'),
    path('client_invoice_search/<int:type>/', views.ClientInvoiceSearch.as_view(), name='ClientInvoiceSearch'),
    path('wool_supplier_search/', views.WoolSupplierSearch.as_view(), name='WoolSupplierSearch'),
    path('wool_search/', views.WoolSearch.as_view(), name='WoolSearch'),
    path('system_statistics/', views.SystemStatistics, name='system_statistics'),
    path('ExpensessDetail/', views.ExpensessDetail, name='ExpensessDetail'),
    path('ExpensessCreate/', views.ExpensessCreate, name='ExpensessCreate'),
    path('ExpensessDelete/<int:pk>/', views.ExpensessDelete.as_view(), name='ExpensessDelete'),
]
