# core/views.py

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, date
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

# Imports para o filtro
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# View para listar e criar produtos
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'batch']
    search_fields = ['name', 'description', 'batch']
    ordering_fields = ['name', 'price', 'expiration_date']

# View para detalhes, atualizar e deletar produtos
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# View para listar produtos próximos do vencimento
class ExpiringProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Retorna produtos que irão expirar nos próximos 30 dias
        """
        today = timezone.now().date()
        expiration_limit = today + timedelta(days=30)

        return Product.objects.filter(
            expiration_date__gte=today,
            expiration_date__lte=expiration_limit,
            quantity__gt=0
        ).order_by('expiration_date')

# View para listar produtos vencidos
class ExpiredProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Retorna produtos já vencidos
        """
        today = timezone.now().date()
        return Product.objects.filter(
            expiration_date__lt=today
        ).order_by('expiration_date')

# View para categorias
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Endpoint para estatísticas do dashboard
@api_view(['GET'])
def dashboard_stats(request):
    """
    Retorna estatísticas para o dashboard
    Nova classificação:
    - Vencidos: < 0 dias
    - Críticos: 0-3 dias  
    - Aviso: 4-7 dias
    - Bom: > 7 dias
    """
    today = date.today()
    
    total_products = Product.objects.count()
    expired_products = Product.objects.filter(expiration_date__lt=today).count()
    
    # Críticos: 0-3 dias
    critical_products = Product.objects.filter(
        expiration_date__gte=today,
        expiration_date__lte=today + timedelta(days=3)
    ).count()
    
    # Aviso: 4-7 dias
    expiring_soon = Product.objects.filter(
        expiration_date__gte=today + timedelta(days=4),
        expiration_date__lte=today + timedelta(days=7)
    ).count()
    
    low_stock = Product.objects.filter(quantity__lt=10).count()
    
    # Log para debug
    print(f"📊 Estatísticas calculadas - Data: {today}")
    print(f"Total: {total_products}, Vencidos: {expired_products}, Críticos: {critical_products}, Aviso: {expiring_soon}")
    
    return Response({
        'total_products': total_products,
        'expired_products': expired_products,
        'critical_products': critical_products,
        'expiring_soon': expiring_soon,
        'low_stock': low_stock,
        'good_products': total_products - expired_products - critical_products - expiring_soon
    })