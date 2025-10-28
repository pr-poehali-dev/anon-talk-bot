'''
Business: VK webhook handler for anonymous chat bot with cross-platform support
Args: event with httpMethod, body; context with request_id
Returns: HTTP response with statusCode 200
'''

import json
import os
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import random

GROUP_TOKEN = os.environ.get('VK_GROUP_TOKEN', '')
DATABASE_URL = os.environ.get('DATABASE_URL', '')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
VK_API_VERSION = '5.131'

def get_db_connection():
    """Get database connection with correct search_path"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SET search_path TO t_p14838969_anon_talk_bot, public")
    cursor.close()
    return conn

def vk_api_call(method: str, params: Dict[str, Any]) -> Optional[Dict]:
    """Call VK API method"""
    url = f'https://api.vk.com/method/{method}'
    params['access_token'] = GROUP_TOKEN
    params['v'] = VK_API_VERSION
    
    response = requests.post(url, data=params)
    result = response.json()
    
    if 'response' in result:
        return result['response']
    return None

def send_message(user_id: int, text: str, keyboard: Optional[Dict] = None) -> bool:
    """Send message to VK user"""
    params = {
        'user_id': user_id,
        'message': text,
        'random_id': random.randint(0, 2147483647)
    }
    
    if keyboard:
        params['keyboard'] = json.dumps(keyboard)
    
    result = vk_api_call('messages.send', params)
    return result is not None

def send_photo(user_id: int, photo_id: str, caption: Optional[str] = None) -> bool:
    """Send photo to VK user"""
    params = {
        'user_id': user_id,
        'attachment': photo_id,
        'random_id': random.randint(0, 2147483647)
    }
    
    if caption:
        params['message'] = caption
    
    result = vk_api_call('messages.send', params)
    return result is not None

def send_video(user_id: int, video_id: str, caption: Optional[str] = None) -> bool:
    """Send video to VK user"""
    params = {
        'user_id': user_id,
        'attachment': video_id,
        'random_id': random.randint(0, 2147483647)
    }
    
    if caption:
        params['message'] = caption
    
    result = vk_api_call('messages.send', params)
    return result is not None

def send_voice(user_id: int, voice_id: str) -> bool:
    """Send voice message to VK user"""
    params = {
        'user_id': user_id,
        'attachment': voice_id,
        'random_id': random.randint(0, 2147483647)
    }
    
    result = vk_api_call('messages.send', params)
    return result is not None

def send_document(user_id: int, doc_id: str, caption: Optional[str] = None) -> bool:
    """Send document to VK user"""
    params = {
        'user_id': user_id,
        'attachment': doc_id,
        'random_id': random.randint(0, 2147483647)
    }
    
    if caption:
        params['message'] = caption
    
    result = vk_api_call('messages.send', params)
    return result is not None

def get_or_create_user(user_id: int, username: str) -> None:
    """Get or create VK user in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (platform_id, platform, username, gender, status, is_searching)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (platform_id, platform) DO NOTHING
    ''', (str(user_id), 'vk', username, 'not_set', 'idle', False))
    
    conn.commit()
    cursor.close()
    conn.close()

def get_user(user_id: int) -> Optional[Dict]:
    """Get VK user from database"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute('SELECT * FROM users WHERE platform_id = %s AND platform = %s', (str(user_id), 'vk'))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(user) if user else None

def update_user_status(user_id: int, status: str) -> None:
    """Update VK user status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET status = %s WHERE platform_id = %s AND platform = %s', 
                   (status, str(user_id), 'vk'))
    
    conn.commit()
    cursor.close()
    conn.close()

def update_user_gender(user_id: int, gender: str) -> None:
    """Update VK user gender"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET gender = %s WHERE platform_id = %s AND platform = %s', 
                   (gender, str(user_id), 'vk'))
    
    conn.commit()
    cursor.close()
    conn.close()

def update_user_preference(user_id: int, preference: str) -> None:
    """Update VK user gender preference"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET gender_preference = %s WHERE platform_id = %s AND platform = %s', 
                   (preference, str(user_id), 'vk'))
    
    conn.commit()
    cursor.close()
    conn.close()

def set_searching(user_id: int, searching: bool) -> None:
    """Set VK user searching status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET is_searching = %s WHERE platform_id = %s AND platform = %s', 
                   (searching, str(user_id), 'vk'))
    
    conn.commit()
    cursor.close()
    conn.close()

def create_chat(user1_id: int, user2_id: int, user2_platform: str) -> int:
    """Create chat between two users (cross-platform)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chats (user1_platform_id, user1_platform, user2_platform_id, user2_platform, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    ''', (str(user1_id), 'vk', str(user2_id), user2_platform, 'active'))
    
    chat_id = cursor.fetchone()[0]
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return chat_id

def get_active_chat(user_id: int) -> Optional[Dict]:
    """Get active chat for VK user"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute('''
        SELECT * FROM chats 
        WHERE ((user1_platform_id = %s AND user1_platform = %s) 
               OR (user2_platform_id = %s AND user2_platform = %s))
        AND status = %s
    ''', (str(user_id), 'vk', str(user_id), 'vk', 'active'))
    
    chat = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(chat) if chat else None

def end_chat(user_id: int) -> None:
    """End active chat for VK user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE chats SET status = %s 
        WHERE ((user1_platform_id = %s AND user1_platform = %s) 
               OR (user2_platform_id = %s AND user2_platform = %s))
        AND status = %s
    ''', ('ended', str(user_id), 'vk', str(user_id), 'vk', 'active'))
    
    conn.commit()
    cursor.close()
    conn.close()

def find_partner(user_id: int, gender_filter: Optional[str] = None) -> Optional[Dict]:
    """Find chat partner (cross-platform search)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if gender_filter:
        cursor.execute('''
            SELECT * FROM users 
            WHERE platform_id != %s 
            AND is_searching = %s 
            AND status = %s
            AND gender = %s
            ORDER BY RANDOM()
            LIMIT 1
        ''', (str(user_id), True, 'idle', gender_filter))
    else:
        cursor.execute('''
            SELECT * FROM users 
            WHERE NOT (platform_id = %s AND platform = %s)
            AND is_searching = %s 
            AND status = %s
            ORDER BY RANDOM()
            LIMIT 1
        ''', (str(user_id), 'vk', True, 'idle'))
    
    partner = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(partner) if partner else None

def get_partner_info(user_id: int) -> Optional[Dict]:
    """Get partner info from active chat"""
    chat = get_active_chat(user_id)
    if not chat:
        return None
    
    partner_id = chat['user2_platform_id'] if chat['user1_platform_id'] == str(user_id) else chat['user1_platform_id']
    partner_platform = chat['user2_platform'] if chat['user1_platform_id'] == str(user_id) else chat['user1_platform']
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute('SELECT * FROM users WHERE platform_id = %s AND platform = %s', (partner_id, partner_platform))
    partner = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(partner) if partner else None

def send_to_partner(user_id: int, message_type: str, content: str, caption: Optional[str] = None) -> bool:
    """Send message to chat partner (cross-platform)"""
    partner = get_partner_info(user_id)
    if not partner:
        return False
    
    partner_id = int(partner['platform_id'])
    partner_platform = partner['platform']
    
    if partner_platform == 'vk':
        if message_type == 'text':
            return send_message(partner_id, content)
        elif message_type == 'photo':
            return send_photo(partner_id, content, caption)
        elif message_type == 'video':
            return send_video(partner_id, content, caption)
        elif message_type == 'voice':
            return send_voice(partner_id, content)
        elif message_type == 'document':
            return send_document(partner_id, content, caption)
    elif partner_platform == 'telegram':
        # Send to Telegram user via Telegram API
        if message_type == 'text':
            url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
            requests.post(url, json={'chat_id': partner_id, 'text': content})
        elif message_type == 'photo':
            url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto'
            requests.post(url, json={'chat_id': partner_id, 'photo': content, 'caption': caption})
        elif message_type == 'video':
            url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo'
            requests.post(url, json={'chat_id': partner_id, 'video': content, 'caption': caption})
        elif message_type == 'voice':
            url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVoice'
            requests.post(url, json={'chat_id': partner_id, 'voice': content})
        elif message_type == 'document':
            url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument'
            requests.post(url, json={'chat_id': partner_id, 'document': content, 'caption': caption})
        
        return True
    
    return False

def handle_start(user_id: int, username: str) -> None:
    """Handle /start command"""
    get_or_create_user(user_id, username)
    user = get_user(user_id)
    
    if not user:
        send_message(user_id, '❌ Ошибка при создании профиля')
        return
    
    if user['gender'] == 'not_set':
        keyboard = {
            'one_time': True,
            'buttons': [
                [{'action': {'type': 'text', 'label': '👨 Мужской'}}],
                [{'action': {'type': 'text', 'label': '👩 Женский'}}]
            ]
        }
        
        send_message(user_id, '👋 Привет! Это анонимный чат для общения.\n\n🔹 Выбери свой пол:', keyboard)
        update_user_status(user_id, 'setting_gender')
        return
    
    keyboard = {
        'buttons': [
            [
                {'action': {'type': 'text', 'label': '🔍 Найти собеседника'}},
                {'action': {'type': 'text', 'label': '🎯 Найти по полу'}}
            ],
            [{'action': {'type': 'text', 'label': '⚙️ Настройки'}}]
        ]
    }
    
    send_message(user_id, '🏠 Главное меню\n\n🌐 Ты можешь общаться с пользователями из VK и Telegram!', keyboard)
    update_user_status(user_id, 'idle')
    set_searching(user_id, False)

def handle_search(user_id: int, gender_filter: Optional[str] = None) -> None:
    """Handle search for chat partner"""
    active_chat = get_active_chat(user_id)
    if active_chat:
        send_message(user_id, '⚠️ У тебя уже есть активный диалог. Сначала заверши его командой "Стоп"')
        return
    
    set_searching(user_id, True)
    partner = find_partner(user_id, gender_filter)
    
    if partner:
        set_searching(user_id, False)
        set_searching(int(partner['platform_id']), False)
        
        create_chat(user_id, int(partner['platform_id']), partner['platform'])
        
        update_user_status(user_id, 'in_chat')
        update_user_status(int(partner['platform_id']), 'in_chat')
        
        keyboard = {
            'buttons': [
                [
                    {'action': {'type': 'text', 'label': '🛑 Стоп'}},
                    {'action': {'type': 'text', 'label': '➡️ Далее'}}
                ]
            ]
        }
        
        platform_emoji = '📱 VK' if partner['platform'] == 'vk' else '✈️ Telegram'
        send_message(user_id, f'✅ Собеседник найден! ({platform_emoji})\n\nМожете начинать общение 💬', keyboard)
        send_to_partner(user_id, 'text', f'✅ Собеседник найден! ({platform_emoji})\n\nМожете начинать общение 💬')
    else:
        send_message(user_id, '🔍 Ищем собеседника...\n\nОжидайте подключения')

def handle_stop_chat(user_id: int) -> None:
    """Handle stop chat command"""
    chat = get_active_chat(user_id)
    if not chat:
        send_message(user_id, '⚠️ У тебя нет активного диалога')
        return
    
    send_message(user_id, '👋 Диалог завершен')
    send_to_partner(user_id, 'text', '👋 Собеседник завершил диалог')
    
    end_chat(user_id)
    
    partner = get_partner_info(user_id)
    if partner:
        update_user_status(int(partner['platform_id']), 'idle')
    
    update_user_status(user_id, 'idle')
    handle_start(user_id, '')

def handle_next_chat(user_id: int) -> None:
    """Handle next chat command"""
    handle_stop_chat(user_id)
    handle_search(user_id)

def handle_settings(user_id: int) -> None:
    """Handle settings command"""
    keyboard = {
        'buttons': [
            [{'action': {'type': 'text', 'label': '🔄 Изменить пол'}}],
            [{'action': {'type': 'text', 'label': '◀️ Назад'}}]
        ]
    }
    
    send_message(user_id, '⚙️ Настройки:\n\n🔹 Выбери действие:', keyboard)

def handle_set_gender(user_id: int) -> None:
    """Handle set gender command"""
    keyboard = {
        'one_time': True,
        'buttons': [
            [{'action': {'type': 'text', 'label': '👨 Мужской'}}],
            [{'action': {'type': 'text', 'label': '👩 Женский'}}],
            [{'action': {'type': 'text', 'label': '◀️ Назад'}}]
        ]
    }
    
    send_message(user_id, '🔹 Выбери свой пол:', keyboard)
    update_user_status(user_id, 'setting_gender')

def handle_gender_search(user_id: int) -> None:
    """Handle gender-based search"""
    keyboard = {
        'one_time': True,
        'buttons': [
            [{'action': {'type': 'text', 'label': '👨 Мужской'}}],
            [{'action': {'type': 'text', 'label': '👩 Женский'}}],
            [{'action': {'type': 'text', 'label': '◀️ Назад'}}]
        ]
    }
    
    send_message(user_id, '🎯 Выбери пол собеседника:', keyboard)
    update_user_status(user_id, 'selecting_gender_preference')

def handle_message(user_id: int, username: str, text: str, attachments: list) -> None:
    """Handle incoming message"""
    user = get_user(user_id)
    
    if not user:
        handle_start(user_id, username)
        return
    
    if user['status'] == 'in_chat':
        if text == '🛑 Стоп':
            handle_stop_chat(user_id)
        elif text == '➡️ Далее':
            handle_next_chat(user_id)
        else:
            if attachments:
                for attachment in attachments:
                    att_type = attachment['type']
                    
                    if att_type == 'photo':
                        photo_id = f"photo{attachment['photo']['owner_id']}_{attachment['photo']['id']}"
                        send_to_partner(user_id, 'photo', photo_id, text if text else None)
                    elif att_type == 'video':
                        video_id = f"video{attachment['video']['owner_id']}_{attachment['video']['id']}"
                        send_to_partner(user_id, 'video', video_id, text if text else None)
                    elif att_type == 'audio_message':
                        voice_id = f"doc{attachment['audio_message']['owner_id']}_{attachment['audio_message']['id']}"
                        send_to_partner(user_id, 'voice', voice_id)
                    elif att_type == 'doc':
                        doc_id = f"doc{attachment['doc']['owner_id']}_{attachment['doc']['id']}"
                        send_to_partner(user_id, 'document', doc_id, text if text else None)
            
            if text and not attachments:
                send_to_partner(user_id, 'text', text)
        return
    
    if user['status'] == 'setting_gender':
        if text == '👨 Мужской':
            update_user_gender(user_id, 'male')
            send_message(user_id, '✅ Пол установлен: Мужской')
            handle_start(user_id, username)
        elif text == '👩 Женский':
            update_user_gender(user_id, 'female')
            send_message(user_id, '✅ Пол установлен: Женский')
            handle_start(user_id, username)
        return
    
    if user['status'] == 'selecting_gender_preference':
        if text == '👨 Мужской':
            update_user_preference(user_id, 'male')
            handle_search(user_id, 'male')
        elif text == '👩 Женский':
            update_user_preference(user_id, 'female')
            handle_search(user_id, 'female')
        elif text == '◀️ Назад':
            handle_start(user_id, username)
        return
    
    if text in ['начать', 'start', '/start']:
        handle_start(user_id, username)
    elif text == '⚙️ Настройки':
        handle_settings(user_id)
    elif text == '◀️ Назад':
        handle_start(user_id, username)
    elif text == '🔄 Изменить пол':
        handle_set_gender(user_id)
    elif text == '🔍 Найти собеседника':
        handle_search(user_id)
    elif text == '🎯 Найти по полу':
        handle_gender_search(user_id)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: VK webhook handler for anonymous chat bot
    Args: event - dict with httpMethod, body
    Returns: HTTP response dict with statusCode 200
    '''
    method = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    body = json.loads(event.get('body', '{}'))
    
    # VK Callback API confirmation
    if body.get('type') == 'confirmation':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': '436abbb5',
            'isBase64Encoded': False
        }
    
    # Handle message_new event
    if body.get('type') == 'message_new':
        message = body['object']['message']
        user_id = message['from_id']
        text = message.get('text', '')
        attachments = message.get('attachments', [])
        
        # Get username
        user_info = vk_api_call('users.get', {'user_ids': str(user_id)})
        username = f"{user_info[0]['first_name']} {user_info[0]['last_name']}" if user_info else 'User'
        
        handle_message(user_id, username, text, attachments)
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'ok',
        'isBase64Encoded': False
    }