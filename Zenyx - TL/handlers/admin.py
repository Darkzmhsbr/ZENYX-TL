"""
Handler para funções administrativas
"""

import logging
import csv
import io
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config.config import Config
from utils.helpers import is_admin, log_user_action, log_error
from utils.templates import MESSAGES, BUTTONS
from services.redis_service import RedisService

logger = logging.getLogger(__name__)
redis_service = RedisService()

async def admin_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para menu administrativo"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return
    
    keyboard = [
        [InlineKeyboardButton(BUTTONS['metrics'], callback_data='admin_metrics')],
        [InlineKeyboardButton(BUTTONS['export'], callback_data='admin_export')],
        [InlineKeyboardButton(BUTTONS['remarketing'], callback_data='admin_remarketing')],
        [InlineKeyboardButton(BUTTONS['status'], callback_data='admin_status')],
        [InlineKeyboardButton(BUTTONS['online'], callback_data='admin_online')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        MESSAGES['admin_menu'],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    log_user_action(user_id, 'admin_menu_accessed')

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para callbacks administrativos"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.edit_message_text("❌ Você não tem permissão para esta ação.")
        return
    
    action = query.data.split('_')[1]
    
    try:
        if action == 'metrics':
            await show_metrics(query, context)
        elif action == 'export':
            await export_contacts(query, context)
        elif action == 'remarketing':
            await start_remarketing(query, context)
        elif action == 'status':
            await show_system_status(query, context)
        elif action == 'online':
            await show_online_users(query, context)
        elif action == 'back':
            await show_admin_menu(query, context)
        else:
            await query.edit_message_text("❌ Ação desconhecida.")
    
    except Exception as e:
        log_error(e, {'handler': 'admin_callback_handler', 'action': action})
        await query.edit_message_text("❌ Erro ao executar ação. Tente novamente.")

async def show_admin_menu(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra menu administrativo"""
    keyboard = [
        [InlineKeyboardButton(BUTTONS['metrics'], callback_data='admin_metrics')],
        [InlineKeyboardButton(BUTTONS['export'], callback_data='admin_export')],
        [InlineKeyboardButton(BUTTONS['remarketing'], callback_data='admin_remarketing')],
        [InlineKeyboardButton(BUTTONS['status'], callback_data='admin_status')],
        [InlineKeyboardButton(BUTTONS['online'], callback_data='admin_online')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES['admin_menu'],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_metrics(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra métricas de vendas"""
    try:
        # Buscar todos os usuários
        all_users = await redis_service.get_all_users()
        
        # Calcular métricas
        total_sales = 0
        total_amount = 0.0
        paying_users = 0
        
        for user_id, user_data in all_users.items():
            sales = user_data.get('sales', [])
            total_sales += len(sales)
            total_amount += sum(sale.get('amount', 0) for sale in sales)
            
            if sales:
                paying_users += 1
        
        average = total_amount / total_sales if total_sales > 0 else 0
        
        message = MESSAGES['sales_metrics'].format(
            period="Total",
            total=total_amount,
            count=total_sales,
            average=average
        )
        
        # Adicionar informações extras
        message += f"\n\n👥 Total de usuários: {len(all_users)}"
        message += f"\n💳 Usuários pagantes: {paying_users}"
        
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='admin_back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    except Exception as e:
        log_error(e, {'handler': 'show_metrics'})
        await query.edit_message_text("❌ Erro ao gerar métricas.")

async def export_contacts(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Exporta lista de contatos"""
    try:
        await query.edit_message_text(MESSAGES['export_contacts'])
        
        # Buscar todos os usuários
        all_users = await redis_service.get_all_users()
        
        # Criar CSV em memória
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalhos
        writer.writerow(['ID', 'Username', 'Nome', 'Total Gasto', 'Última Atividade'])
        
        # Dados
        for user_id, user_data in all_users.items():
            sales = user_data.get('sales', [])
            total_spent = sum(sale.get('amount', 0) for sale in sales)
            
            writer.writerow([
                user_id,
                user_data.get('username', ''),
                user_data.get('first_name', ''),
                f"R$ {total_spent:.2f}",
                user_data.get('last_activity', '')
            ])
        
        # Converter para bytes
        output.seek(0)
        csv_bytes = output.getvalue().encode('utf-8')
        
        # Enviar arquivo
        await context.bot.send_document(
            chat_id=query.from_user.id,
            document=csv_bytes,
            filename=f"contatos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            caption="📋 Lista de contatos exportada com sucesso!"
        )
        
        # Atualizar mensagem
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='admin_back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "✅ Arquivo enviado!",
            reply_markup=reply_markup
        )
    
    except Exception as e:
        log_error(e, {'handler': 'export_contacts'})
        await query.edit_message_text("❌ Erro ao exportar contatos.")

async def start_remarketing(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inicia processo de remarketing"""
    try:
        keyboard = [
            [InlineKeyboardButton("Todos os usuários", callback_data='rmkt_all')],
            [InlineKeyboardButton("Apenas não pagantes", callback_data='rmkt_unpaid')],
            [InlineKeyboardButton(BUTTONS['back'], callback_data='admin_back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            MESSAGES['remarketing'],
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        log_error(e, {'handler': 'start_remarketing'})
        await query.edit_message_text("❌ Erro ao iniciar remarketing.")

async def show_system_status(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra status do sistema"""
    try:
        # Verificar status do Redis
        try:
            await redis_service.get_all_users()
            redis_status = "✅ Online"
        except:
            redis_status = "❌ Offline"
        
        # Verificar PushinPay
        pushinpay_status = "✅ Configurado" if Config.PUSHINPAY_TOKEN else "❌ Não configurado"
        
        message = MESSAGES['system_status'].format(
            redis_status=redis_status,
            pushinpay_status=pushinpay_status
        )
        
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='admin_back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    except Exception as e:
        log_error(e, {'handler': 'show_system_status'})
        await query.edit_message_text("❌ Erro ao verificar status do sistema.")

async def show_online_users(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra usuários online"""
    try:
        # Buscar usuários ativos
        active_users = await redis_service.get_active_users(minutes=5)
        all_users = await redis_service.get_all_users()
        
        message = MESSAGES['online_users'].format(
            active_users=len(active_users),
            total_users=len(all_users)
        )
        
        # Listar alguns usuários ativos
        if active_users:
            message += "\n\n📱 Últimos ativos:"
            for user in active_users[:10]:  # Mostrar apenas os 10 primeiros
                username = user.get('username', 'Sem username')
                message += f"\n• @{username}" if username != 'Sem username' else f"\n• ID: {user.get('id')}"
        
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='admin_back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    except Exception as e:
        log_error(e, {'handler': 'show_online_users'})
        await query.edit_message_text("❌ Erro ao listar usuários online.")

async def handle_remarketing_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para callbacks de remarketing"""
    query = update.callback_query
    await query.answer()
    
    action = query.data.split('_')[1]
    
    try:
        if action == 'all':
            await send_remarketing_to_all(query, context)
        elif action == 'unpaid':
            await send_remarketing_to_unpaid(query, context)
    
    except Exception as e:
        log_error(e, {'handler': 'handle_remarketing_callback'})
        await query.edit_message_text("❌ Erro ao enviar remarketing.")

async def send_remarketing_to_all(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia remarketing para todos os usuários"""
    # Implementar lógica de envio
    await query.edit_message_text("📨 Enviando remarketing para todos os usuários...")
    # TODO: Implementar envio em lote

async def send_remarketing_to_unpaid(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia remarketing apenas para não pagantes"""
    # Implementar lógica de envio
    await query.edit_message_text("📨 Enviando remarketing para usuários não pagantes...")
    # TODO: Implementar envio em lote com filtro