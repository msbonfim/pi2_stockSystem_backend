"""
URL configuration for sistema_gestao project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# meuprojeto/urls.py

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.http import JsonResponse
# --- INÍCIO DO CÓDIGO TEMPORÁRIO ---
def resetar_senha_admin(request):
    # Busca o usuário 'admin'. Se ele não existir (banco resetado), cria um novo.
    user, created = User.objects.get_or_create(username='admin')
    
    # Define a nova senha (troque pela senha que você quer usar)
    user.set_password('SuaNovaSenha123!') 
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    if created:
        return HttpResponse("Superusuário 'admin' CRIADO. Por favor, apague este código do GitHub agora!")
    else:
        return HttpResponse("Senha do 'admin' ALTERADA com sucesso. Por favor, apague este código do GitHub agora!")
# --- FIM DO CÓDIGO TEMPORÁRIO ---
def home(request):
    return JsonResponse({
        'message': 'Sistema de Gestão de Estoque - API Backend',
        'version': '1.0.0',
        'endpoints': {
            'products': '/api/products/',
            'categories': '/api/categories/',
            'dashboard': '/api/dashboard/stats/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    # Adicione esta linha com uma URL difícil de adivinhar
    path('rota-secreta-recuperar-senha/', resetar_senha_admin),
]

# Servir arquivos estáticos e de mídia em ambiente de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
