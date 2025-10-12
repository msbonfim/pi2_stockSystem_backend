# core/urls.py

from django.urls import path
from .views import (
    ProductListCreateView, 
    ProductDetailView,
    ExpiringProductsView, 
    ExpiredProductsView,
    CategoryListCreateView,
    dashboard_stats
)

urlpatterns = [
    # Produtos
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/expiring-soon/', ExpiringProductsView.as_view(), name='expiring-products-list'),
    path('products/expired/', ExpiredProductsView.as_view(), name='expired-products-list'),
    
    # Categorias
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    
    # Dashboard
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
]