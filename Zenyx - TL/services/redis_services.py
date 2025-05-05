"""
Serviço Redis simplificado para testes
"""

import json
import os
from typing import Dict, Any, Optional

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
            self.data = {}
    
    def _save_data(self):
        """Salva dados no arquivo"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except:
            pass
    
    async def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtém dados do usuário"""
        return self.data.get(f"user:{user_id}")
    
    async def save_user_data(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Salva dados do usuário"""
        self.data[f"user:{user_id}"] = data
        self._save_data()
        return True
    
    async def get_user_state(self, user_id: int) -> Optional[str]:
        """Obtém estado do usuário"""
        user_data = self.data.get(f"user:{user_id}", {})
        return user_data.get("state")
    
    async def set_user_state(self, user_id: int, state: str) -> bool:
        """Define estado do usuário"""
        if f"user:{user_id}" not in self.data:
            self.data[f"user:{user_id}"] = {}
        self.data[f"user:{user_id}"]["state"] = state
        self._save_data()
        return True
    
    async def clear_user_state(self, user_id: int) -> bool:
        """Limpa estado do usuário"""
        if f"user:{user_id}" in self.data:
            self.data[f"user:{user_id}"].pop("state", None)
            self._save_data()
        return True