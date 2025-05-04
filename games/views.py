from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Game, Genre, Platform, Review, Order, OrderItem
from .forms import ReviewForm, CheckoutForm
from .serializers import GameSerializer
from users.models import CustomUser


class GameListView(ListView):
    model = Game
    template_name = 'games/list.html'
    context_object_name = 'games'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        sort = self.request.GET.get('sort')
        
        if sort == 'price':
            queryset = queryset.order_by('price')
        elif sort == '-price':
            queryset = queryset.order_by('-price')
        elif sort == 'title':
            queryset = queryset.order_by('title')
        elif sort == '-title':
            queryset = queryset.order_by('-title')
        elif sort == '-release_date':
            queryset = queryset.order_by('-release_date')
            
        return queryset


class GameDetailView(DetailView):
    model = Game
    template_name = 'games/detail.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_form'] = ReviewForm()
        context['reviews'] = self.object.reviews.all().order_by('-created_at')[:5]
        return context


class GameSearchView(ListView):
    model = Game
    template_name = 'games/search.html'
    context_object_name = 'games'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        platform = self.request.GET.get('platform')
        genre = self.request.GET.get('genre')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if platform:
            queryset = queryset.filter(platform__name__icontains=platform)
            
        if genre:
            queryset = queryset.filter(genre__name__icontains=genre)
            
        return queryset.distinct()


class CartView(View):
    template_name = 'games/cart.html'

    def get(self, request):
        cart = request.session.get('cart', {})
        games = Game.objects.filter(id__in=cart.keys())
        
        cart_items = []
        total = 0
        
        for game in games:
            quantity = cart[str(game.id)]
            subtotal = game.price * quantity
            total += subtotal
            cart_items.append({
                'game': game,
                'quantity': quantity,
                'subtotal': subtotal
            })
            
        context = {
            'cart_items': cart_items,
            'total': total
        }
        
        return render(request, self.template_name, context)

    def post(self, request):
        game_id = request.POST.get('game_id')
        action = request.POST.get('action')
        
        cart = request.session.get('cart', {})
        
        if action == 'add':
            cart[game_id] = cart.get(game_id, 0) + 1
        elif action == 'remove':
            if game_id in cart:
                if cart[game_id] > 1:
                    cart[game_id] -= 1
                else:
                    del cart[game_id]
        elif action == 'delete':
            if game_id in cart:
                del cart[game_id]
        
        request.session['cart'] = cart
        return redirect('games:cart')


class CheckoutView(View):
    template_name = 'games/checkout.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            messages.warning(request, "Tu carrito está vacío")
            return redirect('games:list')
            
        games = Game.objects.filter(id__in=cart.keys())
        total = sum(game.price * cart[str(game.id)] for game in games)
        
        initial_data = {
            'shipping_address': request.user.address if hasattr(request.user, 'address') else ''
        }
        form = CheckoutForm(initial=initial_data)
        
        context = {
            'form': form,
            'total': total,
            'cart_items': [
                {
                    'game': game,
                    'quantity': cart[str(game.id)],
                    'subtotal': game.price * cart[str(game.id)]
                } for game in games
            ]
        }
        
        return render(request, self.template_name, context)

    def post(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            messages.warning(request, "Tu carrito está vacío")
            return redirect('games:list')
            
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            # Crear la orden
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'P'
            order.total = sum(
                Game.objects.get(id=game_id).price * quantity 
                for game_id, quantity in cart.items()
            )
            order.save()
            
            # Crear los items de la orden
            for game_id, quantity in cart.items():
                game = Game.objects.get(id=game_id)
                OrderItem.objects.create(
                    order=order,
                    game=game,
                    quantity=quantity,
                    price=game.price
                )
            
            # Limpiar el carrito
            del request.session['cart']
            
            messages.success(request, f"¡Orden #{order.id} creada con éxito!")
            return redirect('games:orders')
            
        messages.error(request, "Por favor corrige los errores en el formulario")
        return self.get(request)


class OrderListView(ListView):
    model = Order
    template_name = 'games/orders.html'
    context_object_name = 'orders'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class GameListAPI(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        platform = self.request.query_params.get('platform')
        genre = self.request.query_params.get('genre')
        search = self.request.query_params.get('search')
        
        if platform:
            queryset = queryset.filter(platform__name__icontains=platform)
        if genre:
            queryset = queryset.filter(genre__name__icontains=genre)
        if search:
            queryset = queryset.filter(title__icontains=search)
            
        return queryset.distinct()


@login_required
def add_review(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.game = game
            review.user = request.user
            review.save()
            
            # Actualizar rating promedio del juego
            reviews = game.reviews.all()
            if reviews.exists():
                game.rating = sum(r.rating for r in reviews) / reviews.count()
                game.save()
            
            messages.success(request, "¡Reseña publicada con éxito!")
        else:
            messages.error(request, "Error al publicar la reseña")
    
    return redirect('games:detail', pk=game_id)


def cart_add(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=401)
        
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart = request.session.get('cart', {})
        cart[game_id] = cart.get(game_id, 0) + quantity
        request.session['cart'] = cart
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values())
        })
        
    return JsonResponse({'error': 'Método no permitido'}, status=405)
    