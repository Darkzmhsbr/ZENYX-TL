"""
Serviço para interação com bots do usuário
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from telegram import Bot
from telegram.error import TelegramError, InvalidToken
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from utils.helpers import log_error

logger = logging.getLogger(__name__)

class BotFatherService:
    """Serviço para iniciar e gerenciar bots dos usuários"""
    
    def __init__(self):
        self.running_bots = {}
        self.applications = {}
    
    async def start_bot(self, token: str) -> Optional[Dict[str, Any]]:
        """Inicia um bot com o token fornecido"""
        try:
            # Verificar se o bot já está rodando
            if token in self.running_bots:
                return self.running_bots[token]
            
            # Criar instância do bot
            bot = Bot(token=token)
            
            # Obter informações do bot
            bot_info = await bot.get_me()
            
            # Criar application
            application = Application.builder().token(token).build()
            
            # Adicionar handlers
            from handlers.bot_creation import handle_bot_configuration, handle_config_callback
            application.add_handler(CommandHandler("start", handle_bot_configuration))
            application.add_handler(CallbackQueryHandler(handle_config_callback))
            
            # Adicionar handlers para mensagens e mídia
            from handlers.user_bot_handlers import (
                handle_text_message,
                handle_media_message,
                handle_pushinpay_token,
                handle_plan_creation
            )
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
            application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media_message))
            
            # Iniciar bot em thread separada
            self.applications[token] = application
            asyncio.create_task(application.run_polling(drop_pending_updates=True))
            
            # Salvar informações do bot
            bot_data = {
                'token': token,
                'username': bot_info.username,
                'first_name': bot_info.first_name,
                'id': bot_info.id,
                'active': True
            }
            
            self.running_bots[token] = bot_data
            
            logger.info(f"Bot started successfully: @{bot_info.username}")
            return bot_data
            
        except InvalidToken:
            logger.error(f"Invalid token: {token[:10]}...")
            return None
        except TelegramError as e:
            log_error(e, {'method': 'start_bot', 'token': token[:10] + '...'})
            return None
        except Exception as e:
            log_error(e, {'method': 'start_bot'})
            return None
    
    async def stop_bot(self, token: str) -> bool:
        """Para um bot em execução"""
        try:
            if token not in self.running_bots:
                return False
            
            # Parar application
            if token in self.applications:
                application = self.applications[token]
                await application.stop()
                await application.shutdown()
                del self.applications[token]
            
            # Remover das listas
            del self.running_bots[token]
            
            logger.info(f"Bot stopped: {token[:10]}...")
            return True
            
        except Exception as e:
            log_error(e, {'method': 'stop_bot', 'token': token[:10] + '...'})
            return False
    
    async def restart_bot(self, token: str) -> Optional[Dict[str, Any]]:
        """Reinicia um bot"""
        try:
            # Parar se estiver rodando
            if token in self.running_bots:
                await self.stop_bot(token)
            
            # Iniciar novamente
            return await self.start_bot(token)
            
        except Exception as e:
            log_error(e, {'method': 'restart_bot'})
            return None
    
    def get_running_bots(self) -> Dict[str, Dict[str, Any]]:
        """Retorna lista de bots em execução"""
        return self.running_bots.copy()
    
    def is_bot_running(self, token: str) -> bool:
        """Verifica se um bot está rodando"""
        return token in self.running_bots
    
    async def send_message_to_bot(self, token: str, chat_id: int, text: str, **kwargs) -> bool:
        """Envia mensagem através de um bot específico"""
        try:
            if token not in self.running_bots:
                return False
            
            bot = Bot(token=token)
            await bot.send_message(chat_id=chat_id, text=text, **kwargs)
            return True
            
        except Exception as e:
            log_error(e, {'method': 'send_message_to_bot'})
            return False
    
    async def get_bot_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um bot"""
        try:
            bot = Bot(token=token)
            info = await bot.get_me()
            
            return {
                'id': info.id,
                'username': info.username,
                'first_name': info.first_name,
                'can_join_groups': info.can_join_groups,
                'can_read_all_group_messages': info.can_read_all_group_messages,
                'supports_inline_queries': info.supports_inline_queries
            }
            
        except Exception as e:
            log_error(e, {'method': 'get_bot_info'})
            return None
    
    async def validate_token(self, token: str) -> bool:
        """Valida se um token é válido"""
        try:
            bot = Bot(token=token)
            await bot.get_me()
            return True
        except:
            return False
    
    async def stop_all_bots(self) -> None:
        """Para todos os bots em execução"""
        try:
            tokens = list(self.running_bots.keys())
            for token in tokens:
                await self.stop_bot(token)
            
            logger.info("All bots stopped successfully")
            
        except Exception as e:
            log_error(e, {'method': 'stop_all_bots'})
    
    async def get_bot_stats(self, token: str) -> Optional[Dict[str, Any]]:
        """Obtém estatísticas de um bot"""
        try:
            if token not in self.running_bots:
                return None
            
            bot_data = self.running_bots[token]
            
            # Aqui você pode adicionar mais estatísticas
            stats = {
                'username': bot_data['username'],
                'active': bot_data['active'],
                'uptime': 'N/A',  # Implementar cálculo de uptime
                'total_users': 0,  # Implementar contagem de usuários
                'total_messages': 0  # Implementar contagem de mensagens
            }
            
            return stats
            
        except Exception as e:
            log_error(e, {'method': 'get_bot_stats'})
            return None