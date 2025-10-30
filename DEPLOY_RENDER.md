# 🚀 Guia de Deploy no Render

Este guia explica como hospedar o Binary Trading Bot no Render gratuitamente.

## 📋 Pré-requisitos

- Conta no GitHub (já tem ✓)
- Conta no Render (gratuita): https://render.com

---

## 🎯 Parte 1: Deploy da API (Backend Python)

### Passo 1: Criar Conta no Render

1. Acesse: https://render.com
2. Clique em **"Get Started"**
3. Faça login com sua conta GitHub

### Passo 2: Conectar Repositório

1. No dashboard do Render, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte ao repositório **`yogrrr/Bi_Trade`**
4. Clique em **"Connect"**

### Passo 3: Configurar o Service

Preencha os campos:

```
Name: binary-trading-bot-api
Region: Oregon (US West)
Branch: main
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.web.api:app --host 0.0.0.0 --port $PORT
Instance Type: Free
```

### Passo 4: Variáveis de Ambiente (Opcional)

Se você quiser usar broker real, adicione:

```
IQOPTION_EMAIL = seu_email@exemplo.com
IQOPTION_PASSWORD = sua_senha
```

⚠️ **Atenção:** Nunca compartilhe suas credenciais!

### Passo 5: Deploy

1. Clique em **"Create Web Service"**
2. Aguarde o build (5-10 minutos)
3. Quando aparecer "Live", sua API está online! 🎉

### Passo 6: Copiar URL da API

Você receberá uma URL tipo:
```
https://binary-trading-bot-api.onrender.com
```

**Guarde essa URL!** Você vai precisar dela para a interface.

---

## 🎨 Parte 2: Deploy da Interface (Frontend)

### Opção A: Via Botão "Publish" (Recomendado)

1. Acesse a interface local: https://3000-ieprctzfnse2hx9pa9iob-66b9b815.manusvm.computer
2. Clique no ícone de menu (☰) no canto superior direito
3. Clique em **"Publish"**
4. Siga as instruções na tela
5. Você receberá uma URL tipo: `https://seu-bot.manus.space`

### Opção B: Deploy Manual no Render

Se preferir hospedar no Render também:

1. No Render, clique em **"New +"** → **"Static Site"**
2. Conecte ao repositório da interface (se separado)
3. Configure:
   ```
   Name: binary-trading-bot-interface
   Build Command: pnpm install && pnpm build
   Publish Directory: dist
   ```
4. Clique em **"Create Static Site"**

---

## 🔗 Parte 3: Conectar Interface à API

### Atualizar URL da API na Interface

Edite o arquivo de configuração da interface para apontar para a API no Render:

```javascript
// Substituir localhost por URL do Render
const API_URL = 'https://binary-trading-bot-api.onrender.com';
```

Ou configure via variável de ambiente:
```
VITE_API_URL=https://binary-trading-bot-api.onrender.com
```

---

## ⚙️ Configurações Importantes

### CORS (Cross-Origin)

A API já está configurada para aceitar requisições de qualquer origem. Se precisar restringir:

```python
# app/web/api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-bot.manus.space"],  # Especificar domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Plano Gratuito do Render

**Limitações:**
- ⏰ Service "dorme" após 15 minutos de inatividade
- 🔄 Demora ~30 segundos para "acordar" na primeira requisição
- 💾 750 horas/mês gratuitas (suficiente para 1 serviço 24/7)
- 🚫 Sem execução contínua de trades (ideal para backtests e testes)

**Para trading 24/7:**
- Upgrade para plano pago ($7/mês)
- Ou use outro serviço (AWS, DigitalOcean, etc.)

---

## 🐛 Troubleshooting

### API não inicia

**Erro:** `ModuleNotFoundError`
- **Solução:** Verifique se `requirements.txt` está correto
- Execute localmente: `pip install -r requirements.txt`

### Interface não conecta à API

**Erro:** `CORS policy` ou `Network Error`
- **Solução:** Verifique se a URL da API está correta
- Confirme que CORS está habilitado na API

### Service fica "dormindo"

**Problema:** Render free tier dorme após inatividade
- **Solução 1:** Upgrade para plano pago
- **Solução 2:** Use um serviço de "ping" (ex: UptimeRobot)
- **Solução 3:** Aceite o delay inicial

### Build falha

**Erro:** `Python version not found`
- **Solução:** Adicione `PYTHON_VERSION=3.11.0` nas variáveis de ambiente

---

## 📊 Monitoramento

### Logs em Tempo Real

No dashboard do Render:
1. Clique no seu service
2. Vá em **"Logs"**
3. Veja logs em tempo real

### Métricas

- **CPU/Memory:** Dashboard → Metrics
- **Requests:** Dashboard → Events
- **Uptime:** Dashboard → Health

---

## 🔐 Segurança

### Variáveis de Ambiente

**NUNCA** commite credenciais no código!

✅ **Correto:**
```yaml
# config.yaml (commitado)
broker:
  type: "iqoption"
  email: ""  # Vazio
  password: ""  # Vazio
```

```bash
# Render Dashboard → Environment Variables
IQOPTION_EMAIL=seu_email@exemplo.com
IQOPTION_PASSWORD=sua_senha
```

❌ **Errado:**
```yaml
# config.yaml (commitado)
broker:
  email: "seu_email@exemplo.com"  # NUNCA FAÇA ISSO!
  password: "sua_senha"  # NUNCA FAÇA ISSO!
```

### HTTPS

O Render fornece HTTPS automaticamente. Sempre use:
```
https://binary-trading-bot-api.onrender.com
```

Nunca:
```
http://binary-trading-bot-api.onrender.com
```

---

## 🎉 Pronto!

Agora você tem:

✅ **API rodando 24/7** no Render
✅ **Interface publicada** e acessível de qualquer lugar
✅ **Logs e monitoramento** em tempo real
✅ **Deploy automático** a cada push no GitHub

### URLs Finais

- **API:** https://binary-trading-bot-api.onrender.com
- **Interface:** https://seu-bot.manus.space (ou Render)
- **Repositório:** https://github.com/yogrrr/Bi_Trade

---

## 🆘 Precisa de Ajuda?

- **Documentação Render:** https://render.com/docs
- **GitHub Issues:** https://github.com/yogrrr/Bi_Trade/issues
- **Render Community:** https://community.render.com

---

## ⚠️ Avisos Finais

1. **Plano gratuito é ideal para testes**, não para trading 24/7
2. **Sempre teste em modo DEMO** antes de usar dinheiro real
3. **Monitore logs regularmente** para detectar problemas
4. **Faça backup** das configurações importantes
5. **Opções binárias são de alto risco** - use com responsabilidade

**Boa sorte com seu bot! 🚀📈**
