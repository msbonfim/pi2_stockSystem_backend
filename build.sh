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
python manage.py collectstatic --no-input --clear

# Criar superusuário se não existir (opcional)
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
