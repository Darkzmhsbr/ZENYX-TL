"""
Configurações do Bot Zenyx
"""

import os
from typing import List
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    # Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8099618851:AAHGyz4EsTgRrrn795JWnTJ4cNA18pv7iL4')
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'GestorPaybot')
    
    # Canal
    CHANNEL_ID = os.getenv('CHANNEL_ID', '-1002630794901')
    CHANNEL_LINK = os.getenv('CHANNEL_LINK', 'https://t.me/+c_MeI3rZn7o1MWY5')
    
    # Admin
    ADMIN_IDS = [int(os.getenv('ADMIN_USER_ID', '7864258242'))]
    
    # PushinPay
    PUSHINPAY_TOKEN = os.getenv('PUSHINPAY_TOKEN', '26627|5I0lOsq1yvn9R2R6PFn3EdwTUQjuer8NJNBkg8Cr09081214')
    
    # Configurações gerais
    COMMISSION_RATE = 0.20
    MIN_WITHDRAWAL = 30.00
    ADMIN_VIP_TRIAL_DAYS = 30
    MAX_BOTS_PER_USER = 3
    MAX_GROUPS_PER_BOT = 5
    REFERRAL_EXPIRY_DAYS = 15
    REFERRAL_MIN_SALES = 3
    REFERRAL_MIN_AMOUNT = 9.90
    WITHDRAWAL_INTERVAL_DAYS = 15
    REDIS_PREFIX = "zenyx"
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        return user_id in cls.ADMIN_IDS

# Estados do bot
BOT_STATES = {
    'WAITING_TOKEN': 'waiting_token',
    'WAITING_PUSHINPAY': 'waiting_pushinpay',
    'WAITING_MESSAGE': 'waiting_message',
    'WAITING_MEDIA': 'waiting_media',
    'WAITING_PLAN_NAME': 'waiting_plan_name'
}

# Emojis utilizados no bot
EMOJIS = {
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'money': '💰',
    'card': '💳',
    'rocket': '🚀',
    'link': '🔗',
    'lock': '🔒',
    'gift': '🎁',
    'chart': '📊',
    'time': '⏰',
    'user': '👤',
    'users': '👥',
    'settings': '⚙️',
    'search': '🔍',
    'notification': '🔔',
    'star': '⭐',
    'fire': '🔥'
}

# Durações de planos em dias
PLAN_DURATIONS = {
    'diário': {'days': 1, 'label': 'Diário'},
    'semanal': {'days': 7, 'label': 'Semanal'},
    'quinzenal': {'days': 15, 'label': 'Quinzenal'},
    'mensal': {'days': 30, 'label': 'Mensal'},
    'trimestral': {'days': 90, 'label': 'Trimestral'},
    'semestral': {'days': 180, 'label': 'Semestral'},
    'anual': {'days': 365, 'label': 'Anual'},
    'permanente': {'days': None, 'label': 'Permanente'}
}