"""
Templates de mensagens do Bot Zenyx
"""

# Mensagens principais do bot
MESSAGES = {
    # Verificação de canal
    'channel_verification': """🔒 *VERIFICAÇÃO NECESSÁRIA*

Para usar todas as funcionalidades do bot, você precisa entrar no nosso canal oficial:

🔗 [Entrar no Canal](https://t.me/+c_MeI3rZn7o1MWY5)

Após entrar, clique no botão abaixo para verificar:""",

    'channel_verification_failed': """❌ Você ainda não entrou no canal. Por favor, entre no canal e tente novamente.""",

    'channel_verified': """✅ *VERIFICAÇÃO CONCLUÍDA*

Obrigado por entrar no nosso canal!

Agora você tem acesso a todas as funcionalidades do bot.""",

    # Menu principal
    'welcome': """🔥 *BOT CRIADOR DE BOTS* 🔥

Este bot permite criar seu próprio bot para gerenciar grupos VIP com sistema de pagamento integrado.

Escolha uma opção abaixo:""",

    # Criação de bot
    'create_bot': """🤖 *CRIAR SEU BOT*

Para criar seu próprio bot, siga os passos abaixo:

1️⃣ Acesse @BotFather no Telegram
2️⃣ Envie /newbot e siga as instruções
3️⃣ Após criar o bot, copie o token que o BotFather enviar
4️⃣ Cole o token aqui neste chat

O token se parece com algo assim:
`123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ`""",

    'invalid_token': """❌ *TOKEN INVÁLIDO*

O token que você enviou não está no formato correto.

Um token válido tem o formato:
`123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ`

Por favor, verifique e envie novamente.""",

    'bot_starting': """🔄 *INICIANDO SEU BOT...*

Seu bot está sendo iniciado. Este processo pode levar alguns segundos.""",

    'bot_created': """✅ *BOT CRIADO COM SUCESSO!*

Seu bot @{bot_username} foi criado e configurado com sucesso!

Clique no botão abaixo para iniciar seu bot:""",

    'bot_started': """✅ *BOT INICIADO COM SUCESSO!*

Seu bot @{bot_username} está online e pronto para uso.

Configure as opções do seu bot enviando o comando /start para ele.""",

    # Saldo e saques
    'balance': """💰 *SEU SALDO*

Saldo atual: R$ {balance:.2f}

💡 Para sacar, você precisa ter no mínimo R$ 30,00 e respeitar o intervalo de 1 dia entre saques.

{withdrawal_message}""",

    'insufficient_balance': """⚠️ Saldo insuficiente. Saldo mínimo: R$ 30,00""",

    'withdrawal_success': """✅ Saque realizado com sucesso! O valor será creditado em sua conta.""",

    'withdrawal_interval': """⚠️ Você precisa aguardar 1 dia desde o último saque.""",

    # Sistema de indicações
    'referral': """👥 *CONVIDE E GANHE*

Se um usuário entrar pelo seu link de indicação, você pode ganhar no mínimo R$ 125,00 em 15 dias, garantido!

*Como monetizamos?*
• Através dos investimentos que fazemos enquanto seu saldo está em nossas mãos
• Através de anúncios que fazemos para assinantes que já compraram algo (você ganha 20% do valor)
• Através de indicação: somos pagos para indicar a PushinPay, e você ganha 60% do lucro sobre isso

*Regras:*
• Você só ganha se o usuário que você convidar vender no mínimo 3 vendas de R$ 9,90 durante 15 dias
• Após 15 dias, você perde o vínculo com o cliente indicado

*Suas estatísticas:*
• Usuários indicados: {referral_count}
• Total ganho com indicações: R$ {referral_earnings:.2f}

Seu link de indicação:
`{referral_link}`""",

    # Admin VIP
    'admin_vip': """👑 *SEJA ADMIN VIP*

*O que você recebe ao assinar?*
• Recebe comissões de todas as fontes de vendas para sempre
• Recebe rendimentos todos os dias
• Comissões sobre o rendimento e compras de seus indicados
• Comissões sobre as vendas através dos anúncios que fazemos

Quanto mais seu indicado for ativo nas vendas, mais você também ganha!

🎁 *SEU PRIMEIRO MÊS É GRÁTIS!*

Você tem esses benefícios somente no primeiro mês de graça.
Depois de 1 mês, seus rendimentos, comissões, etc. serão automaticamente desabilitados.

Preço após o período gratuito: R$ 97,90/mês

Clique abaixo para ativar seu período gratuito!""",

    'admin_vip_activated': """🎉 *PERÍODO GRATUITO ATIVADO!*

Seu período de Admin VIP foi ativado com sucesso!

Você agora tem acesso a todos os benefícios por 30 dias.""",

    # Como funciona
    'how_it_works': """ℹ️ *COMO FUNCIONA*

Nosso sistema permite que você crie facilmente um bot para gerenciar grupos VIP com pagamentos integrados.

💰 *SOBRE PAGAMENTOS:*
• O sistema utiliza PushinPay para processamento de PIX
• Taxa de apenas R$0,30 por transação, independente do valor
• Não cobramos comissão nas suas vendas diretas

🏆 *COMO GANHAMOS:*
• Depois que um usuário compra seu produto, enviamos uma oferta única
• Você recebe 20% de comissão em cada venda gerada
• Você pode sacar suas comissões a cada 15 dias

👑 *VANTAGENS:*
• Sistema totalmente automatizado
• Fácil gerenciamento de assinantes
• Aumente seus lucros com comissões

👥 *PROGRAMA DE INDICAÇÃO:*
• Indique amigos e ganhe R$ 125,00 por cada indicado ativo
• Torne-se Admin VIP e maximize seus lucros com benefícios exclusivos""",

    # Configurações do bot do usuário
    'admin_welcome': """👋🏻 Olá @{username} e bem-vindo ao @{bot_username}!

🔆 Você é o administrador deste bot!""",

    'config_menu': """⚙️ *CONFIGURAR SEU BOT*

Escolha o que deseja configurar:""",

    'config_message': """📝 *CONFIGURAR MENSAGEM*

Escolha o que deseja configurar:""",

    'config_media': """🖼️ *CONFIGURAR MÍDIA*

Envie a mídia que será exibida na mensagem inicial.

Tipos permitidos: fotos e vídeos""",

    'media_saved': """✅ Mídia salva com sucesso!""",

    'config_text': """📝 *CONFIGURAR TEXTO*

Envie o texto que será exibido na mensagem de boas-vindas.

Você pode usar as seguintes variáveis:
• `{firstname}` - Primeiro nome do usuário
• `{username}` - Username do usuário
• `{id}` - ID do usuário""",

    'text_saved': """✅ Texto salvo com sucesso!""",

    'create_plans': """💰 *CRIAR PLANOS*

Envie o nome do plano, valor e duração no formato:

Nome do Plano | Valor | Duração

Exemplo:
Plano Mensal | 49.90 | 30 dias""",

    'plan_created': """✅ Plano criado com sucesso!""",

    'full_preview': """👁️ *VISUALIZAÇÃO COMPLETA*

Aqui está como sua mensagem de boas-vindas ficará:""",

    'advanced_config': """🚀 *CONFIGURAÇÕES AVANÇADAS*

Escolha uma opção:""",

    # PushinPay
    'pushinpay_config': """💰 *CONFIGURAR PUSHINPAY*

Cole aqui seu token gerado na PushinPay.""",

    'pushinpay_configured': """✅ *TOKEN CONFIGURADO!*

Sua integração com PushinPay foi configurada com sucesso.""",

    'pushinpay_invalid': """❌ Token PushinPay inválido. Verifique e tente novamente.""",

    # Canal/Grupo
    'channel_config': """👥 *CONFIGURAR CANAL/GRUPO*

Nenhum grupo ou canal configurado.

Para adicionar um grupo ou canal:

1. Adicione este bot ao grupo/canal como administrador
2. Dê permissões para gerenciar convites, mensagens, etc.
3. Clique no botão abaixo para receber um código
4. Envie o código no grupo/canal para associá-lo""",

    'add_channel': """➕ *ADICIONAR GRUPO/CANAL*

Vou gerar um código único para você vincular seu grupo ou canal.""",

    'code_generated': """🔑 *CÓDIGO GERADO!*

Use o código `{code}` para associar um grupo ou canal a este bot.

*Instruções:*
1. Adicione o bot ao grupo/canal como administrador
2. Envie apenas o código abaixo no grupo/canal
3. O bot irá detectar automaticamente e associar o grupo/canal

`{code}`

Este código expira em 1 hora.""",

    'channel_linked': """✅ Grupo/canal vinculado com sucesso!""",

    'channel_already_linked': """⚠️ Este grupo/canal já está vinculado a outro bot.""",

    # Mensagens de erro
    'error_generic': """❌ Ocorreu um erro. Por favor, tente novamente.""",

    'error_bot_creation': """❌ Erro ao criar o bot. Verifique se o token está correto.""",

    'error_permission': """❌ Você não tem permissão para realizar esta ação.""",

    'error_timeout': """⏰ Tempo esgotado. Por favor, inicie o processo novamente.""",

    # Mensagens administrativas
    'admin_menu': """👨‍💼 *MENU ADMINISTRATIVO*

Escolha uma opção:""",

    'sales_metrics': """📊 *MÉTRICAS DE VENDAS*

Período: {period}
Total de vendas: R$ {total:.2f}
Quantidade de vendas: {count}
Ticket médio: R$ {average:.2f}""",

    'export_contacts': """📋 *EXPORTAR CONTATOS*

Gerando arquivo CSV com todos os contatos...""",

    'remarketing': """📢 *REMARKETING*

Envie a mensagem que deseja enviar para:
• Todos os usuários
• Apenas não pagantes""",

    'system_status': """🔄 *STATUS DO SISTEMA*

Bot Online: ✅
Redis: {redis_status}
PushinPay: {pushinpay_status}
Versão: 1.0.0""",

    'online_users': """📱 *USUÁRIOS ONLINE*

Usuários ativos (últimos 5 min): {active_users}
Total de usuários: {total_users}"""
}

# Mensagens de botões
BUTTONS = {
    'verify': '✅ Verificar',
    'create_bot': '🤖 Criar seu Bot',
    'balance': '💰 Meu saldo',
    'referral': '👥 Convide e ganhe',
    'admin_vip': '👑 Seja Admin VIP',
    'how_it_works': 'ℹ️ Como funciona',
    'back': '🔙 Voltar',
    'cancel': '❌ Cancelar',
    'confirm': '✅ Confirmar',
    'start_bot': '🚀 Iniciar',
    'config_message': '📝 Configurar mensagem',
    'config_pushinpay': '💰 Configurar PushinPay',
    'config_channel': '👥 Configurar canal/grupo',
    'add_channel': '➕ Adicionar grupo/canal',
    'media': '🖼️ Mídia',
    'text': '📝 Texto',
    'create_plans': '💰 Criar planos',
    'full_preview': '👁️ Visualização completa',
    'advanced_config': '🚀 Configurações avançadas',
    'remove_media': '🗑️ Remover mídia atual',
    'activate_vip': '🎁 Ativar Período Gratuito',
    'metrics': '📊 Métricas de Vendas',
    'export': '📋 Exportar Contatos',
    'remarketing': '📢 Remarketing',
    'status': '🔄 Status do Sistema',
    'online': '📱 Usuários Online'
}

# Mensagens de notificação
NOTIFICATIONS = {
    'new_sale': """💰 *NOVA VENDA!*

Plano: {plan_name}
Valor: R$ {amount:.2f}
Usuário: @{username}""",

    'new_referral': """👥 *NOVO INDICADO!*

Usuário: @{username}
Indicado por: @{referrer}""",

    'commission_earned': """💸 *COMISSÃO RECEBIDA!*

Valor: R$ {amount:.2f}
Origem: {source}""",

    'withdrawal_request': """💳 *SOLICITAÇÃO DE SAQUE*

Usuário: @{username}
Valor: R$ {amount:.2f}"""
}

# Mensagens de erro detalhadas
ERROR_MESSAGES = {
    'token_already_used': "❌ Este token já está sendo usado por outro bot.",
    'bot_limit_reached': "❌ Você atingiu o limite máximo de bots permitidos.",
    'invalid_media': "❌ Tipo de mídia não suportado. Use apenas fotos ou vídeos.",
    'invalid_price': "❌ Valor inválido. Use apenas números (ex: 19.90)",
    'payment_failed': "❌ Falha no pagamento. Tente novamente.",
    'database_error': "❌ Erro ao acessar o banco de dados. Tente novamente mais tarde.",
    'network_error': "❌ Erro de conexão. Verifique sua internet e tente novamente."
}