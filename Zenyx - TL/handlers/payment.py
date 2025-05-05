"""
Handler para funções relacionadas a pagamentos e saldo
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config.config import Config
from utils.helpers import (
    format_price,
    generate_referral_link,
    can_withdraw,
    get_user_balance,
    create_back_button,
    log_user_action,
    log_error
)
from utils.templates import MESSAGES, BUTTONS
from services.redis_service import RedisService
from services.payment_service import PaymentService

logger = logging.getLogger(__name__)
redis_service = RedisService()
payment_service = PaymentService()

async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para verificar saldo"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user_data = await redis_service.get_user_data(user_id)
        
        if not user_data:
            await query.edit_message_text(
                MESSAGES['error_generic'],
                reply_markup=create_back_button()
            )
            return
        
        balance = get_user_balance(user_data)
        last_withdrawal = user_data.get('last_withdrawal')
        
        # Verificar se pode sacar
        can_withdraw_now, withdrawal_message = can_withdraw(last_withdrawal, balance)
        
        keyboard = []
        if can_withdraw_now and balance >= Config.MIN_WITHDRAWAL:
            keyboard.append([
                InlineKeyboardButton("💸 Solicitar Saque", callback_data='request_withdrawal')
            ])
        
        keyboard.append([InlineKeyboardButton(BUTTONS['back'], callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            MESSAGES['balance'].format(
                balance=balance,
                withdrawal_message=withdrawal_message
            ),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        log_user_action(user_id, 'check_balance', {'balance': balance})
        
    except Exception as e:
        log_error(e, {'handler': 'balance_handler'})
        await query.edit_message_text(MESSAGES['error_generic'])

async def referral_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para sistema de indicações"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user_data = await redis_service.get_user_data(user_id)
        
        if not user_data:
            await query.edit_message_text(
                MESSAGES['error_generic'],
                reply_markup=create_back_button()
            )
            return
        
        # Obter estatísticas de indicação
        referrals = user_data.get('referrals', [])
        referral_earnings = user_data.get('referral_earnings', 0.0)
        referral_link = generate_referral_link(Config.BOT_USERNAME, user_id)
        
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            MESSAGES['referral'].format(
                referral_count=len(referrals),
                referral_earnings=referral_earnings,
                referral_link=referral_link
            ),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        log_user_action(user_id, 'check_referrals', {
            'referral_count': len(referrals),
            'earnings': referral_earnings
        })
        
    except Exception as e:
        log_error(e, {'handler': 'referral_handler'})
        await query.edit_message_text(MESSAGES['error_generic'])

async def admin_vip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para assinatura Admin VIP"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user_data = await redis_service.get_user_data(user_id)
        
        if not user_data:
            await query.edit_message_text(
                MESSAGES['error_generic'],
                reply_markup=create_back_button()
            )
            return
        
        is_admin_vip = user_data.get('is_admin_vip', False)
        admin_vip_expiry = user_data.get('admin_vip_expiry')
        
        keyboard = []
        
        if not is_admin_vip:
            keyboard.append([
                InlineKeyboardButton(BUTTONS['activate_vip'], callback_data='activate_admin_vip')
            ])
        else:
            # Mostrar data de expiração se existir
            if admin_vip_expiry:
                expiry_date = datetime.fromisoformat(admin_vip_expiry)
                days_left = (expiry_date - datetime.now()).days
                message = MESSAGES['admin_vip'] + f"\n\n⏰ Seu plano expira em {days_left} dias."
            else:
                message = MESSAGES['admin_vip'] + "\n\n✅ Você já é Admin VIP!"
        
        keyboard.append([InlineKeyboardButton(BUTTONS['back'], callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message if 'message' in locals() else MESSAGES['admin_vip'],
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        log_user_action(user_id, 'check_admin_vip', {'is_vip': is_admin_vip})
        
    except Exception as e:
        log_error(e, {'handler': 'admin_vip_handler'})
        await query.edit_message_text(MESSAGES['error_generic'])

async def activate_admin_vip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para ativar período gratuito Admin VIP"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user_data = await redis_service.get_user_data(user_id)
        
        if not user_data:
            await query.edit_message_text(
                MESSAGES['error_generic'],
                reply_markup=create_back_button()
            )
            return
        
        # Verificar se já usou período gratuito
        if user_data.get('used_free_trial', False):
            await query.edit_message_text(
                "❌ Você já utilizou seu período gratuito.",
                reply_markup=create_back_button()
            )
            return
        
        # Ativar período gratuito
        expiry_date = datetime.now() + timedelta(days=Config.ADMIN_VIP_TRIAL_DAYS)
        user_data['is_admin_vip'] = True
        user_data['admin_vip_expiry'] = expiry_date.isoformat()
        user_data['used_free_trial'] = True
        
        await redis_service.save_user_data(user_id, user_data)
        
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            MESSAGES['admin_vip_activated'],
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        log_user_action(user_id, 'activate_admin_vip_trial')
        
    except Exception as e:
        log_error(e, {'handler': 'activate_admin_vip_handler'})
        await query.edit_message_text(MESSAGES['error_generic'])

async def how_it_works_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para explicação de como funciona"""
    query = update.callback_query
    await query.answer()
    
    try:
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            MESSAGES['how_it_works'],
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        log_user_action(update.effective_user.id, 'view_how_it_works')
        
    except Exception as e:
        log_error(e, {'handler': 'how_it_works_handler'})
        await query.edit_message_text(MESSAGES['error_generic'])

async def request_withdrawal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para solicitar saque"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user_data = await redis_service.get_user_data(user_id)
        
        if not user_data:
            await query.edit_message_text(
                MESSAGES['error_generic'],
                reply_markup=create_back_button()
            )
            return
        
        balance = get_user_balance(user_data)
        last_withdrawal = user_data.get('last_withdrawal')
        
        # Verificar se pode sacar
        can_withdraw_now, withdrawal_message = can_withdraw(last_withdrawal, balance)
        
        if not can_withdraw_now:
            await query.edit_message_text(
                f"❌ {withdrawal_message}",
                reply_markup=create_back_button('balance')
            )
            return
        
        # Processar saque
        success = await payment_service.process_withdrawal(user_id, balance)
        
        if success:
            # Atualizar saldo e data do último saque
            user_data['balance'] = 0.0
            user_data['last_withdrawal'] = datetime.now().isoformat()
            await redis_service.save_user_data(user_id, user_data)
            
            await query.edit_message_text(
                MESSAGES['withdrawal_success'],
                reply_markup=create_back_button()
            )
            
            # Notificar admins
            await notify_admins_withdrawal(context, user_id, balance)
            
            log_user_action(user_id, 'withdrawal_success', {'amount': balance})
        else:
            await query.edit_message_text(
                "❌ Erro ao processar saque. Tente novamente mais tarde.",
                reply_markup=create_back_button('balance')
            )
            
            log_user_action(user_id, 'withdrawal_failed', {'amount': balance})
            
    except Exception as e:
        log_error(e, {'handler': 'request_withdrawal_handler'})
        await query.edit_message_text(MESSAGES['error_generic'])

async def notify_admins_withdrawal(context: ContextTypes.DEFAULT_TYPE, user_id: int, amount: float) -> None:
    """Notifica admins sobre solicitação de saque"""
    from utils.templates import NOTIFICATIONS
    
    user_data = await redis_service.get_user_data(user_id)
    username = user_data.get('username', f"User {user_id}")
    
    message = NOTIFICATIONS['withdrawal_request'].format(
        username=username,
        amount=amount
    )
    
    for admin_id in Config.ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")