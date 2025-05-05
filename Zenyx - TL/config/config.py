"""
Configurações do Bot Zenyx
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações centralizadas do bot"""
    
    # Bot
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    BOT_USERNAME: str = os.getenv('BOT_USERNAME', 'GestorPaybot')
    
    # Canal para verificação
    CHANNEL_ID: str = os.getenv('CHANNEL_ID', '@GestorPayNoticias')
    CHANNEL_USERNAME: str = os.getenv('CHANNEL_USERNAME', 'GestorPay Notícias')
    
    # Administradores
    ADMIN_IDS: List[int] = []
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    if admin_ids_str:
        ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
    
    # Redis
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_PREFIX: str = 'zenyx'
    
    # PushinPay
    PUSHINPAY_TOKEN: str = os.getenv('PUSHINPAY_TOKEN', '')
    PUSHINPAY_API_URL: str = 'https://api.pushinpay.com.br/api/pix'
    
    # Configurações de pagamento
    PAYMENT_FEE: float = 0.30  # Taxa por transação em R$
    COMMISSION_RATE: float = 0.20  # 20% de comissão
    MIN_WITHDRAWAL: float = 30.00  # Saque mínimo
    WITHDRAWAL_INTERVAL_DAYS: int = 1  # Intervalo entre saques
    
    # Planos padrão
    DEFAULT_PLANS: List[Dict[str, Any]] = [
        {"name": "Acesso Permanente (SÓ HOJE)", "price": 12.00, "duration": "permanent"},
        {"name": "Acesso Semanal", "price": 14.90, "duration": "weekly"},
        {"name": "Acesso Mensal", "price": 17.90, "duration": "monthly"},
        {"name": "Acesso Permanente", "price": 37.90, "duration": "permanent"}
    ]
    
    # Referral
    REFERRAL_BONUS: float = 125.00  # Bônus por indicação
    REFERRAL_MIN_SALES: int = 3  # Mínimo de vendas do indicado
    REFERRAL_MIN_AMOUNT: float = 9.90  # Valor mínimo de cada venda
    REFERRAL_EXPIRY_DAYS: int = 15  # Dias para expirar o vínculo
    
    # Admin VIP
    ADMIN_VIP_PRICE: float = 97.90  # Preço mensal
    ADMIN_VIP_TRIAL_DAYS: int = 30  # Dias de teste grátis
    
    # Mensagens
    SUPPORT_USERNAME: str = '@GestorPaySuporte'
    SUPPORT_URL: str = f'https://t.me/{SUPPORT_USERNAME[1:]}'
    
    # Configurações gerais
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Timeouts
    PAYMENT_TIMEOUT_MINUTES: int = 30  # Timeout para pagamentos
    CODE_EXPIRY_HOURS: int = 1  # Expiração de códigos de vinculação
    
    # Limites
    MAX_BOTS_PER_USER: int = 5  # Máximo de bots por usuário
    MAX_GROUPS_PER_BOT: int = 10  # Máximo de grupos por bot
    
    @classmethod
    def validate(cls) -> bool:
        """Validar configurações essenciais"""
        essential_vars = ['BOT_TOKEN', 'CHANNEL_ID']
        
        for var in essential_vars:
            if not getattr(cls, var):
                print(f"Erro: {var} não configurado!")
                return False
        
        return True
    
    @classmethod
    def get_admin_ids(cls) -> List[int]:
        """Retorna lista de IDs de admin"""
        return cls.ADMIN_IDS
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Verifica se usuário é admin"""
        return user_id in cls.ADMIN_IDS
    
    @classmethod
    def get_plan_by_price(cls, price: float) -> Dict[str, Any]:
        """Retorna plano pelo preço"""
        for plan in cls.DEFAULT_PLANS:
            if plan['price'] == price:
                return plan
        return {"name": "Plano Personalizado", "price": price, "duration": "custom"}
    
    @classmethod
    def format_price(cls, price: float) -> str:
        """Formata preço para exibição"""
        return f"R$ {price:.2f}"


# Configurações de exibição
DISPLAY_CONFIG = {
    'date_format': '%d/%m/%Y %H:%M:%S',
    'currency_symbol': 'R$',
    'decimal_places': 2,
    'max_message_length': 4096
}

# Emojis usados no bot
EMOJIS = {
    'verified': '✅',
    'error': '❌',
    'warning': '⚠️',
    'money': '💰',
    'robot': '🤖',
    'people': '👥',
    'crown': '👑',
    'info': 'ℹ️',
    'lock': '🔒',
    'unlock': '🔓',
    'fire': '🔥',
    'star': '⭐',
    'chart': '📊',
    'clipboard': '📋',
    'megaphone': '📢',
    'refresh': '🔄',
    'mobile': '📱',
    'key': '🔑',
    'rocket': '🚀',
    'settings': '⚙️',
    'back': '🔙',
    'document': '📄',
    'camera': '📸',
    'video': '🎥',
    'music': '🎵',
    'gift': '🎁',
    'celebration': '🎉'
}

# Estados do bot
BOT_STATES = {
    'WAITING_TOKEN': 'waiting_token',
    'WAITING_PUSHINPAY': 'waiting_pushinpay',
    'WAITING_MESSAGE': 'waiting_message',
    'WAITING_MEDIA': 'waiting_media',
    'WAITING_PLAN_NAME': 'waiting_plan_name',
    'WAITING_PLAN_PRICE': 'waiting_plan_price',
    'WAITING_PLAN_DURATION': 'waiting_plan_duration',
    'WAITING_GROUP_CODE': 'waiting_group_code'
}

# Tipos de mídia suportados
SUPPORTED_MEDIA_TYPES = ['photo', 'video', 'audio', 'document', 'animation']

# Duração dos planos
PLAN_DURATIONS = {
    'daily': {'days': 1, 'label': 'Diário'},
    'weekly': {'days': 7, 'label': 'Semanal'},
    'monthly': {'days': 30, 'label': 'Mensal'},
    'quarterly': {'days': 90, 'label': 'Trimestral'},
    'semiannual': {'days': 180, 'label': 'Semestral'},
    'annual': {'days': 365, 'label': 'Anual'},
    'permanent': {'days': None, 'label': 'Permanente'}
}