# 🚀 Deploy do Backend no Render.com

## 📋 Configuração Apenas do Backend

Este guia mostra como fazer o deploy **apenas do backend Django** no Render.com.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Render.com                              │
├─────────────────────────────────────────────────────────────┤
│  Backend (Web Service)                                    │
│  Django + PostgreSQL                                      │
│  https://backend-name.onrender.com                        │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Estrutura do Backend

```
backend/
├── sistema_gestao/
│   ├── settings.py                    # Configurações gerais
│   ├── settings_production.py         # Configurações de produção
│   └── wsgi.py
├── core/
│   ├── models.py
│   ├── views.py
│   └── serializers.py
├── requirements.txt                   # Dependências
├── build.sh                          # Script de build
├── render.yaml                       # Configuração automática
└── DEPLOY_BACKEND_RENDER.md          # Este arquivo
```

## 🔧 Arquivos de Configuração

### **1. `requirements.txt`** ✅
- Todas as dependências necessárias
- Inclui `whitenoise` para arquivos estáticos
- Inclui `gunicorn` para servidor WSGI

### **2. `build.sh`** ✅
- Script de build para o Render
- Instala dependências
- Executa migrações
- Coleta arquivos estáticos

### **3. `settings_production.py`** ✅
- Configurações de produção otimizadas
- Suporte a variáveis de ambiente
- Configuração de banco PostgreSQL
- Configuração de arquivos estáticos

### **4. `render.yaml`** ✅
- Configuração automática do Render
- Define variáveis de ambiente
- Configura banco de dados

## 🚀 Deploy no Render.com

### **Passo 1: Criar Web Service**
1. Acesse [render.com](https://render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub
4. Selecione a pasta `backend`

### **Passo 2: Configurações do Serviço**
- **Name**: `sistema-gestao-backend`
- **Environment**: `Python 3`
- **Root Directory**: `backend`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn sistema_gestao.wsgi:application`
- **Plan**: Free (ou Paid para produção)

### **Passo 3: Variáveis de Ambiente**
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=backend-name.onrender.com
DATABASE_URL=postgresql://... (fornecido automaticamente)
```

### **Passo 4: Banco de Dados**
1. Crie um "PostgreSQL" service
2. Nome: `sistema-gestao-db`
3. O Render fornecerá automaticamente a `DATABASE_URL`

## 🧪 Testar Deploy

### **1. Verificar Logs:**
- Acesse o dashboard do Render
- Verifique os logs de build e runtime
- Procure por erros

### **2. Testar API:**
```bash
# Testar endpoint de produtos
curl https://backend-name.onrender.com/api/products/

# Testar endpoint de estatísticas
curl https://backend-name.onrender.com/api/dashboard/stats/
```

### **3. Verificar Admin:**
- Acesse `https://backend-name.onrender.com/admin/`
- Crie um superusuário se necessário

## 🔐 Configurações de Segurança

### **1. Variáveis de Ambiente:**
- `SECRET_KEY`: Gere uma chave segura
- `DEBUG`: `False` em produção
- `ALLOWED_HOSTS`: Configure com o domínio do Render

### **2. CORS:**
- Configure apenas domínios necessários
- Para desenvolvimento local, mantenha `CORS_ALLOW_ALL_ORIGINS = True`

## 📊 Monitoramento

### **1. Logs:**
- Acesse o dashboard do Render
- Monitore logs em tempo real
- Configure alertas se necessário

### **2. Métricas:**
- CPU e memória
- Requests por minuto
- Tempo de resposta

## 🚨 Troubleshooting

### **Erro de Build:**
- Verifique se todas as dependências estão no `requirements.txt`
- Confirme se o `build.sh` tem permissão de execução
- Verifique os logs de build

### **Erro de Runtime:**
- Verifique as variáveis de ambiente
- Confirme se o banco está conectado
- Verifique os logs do Render

### **Erro de Banco:**
- Confirme se o PostgreSQL está criado
- Verifique se a `DATABASE_URL` está configurada
- Execute as migrações manualmente se necessário

## ✅ Checklist de Deploy

- [ ] Repositório configurado
- [ ] Arquivos de configuração criados
- [ ] Variáveis de ambiente configuradas
- [ ] Banco PostgreSQL criado
- [ ] Build executado com sucesso
- [ ] API respondendo
- [ ] Admin acessível
- [ ] Logs funcionando

## 🎯 URLs Finais

Após o deploy, você terá:
- **Backend**: `https://sistema-gestao-backend.onrender.com`
- **API**: `https://sistema-gestao-backend.onrender.com/api/products/`
- **Admin**: `https://sistema-gestao-backend.onrender.com/admin/`

## 🔄 Próximos Passos

1. **Deploy do Backend** no Render
2. **Testar API endpoints**
3. **Configurar superusuário**
4. **Testar com frontend local**
5. **Configurar domínio personalizado** (opcional)

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no dashboard do Render
2. Confirme se todas as variáveis estão configuradas
3. Teste os endpoints individualmente
4. Verifique se o banco está conectado
5. Confirme se as migrações foram executadas
