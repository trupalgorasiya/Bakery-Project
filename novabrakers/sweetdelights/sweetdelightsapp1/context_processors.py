from .models import Cart

def cart_count(request):
    total_cart_items = 0
    if request.session.get('user_id'):
        user_id = request.session.get('user_id')
        cart_items = Cart.objects.filter(user_id=user_id)
        total_cart_items = sum(item.quantity for item in cart_items)

    return {'total_cart_items': total_cart_items}
