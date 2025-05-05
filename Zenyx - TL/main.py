#!/usr/bin/env python3
"""
BOT ZENYX - Bot Principal
Gerenciador de bots para pagamentos e grupos VIP no Telegram
"""

import logging
import os
import sys
from typing import Optional
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Importar handlers
from handlers.start import start_handler, verify_channel_handler
from handlers.bot_creation import handle_token_input, create_bot_handler
from handlers.payment import balance_handler, referral_handler, admin_vip_handler, how_it_works_handler
from handlers.admin import admin_menu_handler, admin_callback_handler
from utils.helpers import is_user_in_channel, get_user_balance
from utils.templates import MESSAGES

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

class BotZenyx:
    """Classe principal do Bot Zenyx"""
    
    def __init__(self):
        self.token: str = os.getenv('BOT_TOKEN', '')
        self.channel_id: str = os.getenv('CHANNEL_ID', '')
        self.admin_ids: list[int] = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
        self.debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
        
        if not self.token:
            logger.error("BOT_TOKEN não configurado!")
            sys.exit(1)
            
        if not self.channel_id:
            logger.error("CHANNEL_ID não configurado!")
            sys.exit(1)
            
        if not self.admin_ids:
            logger.warning("ADMIN_IDS não configurado - funções admin desabilitadas")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler para comando /start"""
        user_id = update.effective_user.id
        
        # Verificar se usuário está no canal
        is_in_channel = await is_user_in_channel(context.bot, self.channel_id, user_id)
        
        if not is_in_channel:
            # Mostrar mensagem de verificação necessária
            keyboard = [[InlineKeyboardButton("✅ Verificar", callback_data="verify_channel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                MESSAGES['channel_verification'],
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            # Mostrar menu principal
            await start_handler(update, context)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler para callbacks dos botões"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # Rotas de callback
        if data == "verify_channel":
            await verify_channel_handler(update, context)
        elif data == "create_bot":
            await create_bot_handler(update, context)
        elif data == "balance":
            await balance_handler(update, context)
        elif data == "referral":
            await referral_handler(update, context)
        elif data == "admin_vip":
            await admin_vip_handler(update, context)
        elif data == "how_it_works":
            await how_it_works_handler(update, context)
        elif data.startswith("admin_"):
            # Callbacks administrativos
            if update.effective_user.id in self.admin_ids:
                await admin_callback_handler(update, context)
            else:
                await query.edit_message_text("❌ Acesso negado.")
        else:
            await query.edit_message_text("❌ Comando não reconhecido.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler para mensagens de texto (tokens de bot)"""
        message_text = update.message.text
        
        # Verificar se é um token de bot (formato: 123456789:ABC...)
        if ':' in message_text and len(message_text.split(':')) == 2:
            # Possível token do BotFather
            await handle_token_input(update, context)
        else:
            # Mensagem não reconhecida
            await update.message.reply_text(
                "❌ Comando não reconhecido.\n\n"
                "Use /start para ver as opções disponíveis."
            )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler para comando /admin"""
        user_id = update.effective_user.id
        
        if user_id in self.admin_ids:
            await admin_menu_handler(update, context)
        else:
            await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
    
    async def error_handler(self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler para erros"""
        logger.error(f"Erro no bot: {context.error}", exc_info=context.error)
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente."
                )
            except Exception:
                pass
    
    def run(self) -> None:
        """Iniciar o bot"""
        # Criar a aplicação
        application = Application.builder().token(self.token).build()
        
        # Adicionar handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("admin", self.admin_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Error handler
        application.add_error_handler(self.error_handler)
        
        # Iniciar o bot
        logger.info("Bot Zenyx iniciado!")
        application.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    bot = BotZenyx()
    bot.run()