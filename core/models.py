# core/models.py
from django.db import models
from django.utils import timezone # Certifique-se que está importado

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Marca")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['name']

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantidade em Estoque")
    expiration_date = models.DateField(verbose_name="Data de Validade", null=True, blank=True)
    
    # --- NOVOS CAMPOS ---
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, # Se uma categoria for deletada, o campo no produto fica nulo.
        null=True, 
        blank=True,
        related_name='products',
        verbose_name="Categoria"
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Marca"
    )
    
    batch = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lote")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['expiration_date']