from django.contrib import admin

# Register your models here.
from .models import Genre, Platform, Game, Review, Order, OrderItem

admin.site.register(Genre)
admin.site.register(Platform)
admin.site.register(Game)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)