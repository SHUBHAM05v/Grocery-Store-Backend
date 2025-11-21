from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from products.models import Product


# Manager only
def manager_required(user):
    return user.is_authenticated and user.role == "manager"


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_report(request):

    # Check if user is manager
    if not manager_required(request.user):
        return Response({"error": "Only managers can view sales reports"}, status=403)

    sort = request.GET.get("sort")
    category = request.GET.get("category")

    products = Product.objects.all()

    # Filter by category
    if category:
        products = products.filter(category__icontains=category)

    # Sorting logic
    if sort == "most_sold":
        products = products.order_by('-popularity')
    elif sort == "least_sold":
        products = products.order_by('popularity')

    data = [
        {
            "product": p.name,
            "category": p.category,
            "price": float(p.price),
            "stock_left": p.stock,
            "times_sold": p.popularity
        }
        for p in products
    ]

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def low_stock_products(request):

    # Manager-only access
    if request.user.role != "manager":
        return Response({"error": "Only managers can view low-stock items"}, status=403)

    threshold = 50  # fixed alert level
    products = Product.objects.filter(stock__lt=threshold)

    data = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "stock": p.stock,
            "threshold": threshold,
            "alert": "Low stock! Please restock."
        }
        for p in products
    ]

    return Response(data)

