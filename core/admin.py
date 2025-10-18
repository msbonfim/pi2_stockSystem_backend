# core/admin.py

from django.contrib import admin
from .models import Product, Category, Brand
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
import datetime

# --- WIDGETS PERSONALIZADOS (sem alterações) ---

class PermissiveDateWidget(widgets.DateWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value: return None
        if isinstance(value, datetime.datetime): return value.date()
        if isinstance(value, datetime.date): return value
        if isinstance(value, str) and value.strip() in ('', '-'): return None
        return super().clean(value, row, *args, **kwargs)

class CreateOrGetForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value: return None
        try:
            return super().clean(value, row, *args, **kwargs)
        except self.model.DoesNotExist:
            return self.model.objects.create(**{self.field: value})

class BrazilianDecimalWidget(widgets.DecimalWidget):
    def render(self, value, export_context=None):
        if value is None:
            return ""
        # Formata com 2 casas decimais e substitui o ponto pela vírgula.
        return f"{value:.2f}".replace('.', ',')

# --- VERSÃO FINAL E EXPLÍCITA DO ProductResource ---
class ProductResource(resources.ModelResource):
    # Declaramos CADA campo que queremos no Excel, na ordem desejada.
    # Isso nos dá controle total sobre importação e exportação.

    id = fields.Field(attribute='id', column_name='id')
    name = fields.Field(attribute='name', column_name='Nome do Produto')
    category = fields.Field(
        attribute='category',
        column_name='Categoria',
        widget=CreateOrGetForeignKeyWidget(Category, 'name'))
    brand = fields.Field(
        attribute='brand',
        column_name='Marca',
        widget=CreateOrGetForeignKeyWidget(Brand, 'name'))
    price = fields.Field(
        attribute='price', 
        column_name='Preço de Venda (R$)', 
        widget=BrazilianDecimalWidget()) # Nosso widget para vírgula
    description = fields.Field(attribute='description', column_name='Descrição')
    expiration_date = fields.Field(
        attribute='expiration_date',
        column_name='Validade',
        widget=PermissiveDateWidget(format='%d/%m/%Y')) # Nosso widget para data
    quantity = fields.Field(attribute='quantity', column_name='Quantidade em Estoque')
    batch = fields.Field(attribute='batch', column_name='Lote')

    class Meta:
        model = Product
        # REMOVEMOS a tupla 'fields' para evitar conflitos. A ordem agora é
        # definida pela declaração dos campos acima.
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True

# --- O RESTO DO ARQUIVO CONTINUA IGUAL ---
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ProductResource
    list_display = ('id', 'name', 'category', 'brand', 'price', 'quantity', 'expiration_date')
    search_fields = ('name', 'description', 'brand__name')
    list_filter = ('category', 'brand', 'expiration_date')
    ordering = ('-id',)
    list_per_page = 20
    autocomplete_fields = ['category', 'brand']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)