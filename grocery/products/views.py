from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from . models import Product
from . serializers import ProductSerializer
from . permissions import IsManager


# GET all products / CREATE product (Manager only)
@api_view(['GET', 'POST'])
def products_list(request):

    # GET products (public)
    if request.method == 'GET':
        category = request.GET.get("category")
        popular = request.GET.get("popular")

        products = Product.objects.all()

        if category:
            products = products.filter(category__icontains=category)

        if popular == "true":
            products = products.order_by('-popularity')

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    # POST (Managers only)
    if request.method == 'POST':
        if request.user.role != "manager":
            return Response({"error": "Only managers can create products"}, status=403)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# GET single product / UPDATE / DELETE (Manager only)
@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):

    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    # GET product (public — no authentication required)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    # PUT or DELETE — Authentication required
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)

    # Manager only
    if request.user.role != "manager":
        return Response({"error": "Only managers can modify products"}, status=403)


    # UPDATE product
    if request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


    # DELETE product
    if request.method == 'DELETE':
        product.delete()
        return Response({"message": "Product deleted"}, status=204)
