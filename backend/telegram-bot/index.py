'''
Business: Telegram webhook handler for anonymous chat bot
Args: event with httpMethod, body; context with request_id
Returns: HTTP response with statusCode 200
'''

import json
import os
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
DATABASE_URL = os.environ.get('DATABASE_URL', '')
WEBHOOK_URL = 'https://functions.poehali.dev/757a89cf-4d2d-4573-ba6a-6bfd8aa98d9c'

def setup_webhook():
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook'
        response = requests.post(url, json={'url': WEBHOOK_URL})
        return response.status_code == 200
    except:
        return False

def send_message(chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> bool:
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    response = requests.post(url, json=data)
    return response.status_code == 200

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

def escape_sql(value: Any) -> str:
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float)):
        return str(value)
    return f"'{str(value).replace(chr(39), chr(39)+chr(39))}'"

def get_or_create_user(telegram_id: int, username: Optional[str] = None) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(f"SELECT * FROM users WHERE telegram_id = {telegram_id}")
    user = cursor.fetchone()
    
    if not user:
        username_sql = escape_sql(username)
        cursor.execute(
            f"INSERT INTO users (telegram_id, username, last_active) VALUES ({telegram_id}, {username_sql}, CURRENT_TIMESTAMP) RETURNING *"
        )
        user = cursor.fetchone()
    else:
        cursor.execute(f"UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE telegram_id = {telegram_id}")
    
    cursor.close()
    conn.close()
    return dict(user) if user else {}

def handle_start(chat_id: int, username: Optional[str]):
    user = get_or_create_user(chat_id, username)
    
    if user.get('is_blocked'):
        send_message(chat_id, '🚫 Вы заблокированы')
        return
    
    if not user.get('gender'):
        handle_set_gender(chat_id)
        return
    
    keyboard = {
        'keyboard': [
            [{'text': '🔍 Найти собеседника'}, {'text': '🎯 Найти по полу'}]
        ],
        'resize_keyboard': True
    }
    
    welcome_text = (
        '🎭 <b>Добро пожаловать в анонимный чат!</b>\n\n'
        'Здесь вы можете общаться с незнакомцами полностью анонимно.\n\n'
        '📋 <b>Команды:</b>\n'
        '🔍 Найти собеседника - случайный поиск\n'
        '🎯 Найти по полу - выбрать пол собеседника\n\n'
        '💬 <b>В диалоге:</b>\n'
        '/stop - завершить диалог\n'
        '/settings - настройки профиля'
    )
    
    send_message(chat_id, welcome_text, keyboard)

def handle_set_gender(chat_id: int):
    keyboard = {
        'keyboard': [
            [{'text': '👨 Мужской'}, {'text': '👩 Женский'}]
        ],
        'resize_keyboard': True
    }
    send_message(chat_id, '👤 Выберите ваш пол для начала:', keyboard)

def update_user_gender(telegram_id: int, gender: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    gender_sql = escape_sql(gender)
    cursor.execute(f"UPDATE users SET gender = {gender_sql} WHERE telegram_id = {telegram_id}")
    cursor.close()
    conn.close()

def handle_settings(chat_id: int):
    keyboard = {
        'keyboard': [
            [{'text': '🔄 Изменить пол'}],
            [{'text': '◀️ Назад'}]
        ],
        'resize_keyboard': True
    }
    send_message(chat_id, '⚙️ Настройки:', keyboard)

def find_partner(telegram_id: int, preferred_gender: Optional[str] = None) -> Optional[int]:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = f"SELECT telegram_id FROM users WHERE is_searching = TRUE AND telegram_id != {telegram_id} AND is_blocked = FALSE"
    
    if preferred_gender:
        gender_sql = escape_sql(preferred_gender)
        query += f" AND gender = {gender_sql}"
    
    query += " LIMIT 1"
    
    cursor.execute(query)
    partner = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return partner['telegram_id'] if partner else None

def create_chat(user1_id: int, user2_id: int) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"INSERT INTO chats (user1_telegram_id, user2_telegram_id) VALUES ({user1_id}, {user2_id}) RETURNING id")
    chat_id = cursor.fetchone()[0]
    
    cursor.execute(f"UPDATE users SET is_searching = FALSE, is_in_chat = TRUE, current_chat_id = {chat_id} WHERE telegram_id IN ({user1_id}, {user2_id})")
    
    cursor.close()
    conn.close()
    return chat_id

def handle_search(chat_id: int, preferred_gender: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(f"SELECT * FROM users WHERE telegram_id = {chat_id}")
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        conn.close()
        send_message(chat_id, '❌ Ошибка. Используйте /start')
        return
    
    if user['is_blocked']:
        cursor.close()
        conn.close()
        send_message(chat_id, '🚫 Вы заблокированы')
        return
    
    if user['is_in_chat']:
        cursor.close()
        conn.close()
        send_message(chat_id, '💬 Вы уже в диалоге')
        return
    
    if not user['gender']:
        cursor.close()
        conn.close()
        send_message(chat_id, '⚠️ Сначала укажите ваш пол')
        handle_set_gender(chat_id)
        return
    
    partner_id = find_partner(chat_id, preferred_gender)
    
    if partner_id:
        chat_db_id = create_chat(chat_id, partner_id)
        send_message(chat_id, '✅ Собеседник найден! Можете начинать общение')
        send_message(partner_id, '✅ Собеседник найден! Можете начинать общение')
    else:
        cursor.execute(f"UPDATE users SET is_searching = TRUE WHERE telegram_id = {chat_id}")
        search_text = '🔍 Ищем собеседника...'
        if preferred_gender:
            gender_text = '👨 мужского' if preferred_gender == 'male' else '👩 женского'
            search_text = f'🎯 Ищем собеседника {gender_text} пола...'
        send_message(chat_id, search_text)
    
    cursor.close()
    conn.close()

def handle_gender_search(chat_id: int):
    keyboard = {
        'keyboard': [
            [{'text': '👨 Искать мужчину'}, {'text': '👩 Искать женщину'}],
            [{'text': '◀️ Назад'}]
        ],
        'resize_keyboard': True
    }
    send_message(chat_id, '🎯 Выберите пол собеседника:', keyboard)

def handle_stop_chat(chat_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(f"SELECT * FROM users WHERE telegram_id = {chat_id}")
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        conn.close()
        return
    
    if user['is_searching']:
        cursor.execute(f"UPDATE users SET is_searching = FALSE WHERE telegram_id = {chat_id}")
        send_message(chat_id, '❌ Поиск остановлен')
    elif user['is_in_chat'] and user['current_chat_id']:
        cursor.execute(f"SELECT user1_telegram_id, user2_telegram_id FROM chats WHERE id = {user['current_chat_id']} AND is_active = TRUE")
        chat_data = cursor.fetchone()
        
        if chat_data:
            partner_id = chat_data['user2_telegram_id'] if chat_data['user1_telegram_id'] == chat_id else chat_data['user1_telegram_id']
            
            cursor.execute(f"UPDATE chats SET is_active = FALSE, ended_at = CURRENT_TIMESTAMP WHERE id = {user['current_chat_id']}")
            cursor.execute(f"UPDATE users SET is_in_chat = FALSE, current_chat_id = NULL WHERE telegram_id IN ({chat_id}, {partner_id})")
            
            send_message(chat_id, '👋 Диалог завершён')
            send_message(partner_id, '👋 Собеседник завершил диалог')
    else:
        send_message(chat_id, '⚠️ Вы не в диалоге')
    
    cursor.close()
    conn.close()

def handle_message(chat_id: int, text: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(f"SELECT * FROM users WHERE telegram_id = {chat_id}")
    user = cursor.fetchone()
    
    if not user or not user['is_in_chat'] or not user['current_chat_id']:
        cursor.close()
        conn.close()
        send_message(chat_id, '⚠️ Вы не в диалоге. Используйте "Найти собеседника"')
        return
    
    cursor.execute(f"SELECT user1_telegram_id, user2_telegram_id FROM chats WHERE id = {user['current_chat_id']} AND is_active = TRUE")
    chat_data = cursor.fetchone()
    
    if chat_data:
        partner_id = chat_data['user2_telegram_id'] if chat_data['user1_telegram_id'] == chat_id else chat_data['user1_telegram_id']
        
        cursor.execute(f"UPDATE chats SET message_count = message_count + 1 WHERE id = {user['current_chat_id']}")
        
        text_escaped = text.replace('<', '&lt;').replace('>', '&gt;')
        send_message(partner_id, f'💬 <b>Собеседник:</b>\n{text_escaped}')
    
    cursor.close()
    conn.close()

def handle_complaint(chat_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(f"SELECT * FROM users WHERE telegram_id = {chat_id}")
    user = cursor.fetchone()
    
    if not user or not user['is_in_chat'] or not user['current_chat_id']:
        cursor.close()
        conn.close()
        send_message(chat_id, '⚠️ Вы не в диалоге')
        return
    
    reason_sql = escape_sql('Жалоба от пользователя')
    cursor.execute(f"INSERT INTO complaints (chat_id, reporter_telegram_id, reason) VALUES ({user['current_chat_id']}, {chat_id}, {reason_sql})")
    
    send_message(chat_id, '✅ Жалоба отправлена администрации')
    
    cursor.close()
    conn.close()

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    if event.get('httpMethod') == 'OPTIONS':
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
    
    try:
        body = json.loads(event.get('body', '{}'))
        
        if 'message' not in body:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'ok': True})
            }
        
        message = body['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        username = message.get('from', {}).get('username')
        
        if text == '/start':
            setup_webhook()
            handle_start(chat_id, username)
        elif text == '/stop':
            handle_stop_chat(chat_id)
        elif text == '/settings':
            handle_settings(chat_id)
        elif text == '◀️ Назад':
            handle_start(chat_id, username)
        elif text == '🔄 Изменить пол':
            handle_set_gender(chat_id)
        elif text == '👨 Мужской':
            update_user_gender(chat_id, 'male')
            send_message(chat_id, '✅ Пол установлен: Мужской')
            handle_start(chat_id, username)
        elif text == '👩 Женский':
            update_user_gender(chat_id, 'female')
            send_message(chat_id, '✅ Пол установлен: Женский')
            handle_start(chat_id, username)
        elif text == '🔍 Найти собеседника':
            handle_search(chat_id)
        elif text == '🎯 Найти по полу':
            handle_gender_search(chat_id)
        elif text == '👨 Искать мужчину':
            handle_search(chat_id, 'male')
        elif text == '👩 Искать женщину':
            handle_search(chat_id, 'female')
        elif text == '❌ Завершить диалог':
            handle_stop_chat(chat_id)
        elif text == '⚠️ Пожаловаться':
            handle_complaint(chat_id)
        else:
            handle_message(chat_id, text)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'ok': True})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }