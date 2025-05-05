"""
Serviço de pagamentos PushinPay
"""

import logging
import requests
import json
import base64
from typing import Dict, Any, Optional
from datetime import datetime

from config.config import Config
from utils.helpers import log_error

logger = logging.getLogger(__name__)

class PaymentService:
    """Serviço para integração com PushinPay"""
    
    def __init__(self):
        self.base_url = "https://api.pushinpay.com.br"
        self.token = Config.PUSHINPAY_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    async def create_pix_payment(self, amount: float, webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """Cria um pagamento PIX com QR Code"""
        try:
            payload = {
                'value': int(amount * 100)  # Converter para centavos
            }
            
            if webhook_url:
                payload['webhook_url'] = webhook_url
            
            response = requests.post(
                f"{self.base_url}/api/pix/cashIn",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'payment_id': result.get('id'),
                    'qr_code': result.get('qr_code'),
                    'qr_code_base64': result.get('qr_code_base64'),
                    'status': result.get('status')
                }
            else:
                logger.error(f"Payment creation failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Erro ao criar pagamento: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            log_error(e, {'method': 'create_pix_payment', 'amount': amount})
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Verifica status de um pagamento"""
        try:
            response = requests.get(
                f"{self.base_url}/api/transactions/{payment_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'payment_id': result.get('id'),
                    'status': result.get('status'),
                    'paid': result.get('status') == 'paid'
                }
            else:
                return {
                    'success': False,
                    'error': f"Erro ao verificar pagamento: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            log_error(e, {'method': 'check_payment_status', 'payment_id': payment_id})
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_pix_transfer(self, amount: float, pix_key: str, pix_key_type: str, webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """Cria uma transferência PIX (cashOut)"""
        try:
            payload = {
                'value': int(amount * 100),  # Converter para centavos
                'pix_key': pix_key,
                'pix_key_type': pix_key_type  # evp, cpf, cnpj, phone, email
            }
            
            if webhook_url:
                payload['webhook_url'] = webhook_url
            
            response = requests.post(
                f"{self.base_url}/api/pix/cashOut",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'transfer_id': result.get('id'),
                    'status': result.get('status'),
                    'receiver_name': result.get('receiver_name')
                }
            else:
                return {
                    'success': False,
                    'error': f"Erro ao criar transferência: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            log_error(e, {'method': 'create_pix_transfer', 'amount': amount})
            return {
                'success': False,
                'error': str(e)
            }
    
    async def check_transfer_status(self, transfer_id: str) -> Dict[str, Any]:
        """Verifica status de uma transferência"""
        try:
            response = requests.get(
                f"{self.base_url}/api/transfers/{transfer_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'transfer_id': result.get('id'),
                    'status': result.get('status'),
                    'paid': result.get('status') == 'paid',
                    'receiver_name': result.get('receiver_name'),
                    'end_to_end_id': result.get('end_to_end_id')
                }
            else:
                return {
                    'success': False,
                    'error': f"Erro ao verificar transferência: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            log_error(e, {'method': 'check_transfer_status', 'transfer_id': transfer_id})
            return {
                'success': False,
                'error': str(e)
            }
    
    async def refund_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Realiza estorno de uma transação"""
        try:
            response = requests.post(
                f"{self.base_url}/api/transactions/{transaction_id}/refund",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Transação sendo processada para estorno'
                }
            else:
                error_data = response.json() if response.text else {}
                return {
                    'success': False,
                    'error': error_data.get('error', f"Erro ao estornar: {response.status_code}")
                }
                
        except Exception as e:
            log_error(e, {'method': 'refund_transaction', 'transaction_id': transaction_id})
            return {
                'success': False,
                'error': str(e)
            }
    
    def decode_base64_to_image(self, base64_string: str) -> bytes:
        """Converte uma string base64 em imagem"""
        # Remove o prefixo 'data:image/png;base64,' se existir
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        
        try:
            image_data = base64.b64decode(base64_string)
            return image_data
        except Exception as e:
            logger.error(f"Erro ao decodificar base64: {str(e)}")
            return None
    
    def format_currency(self, value_in_cents: int) -> str:
        """Formata valor em centavos para moeda"""
        value_in_reais = value_in_cents / 100
        return f"R$ {value_in_reais:.2f}".replace(".", ",")
    
    async def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa dados do webhook"""
        try:
            payment_id = data.get('id')
            status = data.get('status')
            value = data.get('value')
            
            if status == 'paid':
                # Pagamento confirmado
                return {
                    'success': True,
                    'action': 'payment_confirmed',
                    'payment_id': payment_id,
                    'value': value
                }
            else:
                # Outros status
                return {
                    'success': True,
                    'action': f'payment_{status}',
                    'payment_id': payment_id
                }
                
        except Exception as e:
            log_error(e, {'method': 'process_webhook'})
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_withdrawal(self, user_id: int, amount: float, pix_key: str, pix_key_type: str = "evp") -> bool:
        """Processa um saque para o usuário via PIX"""
        try:
            # Criar transferência PIX para o usuário
            result = await self.create_pix_transfer(
                amount=amount,
                pix_key=pix_key,
                pix_key_type=pix_key_type
            )
            
            if result['success']:
                logger.info(f"Withdrawal processed: User {user_id}, Amount: {amount}, Transfer ID: {result['transfer_id']}")
                return True
            else:
                logger.error(f"Withdrawal failed: User {user_id}, Error: {result['error']}")
                return False
            
        except Exception as e:
            log_error(e, {'method': 'process_withdrawal', 'user_id': user_id, 'amount': amount})
            return False