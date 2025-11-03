# core/push_utils.py

import json
import platform
import requests
from urllib.parse import urlparse
from django.conf import settings
from .models import PushSubscription
import logging

logger = logging.getLogger(__name__)

# Tenta importar a biblioteca VAPID
VAPID_AVAILABLE = False
try:
    from py_vapid import Vapid
    VAPID_AVAILABLE = True
except ImportError:
    logger.warning("Biblioteca 'py-vapid' não encontrada. Push notifications não funcionarão.")

# Tenta importar bibliotecas para notificações desktop
DESKTOP_NOTIFICATIONS_AVAILABLE = False
try:
    if platform.system() == 'Windows':
        from winotify import Notification, audio
        DESKTOP_NOTIFICATIONS_AVAILABLE = True
except ImportError:
    pass

def send_push_notification(title, message, data=None, user=None):
    """
    Envia uma notificação push para todas as subscriptions ativas (ou de um usuário específico)
    
    Args:
        title: Título da notificação
        message: Mensagem da notificação
        data: Dados adicionais (dict)
        user: Usuário específico (opcional, se None, envia para todos)
    """
    subscriptions = PushSubscription.objects.filter(active=True)
    if not subscriptions.exists():
        logger.info("Nenhuma subscription ativa encontrada para envio de push notification")
        return {"sent": 0, "failed": 0}
    
    if not VAPID_AVAILABLE:
        logger.error("py-vapid não está instalado. Não é possível enviar push notifications.")
        return {"sent": 0, "failed": subscriptions.count(), "error": "py-vapid não instalado"}

    vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
    vapid_claims_email = getattr(settings, 'VAPID_CLAIMS', {}).get("sub", "mailto:admin@example.com")

    # Inicializa o objeto Vapid
    try:
        vapid = Vapid.from_pem(vapid_private_key.encode('utf-8'))
    except Exception as e:
        logger.error(f"Falha crítica ao carregar a VAPID_PRIVATE_KEY: {e}")
        return {"sent": 0, "failed": subscriptions.count(), "error": f"Chave VAPID inválida: {e}"}

    if not vapid_private_key or 'placeholder' in vapid_private_key or not vapid_private_key.strip().startswith('-----BEGIN'):
        error_message = "VAPID_PRIVATE_KEY não está configurada corretamente em settings.py. Deve ser uma string PEM."
        logger.error(error_message)
        return {"sent": 0, "failed": subscriptions.count(), "error": error_message}

    sent = 0
    failed = 0
    payload = {
        "title": title,
        "body": message,
        "icon": "/pwa-192x192.png",  # Ícone da notificação
        "badge": "/pwa-64x64.png",
        "data": data or {}
    }

    for subscription in subscriptions:
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth
            }
        }

        try:
            # Gera os cabeçalhos VAPID para cada requisição
            # O método correto na biblioteca py_vapid é sign().
            # Ele espera um dicionário de claims que contenha 'sub' e 'aud'.
            parsed_url = urlparse(subscription_info["endpoint"])
            audience = f"{parsed_url.scheme}://{parsed_url.netloc}"
            claims = {
                "sub": vapid_claims_email,
                "aud": audience
            }
            vapid_headers = vapid.sign(claims, subscription_info["endpoint"])
            # Adiciona o cabeçalho TTL (Time-To-Live) manualmente, que é obrigatório.
            vapid_headers['TTL'] = '43200'  # 12 horas

            logger.debug(f"Enviando push para {subscription.endpoint[:50]}...")
            
            # Envia a requisição usando a biblioteca 'requests'
            response = requests.post(
                subscription_info["endpoint"],
                headers=vapid_headers,
                data=json.dumps(payload),
                timeout=10
            )
            
            response.raise_for_status()  # Lança um erro para status 4xx ou 5xx
            
            sent += 1
            logger.info(f"Push notification enviada com sucesso para {subscription.endpoint[:50]}...")

        except requests.exceptions.RequestException as e:
            failed += 1
            logger.error(f"Erro de requisição ao enviar push notification: {e}")
            if e.response and e.response.status_code in [404, 410]:
                subscription.active = False
                subscription.save()
                logger.info(f"Subscription desativada pois não existe mais (status {e.response.status_code})")
    
    return {"sent": sent, "failed": failed}

def send_desktop_notification(title, message, duration=10, urgency='normal'):
    """
    Envia uma notificação desktop do Windows que aparece no monitor.
    Funciona apenas no Windows 10/11.
    
    Args:
        title: Título da notificação
        message: Mensagem da notificação (máx 200 caracteres recomendado)
        duration: Duração em segundos que a notificação fica visível (padrão: 10) - não usado, Windows controla
        urgency: 'normal' ou 'critical' (critical usa som de alarme)
    
    Returns:
        dict: {"sent": bool, "error": str ou None}
    """
    if not DESKTOP_NOTIFICATIONS_AVAILABLE:
        logger.debug("Notificações desktop não disponíveis (não está no Windows ou winotify não instalado)")
        return {"sent": False, "error": "Não disponível"}
    
    if platform.system() != 'Windows':
        logger.debug(f"Notificações desktop só funcionam no Windows. Sistema atual: {platform.system()}")
        return {"sent": False, "error": "Apenas Windows"}
    
    try:
        from winotify import Notification, audio
        
        # Trunca mensagem muito longa (limite do Windows Toast é ~200 caracteres)
        if len(message) > 200:
            message = message[:197] + "..."
        
        # Cria a notificação
        toast = Notification(
            app_id="StockSystem",  # Nome do app
            title=title,
            msg=message,
            duration="long" if urgency == 'critical' else "short"
        )
        
        # Configura o som baseado na urgência
        if urgency == 'critical':
            # Som de alarme para alertas críticos (mais chamativo)
            toast.set_audio(audio.LoopingAlarm, loop=False)
        else:
            # Som padrão para notificações normais
            toast.set_audio(audio.Default, loop=False)
        
        # Adiciona um botão de ação (opcional)
        # toast.add_actions("Abrir Sistema", "http://localhost:8000")
        
        # Envia a notificação (ela aparece no canto inferior direito do Windows)
        toast.show()
        
        logger.info(f"Notificação desktop enviada: {title}")
        return {"sent": True, "error": None}
        
    except Exception as e:
        logger.error(f"Erro ao enviar notificação desktop: {e}")
        return {"sent": False, "error": str(e)}
