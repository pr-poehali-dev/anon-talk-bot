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
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

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

def get_or_create_user(user_id: int, username: str) -> None:
    """Get or create VK user (use negative ID to distinguish from Telegram)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    vk_db_id = -abs(user_id)
    
    cursor.execute('''
        INSERT INTO users (telegram_id, username, gender, is_searching, is_in_chat)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (telegram_id) DO NOTHING
    ''', (vk_db_id, username, 'not_set', False, False))
    
    conn.commit()
    cursor.close()
    conn.close()

def get_user(user_id: int) -> Optional[Dict]:
    """Get VK user"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    vk_db_id = -abs(user_id)
    cursor.execute('SELECT * FROM users WHERE telegram_id = %s', (vk_db_id,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(user) if user else None

def update_user_gender(user_id: int, gender: str) -> None:
    """Update VK user gender"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    vk_db_id = -abs(user_id)
    cursor.execute('UPDATE users SET gender = %s WHERE telegram_id = %s', (gender, vk_db_id))
    
    conn.commit()
    cursor.close()
    conn.close()

def set_searching(user_id: int, searching: bool) -> None:
    """Set VK user searching status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    vk_db_id = -abs(user_id)
    cursor.execute('UPDATE users SET is_searching = %s WHERE telegram_id = %s', (searching, vk_db_id))
    
    conn.commit()
    cursor.close()
    conn.close()

def set_in_chat(user_id: int, in_chat: bool, chat_id: Optional[int] = None) -> None:
    """Set VK user in_chat status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    vk_db_id = -abs(user_id)
    cursor.execute('UPDATE users SET is_in_chat = %s, current_chat_id = %s WHERE telegram_id = %s', 
                   (in_chat, chat_id, vk_db_id))
    
    conn.commit()
    cursor.close()
    conn.close()

def create_chat(user1_id: int, user1_platform: str, user2_id: int, user2_platform: str) -> int:
    """Create chat between two users (cross-platform)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert to DB IDs
    user1_db_id = -abs(user1_id) if user1_platform == 'vk' else user1_id
    user2_db_id = -abs(user2_id) if user2_platform == 'vk' else user2_id
    
    cursor.execute('''
        INSERT INTO chats (user1_telegram_id, user2_telegram_id, is_active, user1_platform, user2_platform, 
                          user1_platform_id, user2_platform_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (user1_db_id, user2_db_id, True, user1_platform, user2_platform, str(user1_id), str(user2_id)))
    
    chat_id = cursor.fetchone()[0]
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return chat_id

def get_active_chat(user_id: int) -> Optional[Dict]:
    """Get active chat for VK user"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    vk_db_id = -abs(user_id)
    cursor.execute('''
        SELECT * FROM chats 
        WHERE (user1_telegram_id = %s OR user2_telegram_id = %s)
        AND is_active = true
    ''', (vk_db_id, vk_db_id))
    
    chat = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(chat) if chat else None

def end_chat(user_id: int) -> None:
    """End active chat for VK user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    vk_db_id = -abs(user_id)
    cursor.execute('''
        UPDATE chats SET is_active = false, ended_at = CURRENT_TIMESTAMP
        WHERE (user1_telegram_id = %s OR user2_telegram_id = %s)
        AND is_active = true
    ''', (vk_db_id, vk_db_id))
    
    conn.commit()
    cursor.close()
    conn.close()

def find_partner(user_id: int, gender_filter: Optional[str] = None) -> Optional[Dict]:
    """Find chat partner (cross-platform search)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    vk_db_id = -abs(user_id)
    
    if gender_filter:
        cursor.execute('''
            SELECT * FROM users 
            WHERE telegram_id != %s 
            AND is_searching = true 
            AND is_in_chat = false
            AND gender = %s
            ORDER BY RANDOM()
            LIMIT 1
        ''', (vk_db_id, gender_filter))
    else:
        cursor.execute('''
            SELECT * FROM users 
            WHERE telegram_id != %s
            AND is_searching = true 
            AND is_in_chat = false
            ORDER BY RANDOM()
            LIMIT 1
        ''', (vk_db_id,))
    
    partner = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(partner) if partner else None

def get_partner_from_chat(user_id: int) -> Optional[Dict]:
    """Get partner info from active chat"""
    chat = get_active_chat(user_id)
    if not chat:
        return None
    
    vk_db_id = -abs(user_id)
    partner_db_id = chat['user2_telegram_id'] if chat['user1_telegram_id'] == vk_db_id else chat['user1_telegram_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute('SELECT * FROM users WHERE telegram_id = %s', (partner_db_id,))
    partner = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return dict(partner) if partner else None

def send_to_partner(user_id: int, text: str) -> bool:
    """Send message to chat partner (cross-platform)"""
    partner = get_partner_from_chat(user_id)
    if not partner:
        return False
    
    partner_id = partner['telegram_id']
    
    # Partner is VK user (negative ID)
    if partner_id < 0:
        return send_message(abs(partner_id), text)
    # Partner is Telegram user (positive ID)
    else:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        response = requests.post(url, json={'chat_id': partner_id, 'text': text})
        return response.status_code == 200

def handle_start(user_id: int, username: str) -> None:
    """Handle start command"""
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
    set_searching(user_id, False)

def handle_search(user_id: int, gender_filter: Optional[str] = None) -> None:
    """Handle search for chat partner"""
    active_chat = get_active_chat(user_id)
    if active_chat:
        send_message(user_id, '⚠️ У тебя уже есть активный диалог. Сначала заверши его')
        return
    
    set_searching(user_id, True)
    partner = find_partner(user_id, gender_filter)
    
    if partner:
        set_searching(user_id, False)
        set_searching(abs(partner['telegram_id']), False)
        
        partner_platform = 'vk' if partner['telegram_id'] < 0 else 'telegram'
        partner_real_id = abs(partner['telegram_id'])
        
        chat_id = create_chat(user_id, 'vk', partner_real_id, partner_platform)
        
        set_in_chat(user_id, True, chat_id)
        set_in_chat(partner_real_id if partner_platform == 'vk' else partner['telegram_id'], True, chat_id)
        
        keyboard = {
            'buttons': [
                [
                    {'action': {'type': 'text', 'label': '🛑 Стоп'}},
                    {'action': {'type': 'text', 'label': '➡️ Далее'}}
                ]
            ]
        }
        
        platform_emoji = '📱 VK' if partner_platform == 'vk' else '✈️ Telegram'
        send_message(user_id, f'✅ Собеседник найден! ({platform_emoji})\n\nМожете начинать общение 💬', keyboard)
        send_to_partner(user_id, f'✅ Собеседник найден! (📱 VK)\n\nМожете начинать общение 💬')
    else:
        send_message(user_id, '🔍 Ищем собеседника...\n\nОжидайте подключения')

def handle_stop_chat(user_id: int) -> None:
    """Handle stop chat command"""
    chat = get_active_chat(user_id)
    if not chat:
        send_message(user_id, '⚠️ У тебя нет активного диалога')
        return
    
    send_message(user_id, '👋 Диалог завершен')
    send_to_partner(user_id, '👋 Собеседник завершил диалог')
    
    end_chat(user_id)
    
    partner = get_partner_from_chat(user_id)
    if partner:
        partner_id = abs(partner['telegram_id'])
        set_in_chat(partner_id, False, None)
    
    set_in_chat(user_id, False, None)
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

def handle_gender_search(user_id: int) -> None:
    """Handle gender-based search menu"""
    keyboard = {
        'one_time': True,
        'buttons': [
            [{'action': {'type': 'text', 'label': '👨 Найти мужчину'}}],
            [{'action': {'type': 'text', 'label': '👩 Найти женщину'}}],
            [{'action': {'type': 'text', 'label': '◀️ Назад'}}]
        ]
    }
    
    send_message(user_id, '🎯 Выбери пол собеседника:', keyboard)

def handle_message(user_id: int, username: str, text: str) -> None:
    """Handle incoming message"""
    user = get_user(user_id)
    
    if not user:
        handle_start(user_id, username)
        return
    
    if user['is_in_chat']:
        if text == '🛑 Стоп':
            handle_stop_chat(user_id)
        elif text == '➡️ Далее':
            handle_next_chat(user_id)
        else:
            send_to_partner(user_id, text)
        return
    
    if user['gender'] == 'not_set':
        if text == '👨 Мужской':
            update_user_gender(user_id, 'male')
            send_message(user_id, '✅ Пол установлен: Мужской')
            handle_start(user_id, username)
        elif text == '👩 Женский':
            update_user_gender(user_id, 'female')
            send_message(user_id, '✅ Пол установлен: Женский')
            handle_start(user_id, username)
        return
    
    if text in ['начать', 'start', '/start', 'Начать']:
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
    elif text == '👨 Найти мужчину':
        handle_search(user_id, 'male')
    elif text == '👩 Найти женщину':
        handle_search(user_id, 'female')
    else:
        send_message(user_id, '❓ Неизвестная команда. Используй меню')

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
            'body': '',
            'isBase64Encoded': False
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
        
        # Get username
        user_info = vk_api_call('users.get', {'user_ids': str(user_id)})
        username = f"{user_info[0]['first_name']} {user_info[0]['last_name']}" if user_info else 'User'
        
        handle_message(user_id, username, text)
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'ok',
        'isBase64Encoded': False
    }
