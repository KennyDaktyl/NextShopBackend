from django.utils import timezone
from django.apps import apps

def generate_order_number():
    now = timezone.now()
    current_month = now.strftime("%m")
    current_year = now.strftime("%Y")
    
    Order = apps.get_model('web', 'Order')
    
    orders_this_month = Order.objects.filter(
        created_date__year=current_year,
        created_date__month=current_month
    ).count() + 1  

    order_number = f"{orders_this_month:05d}-{current_month}-{current_year}"
    
    return order_number
