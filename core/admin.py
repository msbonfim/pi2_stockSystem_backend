# core/admin.py

from django.contrib import admin
from .models import Product, Category, Brand
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
import datetime

# --- WIDGET DE DATA QUE FUNCIONA ---
class PermissiveDateWidget(widgets.DateWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value: return None
        if isinstance(value, datetime.datetime): return value.date()
        if isinstance(value, datetime.date): return value
        if isinstance(value, str) and value.strip() in ('', '-'): return None
        return super().clean(value, row, *args, **kwargs)

# --- WIDGET DE CHAVE ESTRANGEIRA QUE FUNCIONA ---
class CreateOrGetForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value: return None
        try:
            return super().clean(value, row, *args, **kwargs)
        except self.model.DoesNotExist:
            return self.model.objects.create(**{self.field: value})

# --- VERSÃO ESTÁVEL DO ProductResource (SEM A FORMATAÇÃO DE EXPORTAÇÃO) ---
class ProductResource(resources.ModelResource):
    # Definimos apenas os campos que precisam de lógica especial (criar FK)
    category = fields.Field(
        column_name='Categoria',
        attribute='category',
        widget=CreateOrGetForeignKeyWidget(Category, 'name'))
    
    brand = fields.Field(
        column_name='Marca',
        attribute='brand',
        widget=CreateOrGetForeignKeyWidget(Brand, 'name'))

    class Meta:
        model = Product
        # Usamos esta lista para definir os campos e a ordem
        fields = ('id', 'name', 'category', 'brand', 'price', 'description', 'expiration_date', 'quantity', 'batch')
        export_order = fields
        import_id_fields = ('id',)
        skip_unchanged = True

        # Usamos o before_import para mapear as colunas da sua planilha
        def before_import(self, dataset, using_transactions, dry_run, **kwargs):
            header_map = {
                'Nome do Produto': 'name',
                'Preço de Venda (R$)': 'price',
                'Descrição': 'description',
                'Validade': 'expiration_date',
                'Quantidade em Estoque': 'quantity',
                'Lote': 'batch',
            }
            new_headers = []
            for header in dataset.headers:
                new_headers.append(header_map.get(header, header))
            dataset.headers = new_headers

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