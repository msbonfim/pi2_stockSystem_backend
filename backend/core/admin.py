# core/admin.py

from django.contrib import admin
# Importe o novo modelo Category
from .models import Product, Category 

# --- REGISTRANDO O MODELO CATEGORY ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Adicione 'category' e 'batch'
    list_display = ('name', 'category', 'price', 'quantity', 'batch', 'expiration_date')
    search_fields = ('name', 'description', 'batch') # Adicione busca por lote
    
    # Adicione filtro por categoria
    list_filter = ('category', 'expiration_date', 'created_at')
    
    ordering = ('expiration_date',)
    list_per_page = 20

    # Melhora a seleção de categoria no formulário do produto
    autocomplete_fields = ['category']