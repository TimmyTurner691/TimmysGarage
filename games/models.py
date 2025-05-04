# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)
    manufacturer = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_date = models.DateField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    genre = models.ManyToManyField(Genre)
    platform = models.ManyToManyField(Platform)
    image = models.ImageField(upload_to='game_images/', blank=True)
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        null=True, blank=True
    )
    
    def __str__(self):
        return self.title

class Review(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('game', 'user')

class Order(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('X', 'Cancelled'),
    )
    
    PAYMENT_METHODS = (
        ('CC', 'Credit Card'),
        ('PP', 'PayPal'),
        ('TB', 'Bank Transfer'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHODS)
    payment_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def subtotal(self):
        return self.quantity * self.price