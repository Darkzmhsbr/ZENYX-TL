#!/usr/bin/env python3
"""
BOT ZENYX - Inicializador para bots dos usuários
Este script é responsável por inicializar os bots criados pelos usuários
"""

import logging
import os
import sys
import threading
import time
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Importar handlers específicos para os bots dos usuários
from handlers.user_bot_handlers import (
    handle_start_command,
    handle_text_message,
    handle_media_message,
    handle_config_callback,
    handle_plan_purchase,
    check_payment_status
)

# Importar serviço Redis
from services.redis_service import RedisService

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar serviço Redis
redis_service = RedisService()

class UserBot:
    """Classe para inicializar os bots dos usuários"""
    
    def __init__(self, token):
        self.token = token
        
        if not self.token:
            logger.error("TOKEN não fornecido!")
            raise ValueError("TOKEN não fornecido")
    
    async def error_handler(self, update, context):
        """Handler para erros"""
        logger.error(f"Erro no bot: {context.error}", exc_info=context.error)
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente."
                )
            except Exception:
                pass
    
    def run(self):
        """Iniciar o bot"""
        # Criar a aplicação
        application = Application.builder().token(self.token).build()
        
        # Adicionar handlers
        
        # Handler para comando /start - crucial para exibir o painel admin
        application.add_handler(CommandHandler("start", handle_start_command))
        
        # Handler para mensagens de texto
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
        # Handler para mensagens com mídia - corrigido para usar apenas os filtros disponíveis
        application.add_handler(MessageHandler(
            filters.PHOTO | filters.VIDEO, 
            handle_media_message
        ))
        
        # Handlers para callbacks
        application.add_handler(CallbackQueryHandler(handle_config_callback, pattern=r'^config_'))
        application.add_handler(CallbackQueryHandler(handle_plan_purchase, pattern=r'^buy_plan_'))
        application.add_handler(CallbackQueryHandler(check_payment_status, pattern=r'^check_payment_'))
        
        # Error handler
        application.add_error_handler(self.error_handler)
        
        # Iniciar o bot
        logger.info(f"Bot do usuário iniciado com token: {self.token[:10]}...")
        application.run_polling(drop_pending_updates=True)


def start_user_bot(token):
    """Inicia um bot do usuário com o token fornecido"""
    try:
        bot = UserBot(token)
        bot.run()
    except Exception as e:
        logger.error(f"Erro ao iniciar bot com token {token[:10]}...: {e}")


def start_bot_in_thread(token):
    """Inicia um bot em uma thread separada"""
    thread = threading.Thread(target=start_user_bot, args=(token,))
    thread.daemon = True
    thread.start()
    return thread


async def get_all_bot_tokens():
    """Obtém todos os tokens de bots registrados no Redis"""
    try:
        # Buscar todos os bots registrados
        bots = await redis_service.get_all_bots()
        if not bots:
            return []
        
        # Extrair tokens
        tokens = [bot_data.get('token') for bot_data in bots.values() if bot_data.get('active', True)]
        return tokens
    except Exception as e:
        logger.error(f"Erro ao buscar tokens dos bots: {e}")
        return []


async def start_all_user_bots():
    """Inicia todos os bots dos usuários registrados"""
    tokens = await get_all_bot_tokens()
    if not tokens:
        logger.warning("Nenhum bot registrado encontrado.")
        return
    
    logger.info(f"Iniciando {len(tokens)} bots de usuários...")
    
    # Iniciar cada bot em uma thread separada
    threads = []
    for token in tokens:
        thread = start_bot_in_thread(token)
        threads.append(thread)
        # Pequeno delay para evitar sobrecarga
        time.sleep(0.5)
    
    logger.info(f"{len(threads)} bots de usuários iniciados com sucesso!")


if __name__ == '__main__':
    # Se o script for executado diretamente
    if len(sys.argv) > 1:
        # Se um token foi fornecido como argumento, iniciar apenas esse bot
        token = sys.argv[1]
        start_user_bot(token)
    else:
        # Se nenhum token foi fornecido, iniciar todos os bots registrados
        import asyncio
        asyncio.run(start_all_user_bots())