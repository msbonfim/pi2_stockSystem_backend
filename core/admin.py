# core/admin.py

from django.contrib import admin
from .models import Product, Category, Brand
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

# --- VERSÃO CORRIGIDA DO WIDGET DE DATA ---
class PermissiveDateWidget(widgets.DateWidget):
    def clean(self, value, row=None, *args, **kwargs):
        # Primeiro, verifica se o valor está vazio.
        if not value:
            return None
        # Em seguida, verifica se é um texto antes de usar .strip()
        if isinstance(value, str) and value.strip() == '-':
            return None
        # Para todos os outros casos (incluindo quando o valor já é um objeto de data),
        # deixa a lógica padrão da biblioteca fazer o trabalho.
        return super().clean(value, row, *args, **kwargs)

# Widget genérico para criar ou obter chaves estrangeiras (sem alterações)
class CreateOrGetForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        try:
            return super().clean(value, row, *args, **kwargs)
        except self.model.DoesNotExist:
            return self.model.objects.create(**{self.field: value})

# Resource explícito (sem alterações)
class ProductResource(resources.ModelResource):
    name = fields.Field(attribute='name', column_name='Nome do Produto')
    category = fields.Field(
        attribute='category',
        column_name='Categoria',
        widget=CreateOrGetForeignKeyWidget(Category, 'name'))
    brand = fields.Field(
        attribute='brand',
        column_name='Marca',
        widget=CreateOrGetForeignKeyWidget(Brand, 'name'))
    price = fields.Field(attribute='price', column_name='Preço de Venda (R$)')
    description = fields.Field(attribute='description', column_name='Descrição')
    expiration_date = fields.Field(
        attribute='expiration_date',
        column_name='Validade',
        widget=PermissiveDateWidget(format='%d/%m/%Y')) # Continua usando nosso widget corrigido
    quantity = fields.Field(attribute='quantity', column_name='Quantidade em Estoque')

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'brand', 'price', 'description', 'expiration_date', 'quantity', 'batch')
        skip_unchanged = True
        report_skipped = True

# O resto do arquivo admin.py continua igual
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ProductResource
    list_display = ('name', 'category', 'brand', 'price', 'quantity', 'expiration_date')
    search_fields = ('name', 'description', 'brand__name')
    list_filter = ('category', 'brand', 'expiration_date')
    ordering = ('expiration_date',)
    list_per_page = 20
    autocomplete_fields = ['category', 'brand']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)