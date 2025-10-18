# core/admin.py

from django.contrib import admin
from .models import Product, Category, Brand
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

# --- NOVO WIDGET DE DATA PERMISSIVO ---
# Este widget converte valores vazios ou hífens em None (sem data).
# Para outros valores, ele tenta processar como uma data no formato DD/MM/YYYY.
class PermissiveDateWidget(widgets.DateWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value or value.strip() == '-':
            return None  # Retorna None para células vazias ou com hífen
        # Para todos os outros casos, usa a lógica padrão para processar a data
        return super().clean(value, row, *args, **kwargs)

# Widget genérico para criar ou obter chaves estrangeiras
class CreateOrGetForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        try:
            return super().clean(value, row, *args, **kwargs)
        except self.model.DoesNotExist:
            return self.model.objects.create(**{self.field: value})

# --- VERSÃO ATUALIZADA DO ProductResource ---
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
    
    # --- AQUI ESTÁ A MUDANÇA PRINCIPAL ---
    # Usando o novo widget permissivo para a data de validade
    expiration_date = fields.Field(
        attribute='expiration_date',
        column_name='Validade',
        widget=PermissiveDateWidget(format='%d/%m/%Y')) # <-- MUDANÇA AQUI
        
    quantity = fields.Field(attribute='quantity', column_name='Quantidade em Estoque')

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'brand', 'price', 'description', 'expiration_date', 'quantity', 'batch')
        skip_unchanged = True
        report_skipped = True

# --- Registrando o novo modelo BrandAdmin ---
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