from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from cart.models import Cart, CartItem
from products.models import Product
from . models import Order, OrderItem, PromoCode, PromoUsage
from django.utils import timezone


# CHECKOUT with Promo Code Support
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user

    # OPTIONAL PROMO CODE
    promo_code_input = request.data.get("promo_code")

    # Get cart
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({"error": "Cart is empty"}, status=400)

    items = CartItem.objects.filter(cart=cart)
    if not items.exists():
        return Response({"error": "No items in cart"}, status=400)

    # Create order (final total will be updated later)
    order = Order.objects.create(user=user, total_price=0)
    total_price = 0
    order_items_detail = []

    # Loop through cart items
    for item in items:
        product = item.product

        # Stock Check
        if product.stock < item.quantity:
            return Response(
                {"error": f"Not enough stock for {product.name}"},
                status=400
            )

        # Create OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            price=product.price,
            quantity=item.quantity
        )

        # Reduce stock + increase popularity
        product.stock -= item.quantity
        product.popularity += item.quantity
        product.save()

        # Bill total
        total_price += float(product.price * item.quantity)

        # Add item details
        order_items_detail.append({
            "product": product.name,
            "price": float(product.price),
            "quantity": item.quantity,
            "total": float(product.price * item.quantity)
        })

    # APPLY PROMO CODE
    discount_applied = 0

    if promo_code_input:  # If user entered a promo code
        try:
            promo = PromoCode.objects.get(code__iexact=promo_code_input, active=True)
        except PromoCode.DoesNotExist:
            return Response({"error": "Invalid promo code"}, status=400)

        # Expiry Check
        if promo.expiry_date < timezone.now():
            return Response({"error": "Promo code expired"}, status=400)

        # Minimum order amount check
        if total_price < float(promo.min_order_amount):
            return Response(
                {"error": f"Minimum order should be {promo.min_order_amount}"},
                status=400
            )

        # One-time use check
        if promo.one_time_use:
            if PromoUsage.objects.filter(user=user, promo=promo).exists():
                return Response({"error": "Promo already used"}, status=400)

        # Discount Calculation
        if promo.discount_type == "percent":
            discount_applied = total_price * float(promo.discount_value) / 100
        else:
            discount_applied = float(promo.discount_value)

        # Discount cannot exceed total
        discount_applied = min(discount_applied, total_price)

        # Save promo usage (only if one-time-use)
        if promo.one_time_use:
            PromoUsage.objects.create(user=user, promo=promo)

    # Final total
    final_total = total_price - discount_applied

    # Update order amount
    order.total_price = final_total
    order.save()

    # Clear cart
    items.delete()

    # Return final bill
    return Response({
        "message": "Checkout successful",
        "order_id": order.id,
        "total_price": final_total,
        "discount_applied": discount_applied,
        "items": order_items_detail
    }, status=201)



# ORDER HISTORY (All orders)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    data = []

    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        items_data = [
            {
                "product": item.product.name,
                "quantity": item.quantity,
                "price": float(item.price),
                "total": float(item.price * item.quantity)
            }
            for item in order_items
        ]

        data.append({
            "order_id": order.id,
            "total_price": float(order.total_price),
            "created_at": order.created_at,
            "items": items_data
        })

    return Response(data)



# MANAGER check
def is_manager(user):
    return user.is_authenticated and user.role == "manager"


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_promo(request):

    if not is_manager(request.user):
        return Response({"error": "Only managers can create promo codes"}, status=403)

    data = request.data

    required_fields = ["code", "discount_type", "discount_value", "expiry_date"]
    for field in required_fields:
        if field not in data:
            return Response({"error": f"{field} is required"}, status=400)

    promo = PromoCode.objects.create(
        code=data["code"],
        discount_type=data["discount_type"],
        discount_value=data["discount_value"],
        min_order_amount=data.get("min_order_amount", 0),
        expiry_date=data["expiry_date"],
        active=data.get("active", True),
        one_time_use=data.get("one_time_use", False)
    )

    return Response({"message": "Promo code created", "code": promo.code}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_promos(request):

    if not is_manager(request.user):
        return Response({"error": "Only managers can view promo codes"}, status=403)

    promos = PromoCode.objects.all().order_by('-id')

    data = [
        {
            "id": p.id,
            "code": p.code,
            "discount_type": p.discount_type,
            "discount_value": float(p.discount_value),
            "min_order_amount": float(p.min_order_amount),
            "expiry_date": p.expiry_date,
            "active": p.active,
            "one_time_use": p.one_time_use
        }
        for p in promos
    ]

    return Response(data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_promo(request, id):

    if not is_manager(request.user):
        return Response({"error": "Only managers can update promo codes"}, status=403)

    try:
        promo = PromoCode.objects.get(id=id)
    except PromoCode.DoesNotExist:
        return Response({"error": "Promo code not found"}, status=404)

    data = request.data

    promo.code = data.get("code", promo.code)
    promo.discount_type = data.get("discount_type", promo.discount_type)
    promo.discount_value = data.get("discount_value", promo.discount_value)
    promo.min_order_amount = data.get("min_order_amount", promo.min_order_amount)
    promo.expiry_date = data.get("expiry_date", promo.expiry_date)
    promo.active = data.get("active", promo.active)
    promo.one_time_use = data.get("one_time_use", promo.one_time_use)

    promo.save()

    return Response({"message": "Promo updated successfully"})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_promo(request, id):

    if not is_manager(request.user):
        return Response({"error": "Only managers can delete promo codes"}, status=403)

    try:
        promo = PromoCode.objects.get(id=id)
    except PromoCode.DoesNotExist:
        return Response({"error": "Promo code not found"}, status=404)

    promo.delete()
    return Response({"message": "Promo deleted"})

