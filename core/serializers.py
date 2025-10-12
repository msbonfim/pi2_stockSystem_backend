# core/serializers.py

from rest_framework import serializers
from .models import Product, Category # Importe Category

# --- NOVO SERIALIZER PARA CATEGORY ---
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    # Exibe o nome da categoria em vez de apenas o ID.
    # read_only=True significa que este campo é apenas para leitura na API de produto.
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)

    class Meta:
        model = Product
        # Adicionamos os novos campos à lista
        fields = [
            'id', 
            'name', 
            'description', 
            'price', 
            'quantity', 
            'expiration_date',
            'batch',
            'category', # ID da categoria, usado para criar/atualizar
            'category_name', # Nome da categoria, para exibição
            'created_at',
            'updated_at'
        ]