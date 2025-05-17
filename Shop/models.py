from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Product(models.Model):
    image = models.ImageField(upload_to='Shop/media/uploads')
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return self.title
    


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart of {self.user.username}' 
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.quantity * self.product.price
    
    def __str__(self):
        return f'{self.product.title}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Complete', 'Complete'),
        ('Cancel', 'Cancel'),
    ]

    PAYMENT_CHOICES = [
        ('Cash On Delivery', 'Cash On Delivery'),
        ('Online Payment', 'Online Payment')
    ]   
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    billing_address = models.CharField(max_length=255, default="Dhaka")
    name = models.CharField(max_length=100, default="Unknown")
    email = models.EmailField(default="@gmail.com")
    phone = models.CharField(max_length=15, default="+8801")
    note = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default="0")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='Cash On Delivery')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.user}"
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)
  
    def get_total_price(self):
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        # Set the price to the product price if not manually set
        if not self.price:
            self.price = self.product.price
        self.total_price = self.get_total_price()  # Ensure total price is updated
        super(OrderItem, self).save(*args, **kwargs)
   
    def __str__(self):
        return f"{self.product.title}"
    