from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from . models import Cart, CartItem, Wishlist
from products.models import Product


def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart



# CART: VIEW CART
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    cart = get_user_cart(request.user)
    items = CartItem.objects.filter(cart=cart)

    serializer = [
        {
            "id": item.id,
            "product": item.product.name,
            "quantity": item.quantity,
            "price": float(item.product.price),
            "total": float(item.product.price * item.quantity)
        }
        for item in items
    ]

    return Response(serializer)



# CART: ADD ITEM
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    product_id = request.data.get("product_id")
    quantity = request.data.get("quantity", 1)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    cart = get_user_cart(request.user)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += int(quantity)
    else:
        item.quantity = int(quantity)

    item.save()

    return Response({"message": "Added to cart"})


# CART: REMOVE ITEM
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    item_id = request.data.get("item_id")

    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        item.delete()
        return Response({"message": "Item removed"})
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=404)


# CART: UPDATE QUANTITY
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart(request):
    item_id = request.data.get("item_id")
    quantity = request.data.get("quantity")

    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)

    item.quantity = int(quantity)
    item.save()

    return Response({"message": "Quantity updated"})






# WISHLIST: VIEW
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    serializer = [
        {
            "id": item.id,
            "product": item.product.name
        }
        for item in items
    ]
    return Response(serializer)


# WISHLIST: ADD
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):

    product_id = request.data.get("product_id")

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    Wishlist.objects.get_or_create(user=request.user, product=product)

    return Response({"message": "Added to wishlist"})


# WISHLIST: REMOVE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_wishlist(request):
    product_id = request.data.get("product_id")

    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product_id=product_id)
        wishlist_item.delete()
        return Response({"message": "Removed from wishlist"})
    except Wishlist.DoesNotExist:
        return Response({"error": "Not found in wishlist"}, status=404)

