"""
Serviço Redis simplificado para testes
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

class RedisService:
    """Serviço simplificado para testes"""
    
    def __init__(self):
        self.data_file = "data/bot_data.json"
        self.data = {}
        self._load_data()
    
    def _load_data(self):
        """Carrega dados do arquivo"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except:
                self.data = {}
        else:
            os.makedirs("data", exist_ok=True)
            self.data = {
                'users': {},
                'bots': {},
                'codes': {},
                'states': {}
            }
            self._save_data()
    
    def _save_data(self):
        """Salva dados no arquivo"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
    
    async def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtém dados do usuário"""
        return self.data.get('users', {}).get(str(user_id))
    
    async def save_user_data(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Salva dados do usuário"""
        if 'users' not in self.data:
            self.data['users'] = {}
        self.data['users'][str(user_id)] = data
        self._save_data()
        return True
    
    async def get_bot_data(self, token: str) -> Optional[Dict[str, Any]]:
        """Obtém dados do bot"""
        return self.data.get('bots', {}).get(token)
    
    async def save_bot_data(self, token: str, data: Dict[str, Any]) -> bool:
        """Salva dados do bot"""
        if 'bots' not in self.data:
            self.data['bots'] = {}
        self.data['bots'][token] = data
        self._save_data()
        return True
    
    async def get_bot_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Busca bot pelo token"""
        return await self.get_bot_data(token)
    
    async def get_user_state(self, user_id: int) -> Optional[str]:
        """Obtém estado do usuário"""
        return self.data.get('states', {}).get(str(user_id))
    
    async def set_user_state(self, user_id: int, state: str) -> bool:
        """Define estado do usuário"""
        if 'states' not in self.data:
            self.data['states'] = {}
        self.data['states'][str(user_id)] = state
        self._save_data()
        return True
    
    async def clear_user_state(self, user_id: int) -> bool:
        """Limpa estado do usuário"""
        if 'states' in self.data and str(user_id) in self.data['states']:
            del self.data['states'][str(user_id)]
            self._save_data()
        return True
    
    async def get_channel_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Obtém código de canal"""
        return self.data.get('codes', {}).get(code)
    
    async def save_channel_code(self, code: str, data: Dict[str, Any]) -> bool:
        """Salva código de canal"""
        if 'codes' not in self.data:
            self.data['codes'] = {}
        self.data['codes'][code] = data
        self._save_data()
        return True
    
    async def delete_channel_code(self, code: str) -> bool:
        """Remove código de canal"""
        if 'codes' in self.data and code in self.data['codes']:
            del self.data['codes'][code]
            self._save_data()
        return True
    
    async def get_all_users(self) -> Dict[int, Dict[str, Any]]:
        """Obtém todos os usuários"""
        return {int(k): v for k, v in self.data.get('users', {}).items()}
    
    async def get_payment_data(self, user_id: int, payment_id: str) -> Optional[Dict[str, Any]]:
        """Obtém dados de pagamento"""
        key = f"{user_id}:{payment_id}"
        return self.data.get('payments', {}).get(key)
    
    async def save_payment_data(self, user_id: int, payment_data: Dict[str, Any]) -> bool:
        """Salva dados de pagamento"""
        payment_id = payment_data.get('payment_id', '')
        key = f"{user_id}:{payment_id}"
        
        if 'payments' not in self.data:
            self.data['payments'] = {}
        
        self.data['payments'][key] = payment_data
        self._save_data()
        return True
    
    async def get_active_users(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Obtém usuários ativos nos últimos X minutos"""
        # Simulação para testes
        return list(self.data.get('users', {}).values())
    
    async def add_user_sale(self, user_id: int, sale_data: Dict[str, Any]) -> bool:
        """Adiciona uma venda ao histórico do usuário"""
        user_data = await self.get_user_data(user_id)
        if not user_data:
            return False
        
        if 'sales' not in user_data:
            user_data['sales'] = []
        
        user_data['sales'].append(sale_data)
        return await self.save_user_data(user_id, user_data)
    
    async def increment_user_stats(self, user_id: int, field: str, amount: float = 1.0) -> bool:
        """Incrementa estatísticas do usuário"""
        user_data = await self.get_user_data(user_id)
        if not user_data:
            return False
        
        if field not in user_data:
            user_data[field] = 0
        
        user_data[field] += amount
        return await self.save_user_data(user_id, user_data)