#!/usr/bin/env python3
"""
Teste simplificado do Bot Zenyx
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para comando /start"""
    await update.message.reply_text('Bot Zenyx está funcionando!')

def main() -> None:
    """Função principal"""
    # Token do bot
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        logger.error("BOT_TOKEN não configurado no arquivo .env")
        return
    
    # Criar aplicação
    application = Application.builder().token(token).build()
    
    # Adicionar handler
    application.add_handler(CommandHandler("start", start))
    
    # Iniciar bot
    logger.info("Bot iniciado!")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()