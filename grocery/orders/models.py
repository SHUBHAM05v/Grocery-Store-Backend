from django.db import models
from users.models import User
from products.models import Product

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at purchase time
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    
    DISCOUNT_TYPES = (
        ('percent', 'Percent'),
        ('fixed', 'Fixed Amount'),
    )

    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expiry_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    one_time_use = models.BooleanField(default=False)

    def __str__(self):
        return self.code

class PromoUsage(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    promo = models.ForeignKey(PromoCode, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)