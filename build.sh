#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Configurar variável de ambiente para usar settings de produção
export DJANGO_SETTINGS_MODULE=sistema_gestao.settings_production
export RENDER=true

# Executar migrações
python manage.py migrate --no-input

# Coletar arquivos estáticos (limpar antes para evitar conflitos)
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input --clear --verbosity=2

# Verificar se os arquivos foram coletados (debug)
echo "🔍 Verificando arquivos coletados..."
if [ -d "staticfiles/admin/css" ]; then
    echo "✓ Arquivos CSS encontrados:"
    ls -la staticfiles/admin/css/ || true
else
    echo "⚠️ Pasta staticfiles/admin/css não encontrada!"
fi

if [ -d "staticfiles/admin/js" ]; then
    echo "✓ Arquivos JS encontrados:"
    ls -la staticfiles/admin/js/ || true
else
    echo "⚠️ Pasta staticfiles/admin/js não encontrada!"
fi

# Criar superusuário se não existir (opcional)
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
