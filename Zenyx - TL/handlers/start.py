"""
Handler para comando /start e verificação de canal
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config.config import Config
from utils.helpers import (
    is_user_in_channel,
    create_main_menu_keyboard,
    parse_referral_start,
    log_user_action,
    log_error
)
from utils.templates import MESSAGES, BUTTONS
from services.redis_service import RedisService

logger = logging.getLogger(__name__)
redis_service = RedisService()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para comando /start"""
    try:
        user = update.effective_user
        user_id = user.id
        username = user.username
        
        # Verificar se é comando com referência
        if update.message and update.message.text:
            referrer_id = parse_referral_start(update.message.text)
            if referrer_id:
                # Processar referência
                await process_referral(user_id, referrer_id, username)
        
        # Registrar usuário no Redis
        user_data = {
            'id': user_id,
            'username': username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'created_at': update.message.date.isoformat() if update.message else None,
            'bots': [],
            'balance': 0.0,
            'referrals': [],
            'is_admin_vip': False
        }
        
        # Salvar ou atualizar dados do usuário
        existing_data = await redis_service.get_user_data(user_id)
        if existing_data:
            # Preservar dados existentes
            user_data['bots'] = existing_data.get('bots', [])
            user_data['balance'] = existing_data.get('balance', 0.0)
            user_data['referrals'] = existing_data.get('referrals', [])
            user_data['is_admin_vip'] = existing_data.get('is_admin_vip', False)
            user_data['created_at'] = existing_data.get('created_at', user_data['created_at'])
        
        await redis_service.save_user_data(user_id, user_data)
        
        # Verificar se usuário está no canal
        is_in_channel = await is_user_in_channel(context.bot, Config.CHANNEL_ID, user_id)
        
        if not is_in_channel:
            # Mostrar mensagem de verificação
            keyboard = [[InlineKeyboardButton(BUTTONS['verify'], callback_data="verify_channel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                MESSAGES['channel_verification'],
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        else:
            # Mostrar menu principal
            reply_markup = create_main_menu_keyboard()
            await update.message.reply_text(
                MESSAGES['welcome'],
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        log_user_action(user_id, 'start_command', {'username': username})
        
    except Exception as e:
        log_error(e, {'handler': 'start_handler', 'user_id': user_id if 'user_id' in locals() else None})
        await update.message.reply_text(MESSAGES['error_generic'])

async def verify_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para verificação de canal"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        
        # Verificar se usuário está no canal
        is_in_channel = await is_user_in_channel(context.bot, Config.CHANNEL_ID, user_id)
        
        if is_in_channel:
            # Usuário está no canal - mostrar menu principal
            reply_markup = create_main_menu_keyboard()
            await query.edit_message_text(
                MESSAGES['channel_verified'] + "\n\n" + MESSAGES['welcome'],
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            log_user_action(user_id, 'channel_verified')
        else:
            # Usuário ainda não está no canal
            keyboard = [[InlineKeyboardButton(BUTTONS['verify'], callback_data="verify_channel")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                MESSAGES['channel_verification_failed'] + "\n\n" + MESSAGES['channel_verification'],
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            log_user_action(user_id, 'channel_verification_failed')
            
    except TelegramError as e:
        log_error(e, {'handler': 'verify_channel_handler', 'user_id': user_id if 'user_id' in locals() else None})
        await query.edit_message_text(MESSAGES['error_generic'])
    except Exception as e:
        log_error(e, {'handler': 'verify_channel_handler', 'user_id': user_id if 'user_id' in locals() else None})
        await query.edit_message_text(MESSAGES['error_generic'])

async def process_referral(user_id: int, referrer_id: int, username: str = None) -> bool:
    """Processa uma nova indicação"""
    try:
        # Verificar se não é auto-referência
        if user_id == referrer_id:
            return False
        
        # Verificar se referrer existe
        referrer_data = await redis_service.get_user_data(referrer_id)
        if not referrer_data:
            return False
        
        # Verificar se usuário já foi indicado
        user_data = await redis_service.get_user_data(user_id)
        if user_data and user_data.get('referred_by'):
            return False
        
        # Adicionar referral
        referrals = referrer_data.get('referrals', [])
        if user_id not in referrals:
            referrals.append(user_id)
            referrer_data['referrals'] = referrals
            await redis_service.save_user_data(referrer_id, referrer_data)
        
        # Marcar usuário como indicado
        if not user_data:
            user_data = {'id': user_id}
        
        user_data['referred_by'] = referrer_id
        user_data['referral_date'] = Update.message.date.isoformat() if hasattr(Update, 'message') else None
        await redis_service.save_user_data(user_id, user_data)
        
        # Notificar referrer
        try:
            await context.bot.send_message(
                chat_id=referrer_id,
                text=NOTIFICATIONS['new_referral'].format(
                    username=username or f"User {user_id}",
                    referrer=referrer_data.get('username', f"User {referrer_id}")
                ),
                parse_mode='Markdown'
            )
        except TelegramError:
            pass
        
        log_user_action(user_id, 'referral_processed', {
            'referrer_id': referrer_id,
            'username': username
        })
        
        return True
        
    except Exception as e:
        log_error(e, {
            'handler': 'process_referral',
            'user_id': user_id,
            'referrer_id': referrer_id
        })
        return False