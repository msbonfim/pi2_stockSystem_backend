# 🚀 Configuração para Deploy no Render.com

## 📋 Arquivos Criados

### **1. `settings_production.py`**
- Configurações de produção otimizadas
- Suporte a variáveis de ambiente
- Configuração de banco PostgreSQL
- Configuração de arquivos estáticos

### **2. `build.sh`**
- Script de build para o Render
- Instala dependências
- Executa migrações
- Coleta arquivos estáticos

### **3. `requirements.txt`**
- Todas as dependências necessárias
- Inclui `whitenoise` para arquivos estáticos
- Inclui `gunicorn` para servidor WSGI

### **4. `render.yaml`**
- Configuração automática do Render
- Define variáveis de ambiente
- Configura banco de dados

## 🔧 Configuração no Render.com

### **1. Criar Novo Web Service:**
1. Acesse [render.com](https://render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub
4. Selecione a pasta `backend`

### **2. Configurações do Serviço:**
- **Name**: `sistema-gestao-backend`
- **Environment**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn sistema_gestao.wsgi:application`
- **Plan**: Free (ou Paid para produção)

### **3. Variáveis de Ambiente:**
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=sistema-gestao-backend.onrender.com
DATABASE_URL=postgresql://... (fornecido automaticamente)
```

### **4. Banco de Dados:**
1. Crie um "PostgreSQL" service
2. Nome: `sistema-gestao-db`
3. O Render fornecerá automaticamente a `DATABASE_URL`

## 📝 Passos para Deploy

### **1. Preparar o Repositório:**
```bash
cd backend
git add .
git commit -m "Configuração para Render.com"
git push origin main
```

### **2. No Render.com:**
1. **Connect Repository**: Selecione seu repositório
2. **Root Directory**: `backend`
3. **Environment**: Python 3
4. **Build Command**: `./build.sh`
5. **Start Command**: `gunicorn sistema_gestao.wsgi:application`

### **3. Configurar Variáveis:**
- `SECRET_KEY`: Gere uma chave segura
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `seu-app.onrender.com`

### **4. Banco de Dados:**
1. Crie um PostgreSQL service
2. Conecte ao web service
3. A `DATABASE_URL` será configurada automaticamente

## 🔄 Atualizar Frontend

### **1. Atualizar API URL:**
```typescript
// frontend/src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://sistema-gestao-backend.onrender.com';
```

### **2. Variável de Ambiente:**
```bash
# frontend/.env
VITE_API_URL=https://sistema-gestao-backend.onrender.com
```

## 🧪 Testar Deploy

### **1. Verificar Logs:**
- Acesse o dashboard do Render
- Verifique os logs de build e runtime
- Procure por erros

### **2. Testar API:**
```bash
curl https://sistema-gestao-backend.onrender.com/api/products/
```

### **3. Verificar Banco:**
- Acesse o admin do Django
- Verifique se as tabelas foram criadas
- Teste criar um produto

## 🚨 Troubleshooting

### **Erro de Build:**
- Verifique se todas as dependências estão no `requirements.txt`
- Confirme se o `build.sh` tem permissão de execução

### **Erro de Runtime:**
- Verifique as variáveis de ambiente
- Confirme se o banco está conectado
- Verifique os logs do Render

### **Erro de CORS:**
- Adicione o domínio do frontend no `CORS_ALLOWED_ORIGINS`
- Configure `ALLOWED_HOSTS` corretamente

## 📊 Monitoramento

### **1. Logs:**
- Acesse o dashboard do Render
- Monitore logs em tempo real
- Configure alertas se necessário

### **2. Métricas:**
- CPU e memória
- Requests por minuto
- Tempo de resposta

## 🔐 Segurança

### **1. Variáveis Sensíveis:**
- Nunca commite `SECRET_KEY` no código
- Use variáveis de ambiente
- Configure `DEBUG=False` em produção

### **2. CORS:**
- Configure apenas domínios necessários
- Remova `CORS_ALLOW_ALL_ORIGINS` em produção

## ✅ Checklist de Deploy

- [ ] Repositório configurado
- [ ] Arquivos de configuração criados
- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados criado
- [ ] Build executado com sucesso
- [ ] API respondendo
- [ ] Frontend configurado para nova URL
- [ ] Testes funcionando

## 🎯 Próximos Passos

1. **Deploy do Backend** no Render
2. **Deploy do Frontend** no Render
3. **Configurar CORS** entre frontend e backend
4. **Testar sistema completo**
5. **Configurar domínio personalizado** (opcional)
