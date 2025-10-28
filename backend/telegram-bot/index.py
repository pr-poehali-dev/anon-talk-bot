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

def send_message(chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> bool:
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    response = requests.post(url, json=data)
    return response.status_code == 200

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def get_or_create_user(telegram_id: int, username: Optional[str] = None) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(
        "SELECT * FROM users WHERE telegram_id = %s",
        (telegram_id,)
    )
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            "INSERT INTO users (telegram_id, username, last_active) VALUES (%s, %s, CURRENT_TIMESTAMP) RETURNING *",
            (telegram_id, username)
        )
        user = cursor.fetchone()
        conn.commit()
    else:
        cursor.execute(
            "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE telegram_id = %s",
            (telegram_id,)
        )
        conn.commit()
    
    cursor.close()
    conn.close()
    return dict(user)

def handle_start(chat_id: int, username: Optional[str]):
    user = get_or_create_user(chat_id, username)
    
    if user.get('is_blocked'):
        send_message(chat_id, '🚫 Вы заблокированы')
        return
    
    keyboard = {
        'keyboard': [
            [{'text': '👤 Указать пол'}],
            [{'text': '🔍 Найти собеседника'}],
            [{'text': '❌ Завершить диалог'}],
            [{'text': '⚠️ Пожаловаться'}]
        ],
        'resize_keyboard': True
    }
    
    welcome_text = (
        '🎭 <b>Добро пожаловать в анонимный чат!</b>\n\n'
        'Здесь вы можете общаться с незнакомцами полностью анонимно.\n\n'
        '📋 <b>Команды:</b>\n'
        '👤 Указать пол - выбрать мужской/женский\n'
        '🔍 Найти собеседника - начать поиск\n'
        '❌ Завершить диалог - закончить текущий чат\n'
        '⚠️ Пожаловаться - отправить жалобу'
    )
    
    send_message(chat_id, welcome_text, keyboard)

def handle_set_gender(chat_id: int):
    keyboard = {
        'keyboard': [
            [{'text': '👨 Мужской'}, {'text': '👩 Женский'}],
            [{'text': '◀️ Назад'}]
        ],
        'resize_keyboard': True
    }
    send_message(chat_id, '👤 Выберите ваш пол:', keyboard)

def update_user_gender(telegram_id: int, gender: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET gender = %s WHERE telegram_id = %s",
        (gender, telegram_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def find_partner(telegram_id: int, preferred_gender: Optional[str] = None) -> Optional[int]:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT telegram_id FROM users 
        WHERE is_searching = TRUE 
        AND telegram_id != %s
        AND is_blocked = FALSE
    """
    params = [telegram_id]
    
    if preferred_gender:
        query += " AND gender = %s"
        params.append(preferred_gender)
    
    query += " LIMIT 1"
    
    cursor.execute(query, tuple(params))
    partner = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return partner['telegram_id'] if partner else None

def create_chat(user1_id: int, user2_id: int) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO chats (user1_telegram_id, user2_telegram_id) VALUES (%s, %s) RETURNING id",
        (user1_id, user2_id)
    )
    chat_id = cursor.fetchone()[0]
    
    cursor.execute(
        "UPDATE users SET is_searching = FALSE, is_in_chat = TRUE, current_chat_id = %s WHERE telegram_id IN (%s, %s)",
        (chat_id, user1_id, user2_id)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    return chat_id

def handle_search(chat_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (chat_id,))
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
    
    partner_id = find_partner(chat_id)
    
    if partner_id:
        chat_db_id = create_chat(chat_id, partner_id)
        send_message(chat_id, '✅ Собеседник найден! Можете начинать общение')
        send_message(partner_id, '✅ Собеседник найден! Можете начинать общение')
    else:
        cursor.execute(
            "UPDATE users SET is_searching = TRUE WHERE telegram_id = %s",
            (chat_id,)
        )
        conn.commit()
        send_message(chat_id, '🔍 Ищем собеседника...')
    
    cursor.close()
    conn.close()

def handle_stop_chat(chat_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (chat_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        conn.close()
        return
    
    if user['is_searching']:
        cursor.execute("UPDATE users SET is_searching = FALSE WHERE telegram_id = %s", (chat_id,))
        conn.commit()
        send_message(chat_id, '❌ Поиск остановлен')
    elif user['is_in_chat'] and user['current_chat_id']:
        cursor.execute(
            "SELECT user1_telegram_id, user2_telegram_id FROM chats WHERE id = %s AND is_active = TRUE",
            (user['current_chat_id'],)
        )
        chat_data = cursor.fetchone()
        
        if chat_data:
            partner_id = chat_data['user2_telegram_id'] if chat_data['user1_telegram_id'] == chat_id else chat_data['user1_telegram_id']
            
            cursor.execute(
                "UPDATE chats SET is_active = FALSE, ended_at = CURRENT_TIMESTAMP WHERE id = %s",
                (user['current_chat_id'],)
            )
            cursor.execute(
                "UPDATE users SET is_in_chat = FALSE, current_chat_id = NULL WHERE telegram_id IN (%s, %s)",
                (chat_id, partner_id)
            )
            conn.commit()
            
            send_message(chat_id, '👋 Диалог завершён')
            send_message(partner_id, '👋 Собеседник завершил диалог')
    else:
        send_message(chat_id, '⚠️ Вы не в диалоге')
    
    cursor.close()
    conn.close()

def handle_message(chat_id: int, text: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (chat_id,))
    user = cursor.fetchone()
    
    if not user or not user['is_in_chat'] or not user['current_chat_id']:
        cursor.close()
        conn.close()
        send_message(chat_id, '⚠️ Вы не в диалоге. Используйте "Найти собеседника"')
        return
    
    cursor.execute(
        "SELECT user1_telegram_id, user2_telegram_id FROM chats WHERE id = %s AND is_active = TRUE",
        (user['current_chat_id'],)
    )
    chat_data = cursor.fetchone()
    
    if chat_data:
        partner_id = chat_data['user2_telegram_id'] if chat_data['user1_telegram_id'] == chat_id else chat_data['user1_telegram_id']
        
        cursor.execute(
            "UPDATE chats SET message_count = message_count + 1 WHERE id = %s",
            (user['current_chat_id'],)
        )
        conn.commit()
        
        send_message(partner_id, f'💬 <b>Собеседник:</b>\n{text}')
    
    cursor.close()
    conn.close()

def handle_complaint(chat_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (chat_id,))
    user = cursor.fetchone()
    
    if not user or not user['is_in_chat'] or not user['current_chat_id']:
        cursor.close()
        conn.close()
        send_message(chat_id, '⚠️ Вы не в диалоге')
        return
    
    cursor.execute(
        "INSERT INTO complaints (chat_id, reporter_telegram_id, reason) VALUES (%s, %s, %s)",
        (user['current_chat_id'], chat_id, 'Жалоба от пользователя')
    )
    conn.commit()
    
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
        
        if text == '/start' or text == '◀️ Назад':
            handle_start(chat_id, username)
        elif text == '👤 Указать пол':
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
