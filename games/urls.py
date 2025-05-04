from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('', views.GameListView.as_view(), name='list'),
    path('<int:pk>/', views.GameDetailView.as_view(), name='detail'),
    path('search/', views.GameSearchView.as_view(), name='search'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('orders/', views.OrderListView.as_view(), name='orders'),
    path('api/games/', views.GameListAPI.as_view(), name='api_games'),
    path('add-review/<int:game_id>/', views.add_review, name='add_review'),
    path('cart/add/', views.cart_add, name='cart_add'),
]