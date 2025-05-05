"""
Funções auxiliares do Bot Zenyx
"""

import re
import random
import string
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from telegram import Bot, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from config.config import Config, EMOJIS, PLAN_DURATIONS

logger = logging.getLogger(__name__)

# Funções de validação
def is_valid_token(token: str) -> bool:
    """Verifica se o token do bot é válido"""
    pattern = r'^\d+:[A-Za-z0-9_-]{35}$'
    return bool(re.match(pattern, token))

def is_valid_pushinpay_token(token: str) -> bool:
    """Verifica se o token PushinPay é válido"""
    pattern = r'^\d+\|[A-Za-z0-9]{40,}$'
    return bool(re.match(pattern, token))

def is_valid_price(price: str) -> bool:
    """Verifica se o preço é válido"""
    try:
        value = float(price.replace(',', '.'))
        return value > 0
    except ValueError:
        return False

def sanitize_price(price: str) -> float:
    """Sanitiza e converte preço para float"""
    return float(price.replace(',', '.'))

# Funções de geração
def generate_code(length: int = 8) -> str:
    """Gera um código aleatório"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_referral_link(bot_username: str, user_id: int) -> str:
    """Gera link de referência"""
    return f"https://t.me/{bot_username}?start=ref_{user_id}"

def generate_transaction_id() -> str:
    """Gera ID único para transação"""
    return hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:16]

# Funções de formatação
def format_price(price: float) -> str:
    """Formata preço para exibição"""
    return f"R$ {price:.2f}"

def format_datetime(dt: datetime) -> str:
    """Formata data/hora para exibição"""
    return dt.strftime("%d/%m/%Y %H:%M:%S")

def format_username(username: Optional[str]) -> str:
    """Formata username para exibição"""
    if not username:
        return "Usuário"
    return f"@{username}" if not username.startswith('@') else username

# Funções de verificação
async def is_user_in_channel(bot: Bot, channel_id: str, user_id: int) -> bool:
    """Verifica se usuário está no canal"""
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in [
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER,
            ChatMember.CREATOR
        ]
    except TelegramError:
        return False

async def is_bot_admin_in_chat(bot: Bot, chat_id: Union[str, int]) -> bool:
    """Verifica se o bot é admin no chat"""
    try:
        bot_member = await bot.get_chat_member(chat_id, bot.id)
        return bot_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except TelegramError:
        return False

def is_admin(user_id: int) -> bool:
    """Verifica se usuário é administrador"""
    return Config.is_admin(user_id)

# Funções de cálculo
def calculate_commission(amount: float, rate: float = Config.COMMISSION_RATE) -> float:
    """Calcula comissão"""
    return amount * rate

def calculate_plan_expiry(duration: str) -> Optional[datetime]:
    """Calcula data de expiração do plano"""
    if duration not in PLAN_DURATIONS:
        return None
    
    days = PLAN_DURATIONS[duration]['days']
    if days is None:  # Plano permanente
        return None
    
    return datetime.now() + timedelta(days=days)

def can_withdraw(last_withdrawal: Optional[datetime], balance: float) -> tuple[bool, str]:
    """Verifica se usuário pode sacar"""
    if balance < Config.MIN_WITHDRAWAL:
        return False, f"Saldo mínimo para saque: {format_price(Config.MIN_WITHDRAWAL)}"
    
    if last_withdrawal:
        next_withdrawal = last_withdrawal + timedelta(days=Config.WITHDRAWAL_INTERVAL_DAYS)
        if datetime.now() < next_withdrawal:
            return False, f"Próximo saque disponível em: {format_datetime(next_withdrawal)}"
    
    return True, "Saque disponível"

# Funções de parse
def parse_plan_input(text: str) -> Optional[Dict[str, Any]]:
    """Parse input de criação de plano"""
    parts = text.split('|')
    if len(parts) != 3:
        return None
    
    name = parts[0].strip()
    try:
        price = sanitize_price(parts[1].strip())
    except ValueError:
        return None
    
    duration_text = parts[2].strip().lower()
    duration = None
    
    # Tentar encontrar duração correspondente
    for key, value in PLAN_DURATIONS.items():
        if value['label'].lower() in duration_text or key in duration_text:
            duration = key
            break
    
    if not duration:
        # Tentar parse de dias
        days_match = re.search(r'(\d+)\s*dia', duration_text)
        if days_match:
            days = int(days_match.group(1))
            if days == 1:
                duration = 'daily'
            elif days == 7:
                duration = 'weekly'
            elif days == 30:
                duration = 'monthly'
            else:
                duration = 'custom'
    
    if not duration:
        return None
    
    return {
        'name': name,
        'price': price,
        'duration': duration
    }

def parse_referral_start(text: str) -> Optional[int]:
    """Parse parâmetro de referência do /start"""
    match = re.match(r'/start ref_(\d+)', text)
    if match:
        return int(match.group(1))
    return None

# Funções de criação de teclados
def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Cria teclado do menu principal"""
    from utils.templates import BUTTONS
    
    keyboard = [
        [InlineKeyboardButton(BUTTONS['create_bot'], callback_data='create_bot')],
        [InlineKeyboardButton(BUTTONS['balance'], callback_data='balance')],
        [InlineKeyboardButton(BUTTONS['referral'], callback_data='referral')],
        [InlineKeyboardButton(BUTTONS['admin_vip'], callback_data='admin_vip')],
        [InlineKeyboardButton(BUTTONS['how_it_works'], callback_data='how_it_works')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_bot_config_keyboard() -> InlineKeyboardMarkup:
    """Cria teclado de configuração do bot"""
    from utils.templates import BUTTONS
    
    keyboard = [
        [InlineKeyboardButton(BUTTONS['config_message'], callback_data='config_message')],
        [InlineKeyboardButton(BUTTONS['config_pushinpay'], callback_data='config_pushinpay')],
        [InlineKeyboardButton(BUTTONS['config_channel'], callback_data='config_channel')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_message_config_keyboard() -> InlineKeyboardMarkup:
    """Cria teclado de configuração de mensagem"""
    from utils.templates import BUTTONS
    
    keyboard = [
        [InlineKeyboardButton(BUTTONS['media'], callback_data='config_media'),
         InlineKeyboardButton(BUTTONS['text'], callback_data='config_text')],
        [InlineKeyboardButton(BUTTONS['create_plans'], callback_data='create_plans')],
        [InlineKeyboardButton(BUTTONS['full_preview'], callback_data='full_preview')],
        [InlineKeyboardButton(BUTTONS['back'], callback_data='back_config')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_back_button(callback_data: str = 'back') -> InlineKeyboardMarkup:
    """Cria botão de voltar"""
    from utils.templates import BUTTONS
    
    keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)

# Funções de log
def log_user_action(user_id: int, action: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Registra ação do usuário"""
    log_entry = {
        'user_id': user_id,
        'action': action,
        'timestamp': datetime.now().isoformat(),
        'details': details or {}
    }
    logger.info(f"User action: {log_entry}")

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Registra erro"""
    error_entry = {
        'error': str(error),
        'type': type(error).__name__,
        'timestamp': datetime.now().isoformat(),
        'context': context or {}
    }
    logger.error(f"Error occurred: {error_entry}", exc_info=True)

# Funções de validação de estado
def validate_user_state(user_data: Dict[str, Any], required_state: str) -> bool:
    """Valida se usuário está no estado correto"""
    return user_data.get('state') == required_state

def get_user_balance(user_data: Dict[str, Any]) -> float:
    """Obtém saldo do usuário"""
    return user_data.get('balance', 0.0)

def get_user_referrals(user_data: Dict[str, Any]) -> List[int]:
    """Obtém lista de indicados do usuário"""
    return user_data.get('referrals', [])

# Funções de tempo
def is_expired(timestamp: datetime, expiry_hours: int) -> bool:
    """Verifica se um timestamp expirou"""
    expiry_time = timestamp + timedelta(hours=expiry_hours)
    return datetime.now() > expiry_time

def get_remaining_time(timestamp: datetime, duration_days: int) -> str:
    """Obtém tempo restante formatado"""
    end_time = timestamp + timedelta(days=duration_days)
    remaining = end_time - datetime.now()
    
    if remaining.total_seconds() <= 0:
        return "Expirado"
    
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    
    if days > 0:
        return f"{days} dias, {hours} horas"
    elif hours > 0:
        return f"{hours} horas, {minutes} minutos"
    else:
        return f"{minutes} minutos"

# Funções de processamento de mídia
def get_media_type(message) -> Optional[str]:
    """Identifica o tipo de mídia da mensagem"""
    if message.photo:
        return 'photo'
    elif message.video:
        return 'video'
    elif message.audio:
        return 'audio'
    elif message.document:
        return 'document'
    elif message.animation:
        return 'animation'
    return None

def extract_media_id(message) -> Optional[str]:
    """Extrai o ID da mídia da mensagem"""
    if message.photo:
        return message.photo[-1].file_id  # Pega a maior resolução
    elif message.video:
        return message.video.file_id
    elif message.audio:
        return message.audio.file_id
    elif message.document:
        return message.document.file_id
    elif message.animation:
        return message.animation.file_id
    return None

# Funções de manipulação de texto
def replace_placeholders(text: str, user_data: Dict[str, Any]) -> str:
    """Substitui placeholders no texto"""
    replacements = {
        '{firstname}': user_data.get('first_name', ''),
        '{username}': user_data.get('username', ''),
        '{id}': str(user_data.get('id', '')),
    }
    
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)
    
    return text

def truncate_text(text: str, max_length: int = 4096) -> str:
    """Trunca texto se exceder tamanho máximo"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

# Funções de validação de negócio
def can_create_bot(user_data: Dict[str, Any]) -> tuple[bool, str]:
    """Verifica se usuário pode criar um novo bot"""
    current_bots = len(user_data.get('bots', []))
    
    if current_bots >= Config.MAX_BOTS_PER_USER:
        return False, f"Limite máximo de {Config.MAX_BOTS_PER_USER} bots atingido"
    
    return True, "Pode criar bot"

def can_add_group(bot_data: Dict[str, Any]) -> tuple[bool, str]:
    """Verifica se pode adicionar mais um grupo ao bot"""
    current_groups = len(bot_data.get('linked_groups', []))
    
    if current_groups >= Config.MAX_GROUPS_PER_BOT:
        return False, f"Limite máximo de {Config.MAX_GROUPS_PER_BOT} grupos atingido"
    
    return True, "Pode adicionar grupo"

def validate_referral_eligibility(referral_data: Dict[str, Any]) -> bool:
    """Valida se referral é elegível para bonus"""
    sales_count = referral_data.get('sales_count', 0)
    total_amount = referral_data.get('total_amount', 0)
    signup_date = referral_data.get('signup_date')
    
    if not signup_date:
        return False
    
    # Verifica se está dentro do período
    days_since_signup = (datetime.now() - signup_date).days
    if days_since_signup > Config.REFERRAL_EXPIRY_DAYS:
        return False
    
    # Verifica requisitos mínimos
    if sales_count < Config.REFERRAL_MIN_SALES:
        return False
    
    if total_amount < (Config.REFERRAL_MIN_AMOUNT * Config.REFERRAL_MIN_SALES):
        return False
    
    return True

# Funções de relatório
def generate_sales_report(sales_data: List[Dict[str, Any]], period: str = 'all') -> Dict[str, Any]:
    """Gera relatório de vendas"""
    total_sales = len(sales_data)
    total_amount = sum(sale.get('amount', 0) for sale in sales_data)
    average_ticket = total_amount / total_sales if total_sales > 0 else 0
    
    # Agrupa por plano
    plans_count = {}
    for sale in sales_data:
        plan_name = sale.get('plan_name', 'Unknown')
        plans_count[plan_name] = plans_count.get(plan_name, 0) + 1
    
    return {
        'period': period,
        'total_sales': total_sales,
        'total_amount': total_amount,
        'average_ticket': average_ticket,
        'plans_count': plans_count,
        'generated_at': datetime.now().isoformat()
    }

def generate_user_report(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Gera relatório do usuário"""
    return {
        'user_id': user_data.get('id'),
        'username': user_data.get('username'),
        'balance': user_data.get('balance', 0),
        'total_bots': len(user_data.get('bots', [])),
        'total_referrals': len(user_data.get('referrals', [])),
        'is_admin_vip': user_data.get('is_admin_vip', False),
        'created_at': user_data.get('created_at'),
        'last_activity': user_data.get('last_activity')
    }

# Funções de notificação
async def notify_admin(bot: Bot, message: str) -> None:
    """Envia notificação para todos os admins"""
    for admin_id in Config.ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=f"🔔 *Notificação Admin*\n\n{message}",
                parse_mode='Markdown'
            )
        except TelegramError as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

async def notify_user_sale(bot: Bot, user_id: int, sale_data: Dict[str, Any]) -> None:
    """Notifica usuário sobre uma venda"""
    from utils.templates import NOTIFICATIONS
    
    message = NOTIFICATIONS['new_sale'].format(
        plan_name=sale_data.get('plan_name'),
        amount=sale_data.get('amount'),
        username=sale_data.get('buyer_username', 'Unknown')
    )
    
    try:
        await bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
    except TelegramError as e:
        logger.error(f"Failed to notify user {user_id} about sale: {e}")

# Funções de segurança
def is_safe_input(text: str) -> bool:
    """Verifica se input é seguro"""
    # Verifica se contém caracteres perigosos
    dangerous_chars = ['<', '>', '&', '"', "'", ';', '\\', '|']
    return not any(char in text for char in dangerous_chars)

def sanitize_input(text: str) -> str:
    """Sanitiza input do usuário"""
    # Remove caracteres perigosos
    safe_text = text.replace('<', '').replace('>', '')
    safe_text = safe_text.replace('&', '').replace('"', '')
    safe_text = safe_text.replace("'", '').replace(';', '')
    safe_text = safe_text.replace('\\', '').replace('|', '')
    
    return safe_text.strip()

# Funções de cache
def get_cache_key(prefix: str, identifier: str) -> str:
    """Gera chave de cache"""
    return f"{Config.REDIS_PREFIX}:{prefix}:{identifier}"

def calculate_ttl(expiry_time: datetime) -> int:
    """Calcula TTL em segundos"""
    remaining = expiry_time - datetime.now()
    return max(0, int(remaining.total_seconds()))

# Funções de erro
def handle_telegram_error(error: TelegramError) -> str:
    """Trata erros do Telegram e retorna mensagem amigável"""
    error_messages = {
        "Bad Request: user not found": "Usuário não encontrado.",
        "Bad Request: chat not found": "Chat não encontrado.",
        "Forbidden: bot was blocked by the user": "O usuário bloqueou o bot.",
        "Forbidden: bot is not a member of the": "O bot não é membro do grupo/canal.",
        "Bad Request: not enough rights": "O bot não tem permissões suficientes."
    }
    
    error_str = str(error)
    for pattern, message in error_messages.items():
        if pattern in error_str:
            return message
    
    return "Ocorreu um erro. Por favor, tente novamente."

# Funções utilitárias gerais
def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Divide lista em chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Mescla dois dicionários recursivamente"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def format_file_size(size_bytes: int) -> str:
    """Formata tamanho de arquivo"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

# Funções de estatísticas
def calculate_user_stats(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula estatísticas do usuário"""
    total_earnings = user_data.get('total_earnings', 0)
    total_withdrawals = user_data.get('total_withdrawals', 0)
    total_sales = len(user_data.get('sales', []))
    active_bots = len([bot for bot in user_data.get('bots', []) if bot.get('active', False)])
    
    return {
        'total_earnings': total_earnings,
        'total_withdrawals': total_withdrawals,
        'available_balance': user_data.get('balance', 0),
        'total_sales': total_sales,
        'active_bots': active_bots,
        'total_referrals': len(user_data.get('referrals', [])),
        'conversion_rate': (total_sales / active_bots * 100) if active_bots > 0 else 0
    }

def calculate_platform_stats(all_users: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula estatísticas da plataforma"""
    total_users = len(all_users)
    active_users = len([u for u in all_users if u.get('last_activity', datetime.min) > datetime.now() - timedelta(days=7)])
    total_revenue = sum(u.get('total_earnings', 0) for u in all_users)
    total_bots = sum(len(u.get('bots', [])) for u in all_users)
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'total_revenue': total_revenue,
        'total_bots': total_bots,
        'average_revenue_per_user': total_revenue / total_users if total_users > 0 else 0
    }