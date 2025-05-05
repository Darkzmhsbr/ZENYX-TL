"""
Handler para criação e gerenciamento de bots dos usuários
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config.config import Config, BOT_STATES
from utils.helpers import (
    is_valid_token,
    can_create_bot,
    create_back_button,
    log_user_action,
    log_error
)
from utils.templates import MESSAGES, BUTTONS, ERROR_MESSAGES
from services.redis_service import RedisService
from services.botfather_service import BotFatherService

logger = logging.getLogger(__name__)
redis_service = RedisService()
botfather_service = BotFatherService()

async def create_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para iniciar processo de criação de bot"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        
        # Verificar se usuário pode criar mais bots
        user_data = await redis_service.get_user_data(user_id)
        can_create, message = can_create_bot(user_data)
        
        if not can_create:
            await query.edit_message_text(
                f"❌ {message}",
                reply_markup=create_back_button()
            )
            return
        
        # Mostrar instruções
        reply_markup = create_back_button()
        await query.edit_message_text(
            MESSAGES['create_bot'],
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Definir estado para aguardar token
        await redis_service.set_user_state(user_id, BOT_STATES['WAITING_TOKEN'])
        
        log_user_action(user_id, 'start_bot_creation')
        
    except Exception as e:
        log_error(e, {'handler': 'create_bot_handler', 'user_id': user_id if 'user_id' in locals() else None})
        await query.edit_message_text(MESSAGES['error_generic'])

async def handle_token_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para processar token do bot"""
    try:
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Verificar se está no estado correto
        user_state = await redis_service.get_user_state(user_id)
        if user_state != BOT_STATES['WAITING_TOKEN']:
            return
        
        # Validar formato do token
        if not is_valid_token(message_text):
            await update.message.reply_text(
                MESSAGES['invalid_token'],
                parse_mode='Markdown'
            )
            return
        
        # Verificar se token já está em uso
        existing_bot = await redis_service.get_bot_by_token(message_text)
        if existing_bot:
            await update.message.reply_text(
                ERROR_MESSAGES['token_already_used']
            )
            return
        
        # Mostrar mensagem de processamento
        processing_message = await update.message.reply_text(
            MESSAGES['bot_starting']
        )
        
        # Iniciar bot com o token
        bot_info = await botfather_service.start_bot(message_text)
        
        if not bot_info:
            await processing_message.edit_text(
                ERROR_MESSAGES['bot_creation']
            )
            return
        
        # Salvar dados do bot
        bot_data = {
            'token': message_text,
            'owner_id': user_id,
            'username': bot_info.get('username'),
            'config': {
                'welcome_message': '',
                'media_type': None,
                'media_id': None,
                'plans': [],
                'pushinpay_token': '',
                'linked_groups': []
            },
            'created_at': update.message.date.isoformat(),
            'active': True
        }
        
        await redis_service.save_bot_data(message_text, bot_data)
        
        # Adicionar bot à lista do usuário
        user_data = await redis_service.get_user_data(user_id)
        user_bots = user_data.get('bots', [])
        if message_text not in user_bots:
            user_bots.append(message_text)
            user_data['bots'] = user_bots
            await redis_service.save_user_data(user_id, user_data)
        
        # Atualizar mensagem com sucesso
        await processing_message.edit_text(
            MESSAGES['bot_created'].format(bot_username=bot_info.get('username'))
        )
        
        # Adicionar botão para iniciar configuração
        keyboard = [[
            InlineKeyboardButton(
                f"🚀 Iniciar @{bot_info.get('username')}",
                url=f"https://t.me/{bot_info.get('username')}"
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            MESSAGES['bot_started'].format(bot_username=bot_info.get('username')),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Limpar estado
        await redis_service.clear_user_state(user_id)
        
        log_user_action(user_id, 'bot_created', {
            'bot_username': bot_info.get('username'),
            'token': message_text[:10] + '...'  # Log parcial por segurança
        })
        
    except TelegramError as e:
        log_error(e, {'handler': 'handle_token_input', 'user_id': user_id if 'user_id' in locals() else None})
        await update.message.reply_text(ERROR_MESSAGES['bot_creation'])
    except Exception as e:
        log_error(e, {'handler': 'handle_token_input', 'user_id': user_id if 'user_id' in locals() else None})
        await update.message.reply_text(MESSAGES['error_generic'])

async def handle_bot_configuration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para configuração do bot do usuário"""
    try:
        user_id = update.effective_user.id
        bot_token = context.bot.token
        
        # Verificar se é o dono do bot
        bot_data = await redis_service.get_bot_data(bot_token)
        if not bot_data or bot_data.get('owner_id') != user_id:
            await update.message.reply_text(
                ERROR_MESSAGES['permission']
            )
            return
        
        # Mostrar mensagem de boas-vindas admin
        await update.message.reply_text(
            MESSAGES['admin_welcome'].format(
                username=update.effective_user.username,
                bot_username=context.bot.username
            ),
            parse_mode='Markdown'
        )
        
        # Mostrar menu de configuração
        keyboard = [
            [InlineKeyboardButton(BUTTONS['config_message'], callback_data='config_message')],
            [InlineKeyboardButton(BUTTONS['config_pushinpay'], callback_data='config_pushinpay')],
            [InlineKeyboardButton(BUTTONS['config_channel'], callback_data='config_channel')]
        ]
        
        # Adicionar botão de configurações avançadas se tudo estiver configurado
        config = bot_data.get('config', {})
        if (config.get('welcome_message') and 
            config.get('pushinpay_token') and 
            config.get('plans')):
            keyboard.append([
                InlineKeyboardButton(BUTTONS['advanced_config'], callback_data='advanced_config')
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            MESSAGES['config_menu'],
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        log_user_action(user_id, 'bot_configuration_started', {
            'bot_username': context.bot.username
        })
        
    except Exception as e:
        log_error(e, {'handler': 'handle_bot_configuration'})
        await update.message.reply_text(MESSAGES['error_generic'])

async def handle_config_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para callbacks de configuração do bot"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        bot_token = context.bot.token
        action = query.data
        
        # Verificar se é o dono do bot
        bot_data = await redis_service.get_bot_data(bot_token)
        if not bot_data or bot_data.get('owner_id') != user_id:
            await query.edit_message_text(ERROR_MESSAGES['permission'])
            return
        
        # Processar ação de configuração
        if action == 'config_message':
            await handle_config_message(query, context, bot_data)
        elif action == 'config_pushinpay':
            await handle_config_pushinpay(query, context, user_id)
        elif action == 'config_channel':
            await handle_config_channel(query, context, bot_data)
        elif action == 'advanced_config':
            await handle_advanced_config(query, context, bot_data)
        elif action.startswith('config_'):
            await handle_specific_config(query, context, action, bot_data)
        
    except Exception as e:
        log_error(e, {'handler': 'handle_config_callback'})
        await query.edit_message_text(MESSAGES['error_generic'])

async def handle_config_message(query, context, bot_data):
    """Handler para configuração de mensagem de boas-vindas"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTONS['media'], callback_data='config_media'),
            InlineKeyboardButton(BUTTONS['text'], callback_data='config_text')
        ],
        [InlineKeyboardButton(BUTTONS['create_plans'], callback_data='config_plans')],
        [InlineKeyboardButton(BUTTONS['full_preview'], callback_data='config_preview')],
        [InlineKeyboardButton(BUTTONS['back'], callback_data='config_main')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        MESSAGES['config_message'],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_config_pushinpay(query, context, user_id):
    """Handler para configuração do PushinPay"""
    await query.edit_message_text(
        MESSAGES['pushinpay_config'],
        reply_markup=create_back_button('config_main')
    )
    
    # Definir estado para aguardar token PushinPay
    await redis_service.set_user_state(user_id, BOT_STATES['WAITING_PUSHINPAY'])

async def handle_config_channel(query, context, bot_data):
    """Handler para configuração de canal/grupo"""
    config = bot_data.get('config', {})
    linked_groups = config.get('linked_groups', [])
    
    if not linked_groups:
        # Nenhum grupo configurado
        keyboard = [
            [InlineKeyboardButton(BUTTONS['add_channel'], callback_data='add_channel')],
            [InlineKeyboardButton(BUTTONS['back'], callback_data='config_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            MESSAGES['channel_config'],
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        # Mostrar grupos configurados
        text = "👥 *GRUPOS/CANAIS CONFIGURADOS*\n\n"
        for i, group in enumerate(linked_groups, 1):
            text += f"{i}. {group['title']} ({group['type']})\n"
        
        keyboard = [
            [InlineKeyboardButton(BUTTONS['add_channel'], callback_data='add_channel')],
            [InlineKeyboardButton(BUTTONS['back'], callback_data='config_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_advanced_config(query, context, bot_data):
    """Handler para configurações avançadas"""
    keyboard = [
        [InlineKeyboardButton("🔄 Remarketing", callback_data='advanced_remarketing')],
        [InlineKeyboardButton("📊 Métricas", callback_data='advanced_metrics')],
        [InlineKeyboardButton("👥 Usuários Ativos", callback_data='advanced_users')],
        [InlineKeyboardButton("📋 Exportar Contatos", callback_data='advanced_export')],
        [InlineKeyboardButton(BUTTONS['back'], callback_data='config_main')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        MESSAGES['advanced_config'],
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_specific_config(query, context, action, bot_data):
    """Handler para ações específicas de configuração"""
    user_id = query.from_user.id
    
    if action == 'config_media':
        await query.edit_message_text(
            MESSAGES['config_media'],
            reply_markup=create_back_button('config_message')
        )
        await redis_service.set_user_state(user_id, BOT_STATES['WAITING_MEDIA'])
    
    elif action == 'config_text':
        await query.edit_message_text(
            MESSAGES['config_text'],
            reply_markup=create_back_button('config_message'),
            parse_mode='Markdown'
        )
        await redis_service.set_user_state(user_id, BOT_STATES['WAITING_MESSAGE'])
    
    elif action == 'config_plans':
        await query.edit_message_text(
            MESSAGES['create_plans'],
            reply_markup=create_back_button('config_message'),
            parse_mode='Markdown'
        )
        await redis_service.set_user_state(user_id, BOT_STATES['WAITING_PLAN_NAME'])
    
    elif action == 'config_preview':
        await show_message_preview(query, context, bot_data)
    
    elif action == 'config_main':
        # Voltar ao menu principal de configuração
        await handle_bot_configuration(query, context)

async def show_message_preview(query, context, bot_data):
    """Mostra preview da mensagem de boas-vindas"""
    config = bot_data.get('config', {})
    
    # Criar preview
    preview_text = MESSAGES['full_preview'] + "\n\n"
    
    if config.get('welcome_message'):
        preview_text += config['welcome_message'] + "\n\n"
    else:
        preview_text += "_Nenhuma mensagem configurada_\n\n"
    
    if config.get('plans'):
        preview_text += "*Planos disponíveis:*\n"
        for plan in config['plans']:
            preview_text += f"• {plan['name']} - R$ {plan['price']:.2f}\n"
    else:
        preview_text += "_Nenhum plano configurado_\n"
    
    keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='config_message')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Se houver mídia configurada, tentar enviar
    if config.get('media_id') and config.get('media_type'):
        try:
            if config['media_type'] == 'photo':
                await query.message.reply_photo(
                    photo=config['media_id'],
                    caption=preview_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            elif config['media_type'] == 'video':
                await query.message.reply_video(
                    video=config['media_id'],
                    caption=preview_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            await query.message.delete()
            return
        except Exception:
            # Se falhar, mostrar apenas texto
            pass
    
    await query.edit_message_text(
        preview_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para adicionar canal/grupo"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = query.from_user.id
        bot_token = context.bot.token
        
        # Gerar código único
        code = generate_code()
        expiry = datetime.now() + timedelta(hours=1)
        
        # Salvar código no Redis
        await redis_service.save_channel_code(code, {
            'bot_token': bot_token,
            'user_id': user_id,
            'expiry': expiry.isoformat()
        })
        
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='config_channel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            MESSAGES['code_generated'].format(code=code),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        log_error(e, {'handler': 'handle_add_channel'})
        await query.edit_message_text(MESSAGES['error_generic'])

async def handle_channel_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para processar código de canal"""
    try:
        chat_id = update.effective_chat.id
        message_text = update.message.text.strip()
        
        # Verificar se é um código válido
        code_data = await redis_service.get_channel_code(message_text)
        if not code_data:
            return
        
        # Verificar se código não expirou
        expiry = datetime.fromisoformat(code_data['expiry'])
        if datetime.now() > expiry:
            await update.message.reply_text("❌ Código expirado.")
            return
        
        # Verificar se bot é admin no chat
        try:
            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            if bot_member.status not in ['administrator', 'creator']:
                await update.message.reply_text(
                    "❌ O bot precisa ser administrador neste grupo/canal."
                )
                return
        except Exception:
            await update.message.reply_text(
                "❌ Não foi possível verificar as permissões do bot."
            )
            return
        
        # Obter informações do chat
        chat = await context.bot.get_chat(chat_id)
        
        # Adicionar grupo/canal à configuração do bot
        bot_token = code_data['bot_token']
        bot_data = await redis_service.get_bot_data(bot_token)
        
        if bot_data:
            config = bot_data.get('config', {})
            linked_groups = config.get('linked_groups', [])
            
            # Verificar se grupo já está vinculado
            if any(group['id'] == chat_id for group in linked_groups):
                await update.message.reply_text(
                    "⚠️ Este grupo/canal já está vinculado."
                )
                return
            
            # Adicionar novo grupo
            linked_groups.append({
                'id': chat_id,
                'title': chat.title,
                'type': chat.type,
                'username': chat.username
            })
            
            config['linked_groups'] = linked_groups
            bot_data['config'] = config
            await redis_service.save_bot_data(bot_token, bot_data)
            
            await update.message.reply_text(
                f"✅ {chat.title} vinculado com sucesso!"
            )
            
            # Notificar o dono do bot
            try:
                await context.bot.send_message(
                    chat_id=code_data['user_id'],
                    text=f"✅ Grupo/Canal '{chat.title}' foi vinculado ao seu bot com sucesso!"
                )
            except Exception:
                pass
        
        # Remover código usado
        await redis_service.delete_channel_code(message_text)
        
    except Exception as e:
        log_error(e, {'handler': 'handle_channel_code'})
        if update.message:
            await update.message.reply_text("❌ Erro ao processar código.")