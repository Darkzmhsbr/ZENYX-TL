#!/usr/bin/env python3
"""
Script para iniciar todos os bots do sistema
"""

import os
import subprocess
import sys
import time

def start_bot(script_name):
    """Inicia um bot em processo separado"""
    subprocess.Popen([
        sys.executable,
        script_name
    ])

if __name__ == "__main__":
    # Iniciar bot principal
    start_bot("main.py")
    print("Bot principal iniciado!")
    
    # Pequeno delay
    time.sleep(3)
    
    # Iniciar bots dos usuários
    start_bot("user_bot_main.py")
    print("Iniciando bots dos usuários...")
    
    print("Sistema iniciado com sucesso!")