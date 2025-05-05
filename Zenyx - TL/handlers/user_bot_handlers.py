"""
Handlers para os bots criados pelos usuários
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config.config import Config, BOT_STATES
from utils.helpers import (
    is_valid_pushinpay_token,
    get_media_type,
    extract_media_id,
    parse_plan_input,
    log_user_action,
    log_error,
    replace_placeholders
)
from utils.templates import MESSAGES, BUTTONS
from services.redis_service import RedisService
from services.payment_service import PaymentService

logger = logging.getLogger(__name__)
redis_service = RedisService()
payment_service = PaymentService()

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para mensagens de texto nos bots dos usuários"""
    try:
        user_id = update.effective_user.id
        bot_token = context.bot.token
        text = update.message.text
        
        # Obter dados do bot
        bot_data = await redis_service.get_bot_data(bot_token)
        if not bot_data:
            return
        
        # Verificar estado do usuário
        user_state = await redis_service.get_user_state(user_id)
        
        # Se estiver esperando token PushinPay
        if user_state == BOT_STATES['WAITING_PUSHINPAY']:
            await handle_pushinpay_token(update, context, bot_data)
            return
        
        # Se estiver esperando mensagem de boas-vindas
        if user_state == BOT_STATES['WAITING_MESSAGE']:
            await handle_welcome_message(update, context, bot_data)
            return
        
        # Se estiver criando plano
        if user_state == BOT_STATES['WAITING_PLAN_NAME']:
            await handle_plan_creation(update, context, bot_data)
            return
        
        # Se for um código de vinculação de grupo
        if len(text) == 8 and text.isupper() and text.isalnum():
            await handle_channel_code(update, context)
            return
        
        # Mensagem normal - responder com mensagem de boas-vindas se configurada
        await send_welcome_message(update, context, bot_data)
        
    except Exception as e:
        log_error(e, {'handler': 'handle_text_message'})

async def handle_media_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para mensagens de mídia"""
    try:
        user_id = update.effective_user.id
        bot_token = context.bot.token
        
        # Verificar se está esperando mídia
        user_state = await redis_service.get_user_state(user_id)
        if user_state != BOT_STATES['WAITING_MEDIA']:
            return
        
        # Obter dados do bot
        bot_data = await redis_service.get_bot_data(bot_token)
        if not bot_data or bot_data.get('owner_id') != user_id:
            return
        
        # Extrair informações da mídia
        media_type = get_media_type(update.message)
        media_id = extract_media_id(update.message)
        
        if not media_type or not media_id:
            await update.message.reply_text(
                "❌ Tipo de mídia não suportado. Use apenas fotos ou vídeos."
            )
            return
        
        # Salvar mídia na configuração
        config = bot_data.get('config', {})
        config['media_type'] = media_type
        config['media_id'] = media_id
        bot_data['config'] = config
        
        await redis_service.save_bot_data(bot_token, bot_data)
        
        # Limpar estado
        await redis_service.clear_user_state(user_id)
        
        # Confirmar
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='config_message')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            MESSAGES['media_saved'],
            reply_markup=reply_markup
        )
        
    except Exception as e:
        log_error(e, {'handler': 'handle_media_message'})

async def handle_pushinpay_token(update: Update, context: ContextTypes.DEFAULT_TYPE, bot_data: Dict) -> None:
    """Handler para token PushinPay"""
    try:
        user_id = update.effective_user.id
        token = update.message.text.strip()
        
        # Validar formato do token
        if not is_valid_pushinpay_token(token):
            await update.message.reply_text(
                MESSAGES['pushinpay_invalid']
            )
            return
        
        # Salvar token na configuração
        config = bot_data.get('config', {})
        config['pushinpay_token'] = token
        bot_data['config'] = config
        
        await redis_service.save_bot_data(bot_data['token'], bot_data)
        
        # Limpar estado
        await redis_service.clear_user_state(user_id)
        
        # Confirmar
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='config_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            MESSAGES['pushinpay_configured'],
            reply_markup=reply_markup
        )
        
    except Exception as e:
        log_error(e, {'handler': 'handle_pushinpay_token'})

async def handle_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE, bot_data: Dict) -> None:
    """Handler para mensagem de boas-vindas"""
    try:
        user_id = update.effective_user.id
        text = update.message.text
        
        # Salvar mensagem na configuração
        config = bot_data.get('config', {})
        config['welcome_message'] = text
        bot_data['config'] = config
        
        await redis_service.save_bot_data(bot_data['token'], bot_data)
        
        # Limpar estado
        await redis_service.clear_user_state(user_id)
        
        # Confirmar
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='config_message')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            MESSAGES['text_saved'],
            reply_markup=reply_markup
        )
        
    except Exception as e:
        log_error(e, {'handler': 'handle_welcome_message'})

async def handle_plan_creation(update: Update, context: ContextTypes.DEFAULT_TYPE, bot_data: Dict) -> None:
    """Handler para criação de planos"""
    try:
        user_id = update.effective_user.id
        text = update.message.text
        
        # Parse do input do plano
        plan_data = parse_plan_input(text)
        
        if not plan_data:
            await update.message.reply_text(
                "❌ Formato inválido. Use: Nome do Plano | Valor | Duração\n"
                "Exemplo: Plano Mensal | 49.90 | 30 dias"
            )
            return
        
        # Adicionar plano à configuração
        config = bot_data.get('config', {})
        if 'plans' not in config:
            config['plans'] = []
        
        config['plans'].append(plan_data)
        bot_data['config'] = config
        
        await redis_service.save_bot_data(bot_data['token'], bot_data)
        
        # Limpar estado
        await redis_service.clear_user_state(user_id)
        
        # Confirmar
        keyboard = [[InlineKeyboardButton(BUTTONS['back'], callback_data='config_message')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            MESSAGES['plan_created'],
            reply_markup=reply_markup
        )
        
    except Exception as e:
        log_error(e, {'handler': 'handle_plan_creation'})

async def handle_channel_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para código de vinculação de canal"""
    try:
        chat_id = update.effective_chat.id
        code = update.message.text.strip()
        
        # Obter dados do código
        code_data = await redis_service.get_channel_code(code)
        if not code_data:
            return
        
        # Verificar se código não expirou
        from datetime import datetime
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
        await redis_service.delete_channel_code(code)
        
    except Exception as e:
        log_error(e, {'handler': 'handle_channel_code'})

async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE, bot_data: Dict) -> None:
    """Envia mensagem de boas-vindas configurada"""
    try:
        config = bot_data.get('config', {})
        user_data = {
            'id': update.effective_user.id,
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        }
        
        # Preparar mensagem
        welcome_text = config.get('welcome_message', '')
        if welcome_text:
            welcome_text = replace_placeholders(welcome_text, user_data)
        
        # Verificar se tem planos configurados
        plans = config.get('plans', [])
        if plans:
            # Criar botões para os planos
            keyboard = []
            for plan in plans:
                button_text = f"{plan['name']} - R$ {plan['price']:.2f}"
                callback_data = f"buy_plan_{plan['name']}_{plan['price']}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reply_markup = None
        
        # Enviar mensagem com mídia se configurada
        media_type = config.get('media_type')
        media_id = config.get('media_id')
        
        if media_type and media_id:
            try:
                if media_type == 'photo':
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=media_id,
                        caption=welcome_text,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                elif media_type == 'video':
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=media_id,
                        caption=welcome_text,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                else:
                    # Fallback para mensagem de texto
                    await update.message.reply_text(
                        text=welcome_text,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
            except Exception as e:
                # Se falhar ao enviar mídia, enviar apenas texto
                logger.error(f"Failed to send media: {e}")
                await update.message.reply_text(
                    text=welcome_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
        else:
            # Enviar apenas mensagem de texto
            if welcome_text:
                await update.message.reply_text(
                    text=welcome_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    "Bem-vindo! Configure a mensagem de boas-vindas no painel de administração.",
                    reply_markup=reply_markup
                )
    
    except Exception as e:
        log_error(e, {'handler': 'send_welcome_message'})
        await update.message.reply_text("Ocorreu um erro. Por favor, tente novamente.")

async def handle_plan_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para compra de planos"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Extrair informações do callback_data
        data_parts = query.data.split('_')
        if len(data_parts) < 4 or data_parts[0] != 'buy' or data_parts[1] != 'plan':
            await query.answer("Dados inválidos", show_alert=True)
            return
        
        plan_name = data_parts[2]
        plan_price = float(data_parts[3])
        
        # Obter dados do bot
        bot_token = context.bot.token
        bot_data = await redis_service.get_bot_data(bot_token)
        
        if not bot_data:
            await query.answer("Bot não encontrado", show_alert=True)
            return
        
        # Obter configuração de PushinPay
        config = bot_data.get('config', {})
        pushinpay_token = config.get('pushinpay_token')
        
        if not pushinpay_token:
            await query.edit_message_text(
                "❌ Este bot ainda não está configurado para receber pagamentos.\n"
                "Por favor, contate o administrador."
            )
            return
        
        # Criar um PaymentService com o token do usuário
        user_payment_service = PaymentService()
        user_payment_service.token = pushinpay_token
        user_payment_service.headers['Authorization'] = f'Bearer {pushinpay_token}'
        
        # Criar pagamento
        payment_result = await user_payment_service.create_pix_payment(plan_price)
        
        if not payment_result['success']:
            await query.edit_message_text(
                f"❌ Erro ao gerar pagamento: {payment_result.get('error', 'Erro desconhecido')}"
            )
            return
        
        # Extrair dados do pagamento
        payment_id = payment_result['payment_id']
        qr_code = payment_result['qr_code']
        qr_code_base64 = payment_result['qr_code_base64']
        
        # Salvar dados do pagamento para o usuário
        user_id = update.effective_user.id
        payment_data = {
            'payment_id': payment_id,
            'plan_name': plan_name,
            'plan_price': plan_price,
            'bot_token': bot_token,
            'user_id': user_id,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        await redis_service.save_payment_data(user_id, payment_data)
        
        # Decodificar imagem do QR Code
        qr_image = user_payment_service.decode_base64_to_image(qr_code_base64)
        
        if qr_image:
            # Enviar QR Code como imagem
            await query.message.reply_photo(
                photo=qr_image,
                caption=f"🔐 *Pagamento PIX*\n\n"
                       f"Plano: {plan_name}\n"
                       f"Valor: R$ {plan_price:.2f}\n\n"
                       f"Escaneie o QR Code ou copie o código abaixo:",
                parse_mode='Markdown'
            )
        else:
            # Se não conseguir decodificar, enviar só o texto
            await query.edit_message_text(
                f"🔐 *Pagamento PIX*\n\n"
                f"Plano: {plan_name}\n"
                f"Valor: R$ {plan_price:.2f}\n\n"
                f"Use o código PIX abaixo para pagamento:",
                parse_mode='Markdown'
            )
        
        # Enviar código PIX
        await query.message.reply_text(
            f"```\n{qr_code}\n```",
            parse_mode='Markdown'
        )
        
        # Botão para verificar pagamento
        keyboard = [[
            InlineKeyboardButton(
                "✅ Verificar Pagamento", 
                callback_data=f"check_payment_{payment_id}"
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "Após realizar o pagamento, clique no botão abaixo:",
            reply_markup=reply_markup
        )
        
        # Iniciar verificação automática em background
        asyncio.create_task(auto_check_payment(context, user_id, payment_id, bot_data))
        
    except Exception as e:
        log_error(e, {'handler': 'handle_plan_purchase'})
        await query.answer("Erro ao processar pagamento", show_alert=True)

async def check_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para verificar status do pagamento"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Extrair payment_id
        payment_id = query.data.split('_')[2]
        user_id = update.effective_user.id
        
        # Buscar dados do pagamento
        payment_data = await redis_service.get_payment_data(user_id, payment_id)
        
        if not payment_data:
            await query.answer("Pagamento não encontrado", show_alert=True)
            return
        
        # Obter token do bot para PushinPay
        bot_token = payment_data.get('bot_token')
        bot_data = await redis_service.get_bot_data(bot_token)
        config = bot_data.get('config', {})
        pushinpay_token = config.get('pushinpay_token')
        
        # Criar PaymentService com token do usuário
        user_payment_service = PaymentService()
        user_payment_service.token = pushinpay_token
        user_payment_service.headers['Authorization'] = f'Bearer {pushinpay_token}'
        
        # Verificar status
        result = await user_payment_service.check_payment_status(payment_id)
        
        if result['success'] and result['paid']:
            # Pagamento confirmado
            await process_successful_payment(update, context, payment_data, bot_data)
        else:
            await query.answer("Pagamento ainda não confirmado", show_alert=True)
    
    except Exception as e:
        log_error(e, {'handler': 'check_payment_status'})
        await query.answer("Erro ao verificar pagamento", show_alert=True)

async def auto_check_payment(context: ContextTypes.DEFAULT_TYPE, user_id: int, payment_id: str, bot_data: Dict) -> None:
    """Verifica automaticamente o status do pagamento em intervalos"""
    try:
        config = bot_data.get('config', {})
        pushinpay_token = config.get('pushinpay_token')
        
        # Criar PaymentService com token do usuário
        user_payment_service = PaymentService()
        user_payment_service.token = pushinpay_token
        user_payment_service.headers['Authorization'] = f'Bearer {pushinpay_token}'
        
        # Verificar por até 30 minutos
        max_attempts = 60  # 30 minutos (30 segundos * 60)
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            
            # Verificar status
            result = await user_payment_service.check_payment_status(payment_id)
            
            if result['success'] and result['paid']:
                # Pagamento confirmado
                payment_data = await redis_service.get_payment_data(user_id, payment_id)
                if payment_data:
                    # Criar um update fake para processar o pagamento
                    class FakeUpdate:
                        class effective_user:
                            id = user_id
                    
                    fake_update = FakeUpdate()
                    await process_successful_payment(fake_update, context, payment_data, bot_data)
                break
            
            # Aguardar 30 segundos antes da próxima verificação
            await asyncio.sleep(30)
    
    except Exception as e:
        log_error(e, {'function': 'auto_check_payment'})

async def process_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, payment_data: Dict, bot_data: Dict) -> None:
    """Processa um pagamento bem-sucedido"""
    try:
        user_id = update.effective_user.id
        plan_name = payment_data.get('plan_name')
        plan_price = payment_data.get('plan_price')
        
        # Atualizar status do pagamento
        payment_data['status'] = 'paid'
        payment_data['paid_at'] = datetime.now().isoformat()
        await redis_service.save_payment_data(user_id, payment_data['payment_id'])
        
        # Obter grupos vinculados
        config = bot_data.get('config', {})
        linked_groups = config.get('linked_groups', [])
        
        # Enviar confirmação ao usuário
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Pagamento confirmado!\n\n"
                 f"Plano: {plan_name}\n"
                 f"Valor: R$ {plan_price:.2f}\n\n"
                 f"Seu acesso aos grupos VIP foi liberado."
        )
        
        # Adicionar usuário aos grupos VIP
        for group in linked_groups:
            try:
                # Gerar link de convite
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=group['id'],
                    member_limit=1,
                    expire_date=int((datetime.now() + timedelta(days=1)).timestamp())
                )
                
                # Enviar link ao usuário
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🎉 Acesso ao grupo {group['title']}:\n{invite_link.invite_link}"
                )
            except Exception as e:
                logger.error(f"Failed to create invite link for group {group['id']}: {e}")
        
        # Registrar venda para o dono do bot
        owner_id = bot_data.get('owner_id')
        if owner_id:
            sale_data = {
                'user_id': user_id,
                'plan_name': plan_name,
                'amount': plan_price,
                'timestamp': datetime.now().isoformat()
            }
            await redis_service.add_user_sale(owner_id, sale_data)
            
            # Calcular e adicionar comissão
            commission = plan_price * Config.COMMISSION_RATE
            await redis_service.increment_user_stats(owner_id, 'balance', commission)
            
            # Notificar o dono do bot
            try:
                await context.bot.send_message(
                    chat_id=owner_id,
                    text=f"💰 Nova venda realizada!\n\n"
                         f"Plano: {plan_name}\n"
                         f"Valor: R$ {plan_price:.2f}\n"
                         f"Comissão: R$ {commission:.2f}"
                )
            except Exception:
                pass
    
    except Exception as e:
        log_error(e, {'handler': 'process_successful_payment'})