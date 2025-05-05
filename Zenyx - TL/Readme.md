# BOT ZENYX - Gestor de Bots do Telegram

## Estrutura do Projeto

```
/zenyx-bot
│
├── /config
│   └── config.py              # Configurações gerais e variáveis de ambiente
│
├── /handlers
│   ├── start.py               # Handler para comando /start e menu principal
│   ├── admin.py               # Funções administrativas
│   ├── payment.py             # Integração com PushinPay
│   ├── verify.py              # Verificação de canal
│   ├── referral.py            # Sistema de indicações
│   └── bot_creation.py        # Criação e gerenciamento de bots
│
├── /services
│   ├── payment_service.py     # Serviço de pagamentos PushinPay
│   ├── redis_service.py       # Serviço Redis para persistência
│   └── botfather_service.py   # Integração com BotFather
│
├── /models
│   └── user_model.py          # Modelos de dados
│
├── /utils
│   ├── helpers.py             # Funções auxiliares
│   └── templates.py           # Templates de mensagens
│
├── /tests
│   └── test_handlers.py       # Testes unitários
│
├── main.py                    # Arquivo principal
├── requirements.txt           # Dependências
├── .env.example               # Exemplo de variáveis de ambiente
└── README.md                  # Documentação

```

## Visão Geral

BOT ZENYX é um bot do Telegram que permite aos usuários criar e gerenciar seus próprios bots para administrar grupos/canais VIP com pagamentos integrados via PushinPay.

### Funcionalidades Principais

- ✅ Criação automática de bots a partir de tokens do BotFather
- ✅ Configuração personalizada de mensagens de boas-vindas
- ✅ Integração com PushinPay para pagamentos PIX
- ✅ Gerenciamento de grupos/canais VIP
- ✅ Sistema de indicações com comissões
- ✅ Painel administrativo com métricas
- ✅ Remarketing segmentado

## Requisitos do Sistema

- Python 3.8+
- Redis (ou fallback para armazenamento em arquivo)
- Conta no Telegram Bot API
- Token da API PushinPay

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/zenyx-bot.git
cd zenyx-bot
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

5. Execute o bot:
```bash
python main.py
```

## Configuração

### Variáveis de Ambiente (.env)

```env
# Token do Bot Principal
BOT_TOKEN=seu_token_aqui

# Configurações do Redis
REDIS_URL=redis://localhost:6379/0

# Configurações PushinPay
PUSHINPAY_TOKEN=seu_token_pushinpay

# ID do Canal para Verificação
CHANNEL_ID=@seu_canal

# IDs dos Administradores
ADMIN_IDS=123456789,987654321

# Modo Debug
DEBUG=False
```

## Fluxo de Funcionamento

### 1. Início do Bot

Usuário inicia o bot com `/start`:
- Verifica se usuário está no canal obrigatório
- Exibe menu principal após verificação

### 2. Criação de Bot

Usuário seleciona "🤖 Criar seu Bot":
- Solicita token do BotFather
- Valida e inicializa o bot do usuário
- Redireciona para configuração

### 3. Configuração do Bot

No bot criado, o usuário pode:
- Configurar mensagem de boas-vindas (texto/mídia)
- Integrar PushinPay (token)
- Vincular grupos/canais VIP
- Criar planos de pagamento

### 4. Sistema de Pagamentos

Quando usuário compra acesso:
- Gera QR Code PIX via PushinPay
- Verifica pagamento automaticamente
- Libera acesso ao grupo/canal VIP

### 5. Administrativo

Funções disponíveis para admins:
- Métricas de vendas
- Exportação de contatos
- Remarketing segmentado
- Status do sistema
- Usuários online

## Comandos Disponíveis

### Bot Principal (ZENYX)

- `/start` - Inicia o bot e exibe menu principal
- `/admin` - Acessa painel administrativo (apenas admins)
- `/stats` - Exibe estatísticas básicas
- `/help` - Ajuda e suporte

### Bot do Usuário

- `/start` - Menu de configuração do bot
- `/config` - Configurações avançadas
- `/plans` - Gerenciar planos de pagamento
- `/users` - Lista de usuários

## Sistema de Indicações

- Usuário recebe link único de indicação
- Ganha R$ 125,00 se indicado gerar 3 vendas em 15 dias
- Comissão de 20% sobre vendas diretas
- Vínculo expira após 15 dias

## Estrutura de Dados

### Usuário
```python
{
    "user_id": "123456789",
    "username": "@usuario",
    "bots": ["bot_token1", "bot_token2"],
    "balance": 0.0,
    "referrals": [],
    "created_at": "2024-01-01T00:00:00",
    "is_admin_vip": False
}
```

### Bot Criado
```python
{
    "token": "123456:ABC...",
    "owner_id": "123456789",
    "username": "@bot_do_usuario",
    "config": {
        "welcome_message": "",
        "media_type": None,
        "media_id": None,
        "plans": [],
        "pushinpay_token": "",
        "linked_groups": []
    },
    "created_at": "2024-01-01T00:00:00"
}
```

## Testes Locais

1. Execute os testes:
```bash
python -m pytest tests/
```

2. Teste manual com BotFather:
```bash
# Crie um bot no BotFather
# Use o token no BOT ZENYX
# Verifique se o bot foi criado corretamente
```

## Deploy

### Railway

1. Crie uma conta no Railway
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente
4. Deploy automático a cada push

### Docker

```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Suporte

- Telegram: @SuporteBotZenyx
- Email: suporte@botzenyx.com
- Issues: GitHub Issues

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

Desenvolvido com ❤️ pela equipe Bot Zenyx