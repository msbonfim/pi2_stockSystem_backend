# core/push_utils.py

import json
import platform
import requests
from urllib.parse import urlparse
from django.conf import settings
from .models import PushSubscription
import logging

logger = logging.getLogger(__name__)

# Tenta importar as bibliotecas necessárias
VAPID_AVAILABLE = False
WEBPUSH_AVAILABLE = False
try:
    from py_vapid import Vapid
    VAPID_AVAILABLE = True
except ImportError:
    logger.warning("Biblioteca 'py-vapid' não encontrada. Push notifications não funcionarão.")

try:
    from pywebpush import webpush
    WEBPUSH_AVAILABLE = True
except ImportError:
    logger.warning("Biblioteca 'pywebpush' não encontrada. Push notifications não funcionarão.")

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
    # Logs FORÇADOS com print() para aparecer sempre
    import sys
    print("\n" + "="*70, file=sys.stdout, flush=True)
    print(f"🚀 INICIANDO ENVIO DE PUSH NOTIFICATION", file=sys.stdout, flush=True)
    print(f"📝 Título: {title}", file=sys.stdout, flush=True)
    print(f"📝 Mensagem: {message}", file=sys.stdout, flush=True)
    print("="*70, file=sys.stdout, flush=True)
    
    logger.info("=" * 60)
    logger.info(f"🚀 INICIANDO ENVIO DE PUSH NOTIFICATION")
    logger.info(f"📝 Título: {title}")
    logger.info(f"📝 Mensagem: {message}")
    logger.info("=" * 60)
    
    subscriptions = PushSubscription.objects.filter(active=True)
    subscription_count = subscriptions.count()
    
    # Logs sempre visíveis, mesmo sem subscriptions
    import sys
    print(f"\n{'='*70}", file=sys.stdout, flush=True)
    print(f"🔔 PUSH NOTIFICATION: {title}", file=sys.stdout, flush=True)
    print(f"{'='*70}", file=sys.stdout, flush=True)
    print(f"📊 Subscriptions ativas: {subscription_count}", file=sys.stdout, flush=True)
    logger.info(f"🔍 Subscriptions ativas encontradas: {subscription_count}")
    
    if not subscriptions.exists():
        import sys
        msg = "❌ Nenhuma subscription ativa encontrada para envio de push notification"
        print(msg, file=sys.stdout, flush=True)
        logger.warning(msg)
        print("💡 SOLUÇÃO: No navegador, limpe Service Worker e permita notificações novamente", file=sys.stdout, flush=True)
        print(f"{'='*70}\n", file=sys.stdout, flush=True)
        return {"sent": 0, "failed": 0}
    
    if not VAPID_AVAILABLE or not WEBPUSH_AVAILABLE:
        import sys
        error_msg = "❌ Bibliotecas necessárias não instaladas. py-vapid: {}, pywebpush: {}".format(
            "OK" if VAPID_AVAILABLE else "FALTANDO",
            "OK" if WEBPUSH_AVAILABLE else "FALTANDO"
        )
        print(error_msg, file=sys.stdout, flush=True)
        logger.error(error_msg)
        return {"sent": 0, "failed": subscriptions.count(), "error": "Bibliotecas não instaladas"}

    vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
    vapid_claims_email = getattr(settings, 'VAPID_CLAIMS', {}).get("sub", "mailto:admin@example.com")
    
    logger.info(f"🔑 VAPID_PRIVATE_KEY configurada: {'Sim' if vapid_private_key else 'Não'}")
    logger.info(f"📧 VAPID_EMAIL: {vapid_claims_email}")

    # Inicializa o objeto Vapid
    logger.info("🔧 Inicializando objeto Vapid...")
    try:
        vapid = Vapid.from_pem(vapid_private_key.encode('utf-8'))
        logger.info("✅ Objeto Vapid inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Falha crítica ao carregar a VAPID_PRIVATE_KEY: {e}")
        return {"sent": 0, "failed": subscriptions.count(), "error": f"Chave VAPID inválida: {e}"}

    if not vapid_private_key or 'placeholder' in vapid_private_key or not vapid_private_key.strip().startswith('-----BEGIN'):
        error_message = "VAPID_PRIVATE_KEY não está configurada corretamente em settings.py. Deve ser uma string PEM."
        logger.error(f"❌ {error_message}")
        return {"sent": 0, "failed": subscriptions.count(), "error": error_message}

    sent = 0
    failed = 0
    
    # Payload que será enviado (será criptografado pelo pywebpush)
    payload = {
        "title": title,
        "message": message,  # Service Worker procura por 'message' ou 'body'
        "body": message,     # Também inclui 'body' para compatibilidade
        "icon": "/pwa-192x192.png",
        "badge": "/pwa-64x64.png",
        "data": data or {}
    }
    
    import sys
    print(f"📦 Payload criado: título='{title}', mensagem='{message[:50]}...'", file=sys.stdout, flush=True)
    logger.info(f"📦 Payload criado: título='{title}', mensagem='{message[:50]}...'")
    logger.info(f"🔄 Iniciando loop para {subscription_count} subscription(s)")

    for idx, subscription in enumerate(subscriptions, 1):
        import sys
        print(f"📤 [{idx}/{subscription_count}] Processando subscription {subscription.id}...", file=sys.stdout, flush=True)
        logger.info(f"📤 [{idx}/{subscription_count}] Processando subscription {subscription.id}...")
        
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth
            }
        }

        try:
            # Usa pywebpush para enviar (ele criptografa o payload automaticamente)
            # pywebpush precisa do VAPID_PRIVATE_KEY e VAPID_CLAIMS
            print(f"🔔 Enviando push para {subscription.endpoint[:50]}...", file=sys.stdout, flush=True)
            logger.info(f"🔔 Enviando push para {subscription.endpoint[:50]}...")
            
            # pywebpush.webpush() faz tudo: criptografia + headers VAPID + envio
            parsed_url = urlparse(subscription.endpoint)
            audience = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            response = webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims={
                    "sub": vapid_claims_email,
                    "aud": audience
                }
            )
            
            sent += 1
            print(f"✅ [{idx}/{subscription_count}] Push notification enviada com sucesso! Status: {response.status_code if hasattr(response, 'status_code') else 'OK'}", file=sys.stdout, flush=True)
            logger.info(f"✅ [{idx}/{subscription_count}] Push notification enviada com sucesso!")
            logger.info(f"   Endpoint: {subscription.endpoint[:50]}...")

        except Exception as e:
            failed += 1
            error_msg = str(e)
            import sys
            print(f"❌ [{idx}/{subscription_count}] Erro: {error_msg}", file=sys.stdout, flush=True)
            logger.error(f"❌ [{idx}/{subscription_count}] Erro ao enviar push notification")
            logger.error(f"   Erro completo: {error_msg}")
            logger.error(f"   Endpoint: {subscription.endpoint[:100]}")
            
            # Log detalhado do erro
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                logger.error(f"   Status Code: {status_code}")
                logger.error(f"   Erro: {error_msg}")
                
                # Tenta ler resposta do erro
                error_response = None
                try:
                    error_response = e.response.text[:200]
                    logger.error(f"   Resposta do servidor: {error_response}")
                except:
                    pass
                
                # 403 Forbidden geralmente indica chave VAPID incorreta ou subscription inválida
                if status_code == 403:
                    logger.error(f"   ⚠️ 403 Forbidden - Subscription inválida detectada!")
                    logger.error(f"   Motivo: {error_response if error_response else 'Chave VAPID não corresponde'}")
                    logger.error(f"   Endpoint completo: {subscription.endpoint[:150]}")
                    # Deleta subscription com 403 - está definitivamente inválida
                    subscription_id = subscription.id
                    subscription.delete()
                    logger.info(f"   🗑️ Subscription {subscription_id} DELETADA automaticamente")
                    logger.warning(f"   💡 Execute: python manage.py fix_push_notifications para diagnosticar")
                # 404 ou 410 = subscription não existe mais
                elif status_code in [404, 410]:
                    subscription.active = False
                    subscription.save()
                    logger.info(f"   🔄 Subscription {subscription.id} desativada pois não existe mais (status {status_code})")
            else:
                # Erro sem resposta HTTP (pode ser 403 mas sem response object)
                logger.error(f"   Erro de requisição (sem objeto response): {error_msg}")
                # Tenta extrair status code da mensagem de erro
                if "403" in error_msg or "Forbidden" in error_msg:
                    logger.error(f"   ⚠️ Detectado 403 Forbidden na mensagem de erro")
                    logger.error(f"   Motivo: Subscription criada com chave diferente da atual")
                    logger.error(f"   Endpoint completo: {subscription.endpoint[:150]}")
                    subscription_id = subscription.id
                    subscription.delete()
                    logger.info(f"   🗑️ Subscription {subscription_id} DELETADA automaticamente")
                    logger.warning(f"   💡 Execute: python manage.py fix_push_notifications para diagnosticar")
    
    # Logs finais sempre visíveis
    import sys
    print(f"\n{'='*70}", file=sys.stdout, flush=True)
    print(f"📊 RESULTADO: {sent} enviada(s), {failed} falha(s)", file=sys.stdout, flush=True)
    print(f"{'='*70}\n", file=sys.stdout, flush=True)
    logger.info("=" * 60)
    logger.info(f"📊 RESULTADO FINAL: {sent} enviada(s), {failed} falha(s)")
    logger.info("=" * 60)
    
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
