from Core.models import SystemInformation
from Factories.models import Factory, Supplier
from Invoices.models import *
from django.db.models import F
from Treasury.models import Treasury
from Wool.models import WoolSupplier
from Workers.models import Worker
from Core.models import *


def allcontext(request):
    info = SystemInformation.objects.filter(id=1)
    factorys = Factory.objects.filter(deleted=False)
    treasurys = Treasury.objects.filter(deleted=False)
    products = Product.objects.filter(deleted=False)
    sellers = ProductSellers.objects.filter(deleted=False)
    allsellers = ProductSellers.objects.all()
    workers = Worker.objects.filter(deleted=False)
    suppliers = Supplier.objects.filter(deleted=False)
    wool_suppliers = WoolSupplier.objects.filter(deleted=False)

    invoices_notify = Invoice.objects.filter(saved=False)
    products_notify = Product.objects.filter(price__lt=F('cost'))

    notification_count = invoices_notify.count() + products_notify.count()

    modules = Modules.objects.all().last()
    today = datetime.now().date()
    context = { 
        'info':info,
        'factorys' : factorys,
        'suppliers' : suppliers,
        'wool_suppliers' : wool_suppliers,
        'products':products,
        'sellers':sellers,
        'allsellers':allsellers,
        'workers':workers,
        'treasurys':treasurys,
        'invoices_notify':invoices_notify,
        'products_notify':products_notify,
        'notification_count':notification_count,
        'modules':modules,
        'today':today,
    }
    return context