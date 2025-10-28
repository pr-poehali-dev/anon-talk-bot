'''
Business: Admin API for getting stats, active chats, complaints
Args: event with httpMethod, queryStringParameters; context with request_id
Returns: JSON with statistics, chats or complaints
'''

import json
import os
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def get_stats() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE last_active > NOW() - INTERVAL '1 hour'")
    active_users = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM chats WHERE is_active = TRUE")
    active_chats = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM users WHERE is_searching = TRUE")
    searching_users = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM complaints WHERE status = 'pending'")
    pending_complaints = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE gender = 'male') as male_count,
            COUNT(*) FILTER (WHERE gender = 'female') as female_count
        FROM users 
        WHERE last_active > NOW() - INTERVAL '24 hours'
    """)
    gender_stats = cursor.fetchone()
    
    cursor.execute("""
        SELECT 
            EXTRACT(HOUR FROM started_at) as hour,
            COUNT(*) as count
        FROM chats
        WHERE started_at > NOW() - INTERVAL '24 hours'
        GROUP BY EXTRACT(HOUR FROM started_at)
        ORDER BY hour
    """)
    hourly_stats = cursor.fetchall()
    
    cursor.execute("""
        SELECT 
            AVG(EXTRACT(EPOCH FROM (COALESCE(ended_at, NOW()) - started_at)) / 60) as avg_duration_minutes
        FROM chats
        WHERE started_at > NOW() - INTERVAL '24 hours'
    """)
    avg_duration = cursor.fetchone()['avg_duration_minutes'] or 0
    
    cursor.execute("""
        SELECT SUM(message_count) as total_messages
        FROM chats
        WHERE started_at > NOW() - INTERVAL '24 hours'
    """)
    total_messages = cursor.fetchone()['total_messages'] or 0
    
    cursor.close()
    conn.close()
    
    return {
        'active_users': active_users,
        'active_chats': active_chats,
        'searching_users': searching_users,
        'pending_complaints': pending_complaints,
        'gender_distribution': {
            'male': gender_stats['male_count'] or 0,
            'female': gender_stats['female_count'] or 0
        },
        'hourly_stats': [dict(row) for row in hourly_stats],
        'avg_chat_duration_minutes': round(float(avg_duration), 2),
        'total_messages_today': total_messages
    }

def get_active_chats() -> list:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            c.id,
            c.started_at,
            c.message_count,
            u1.gender as user1_gender,
            u2.gender as user2_gender,
            EXTRACT(EPOCH FROM (NOW() - c.started_at)) / 60 as duration_minutes
        FROM chats c
        JOIN users u1 ON c.user1_telegram_id = u1.telegram_id
        JOIN users u2 ON c.user2_telegram_id = u2.telegram_id
        WHERE c.is_active = TRUE
        ORDER BY c.started_at DESC
        LIMIT 50
    """)
    
    chats = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for chat in chats:
        duration_minutes = int(chat['duration_minutes'])
        hours = duration_minutes // 60
        minutes = duration_minutes % 60
        
        gender_label = f"{chat['user1_gender'][0].upper() if chat['user1_gender'] else '?'} ↔ {chat['user2_gender'][0].upper() if chat['user2_gender'] else '?'}"
        
        result.append({
            'id': f"CH-{str(chat['id']).zfill(3)}",
            'duration': f"{hours:02d}:{minutes:02d}",
            'gender': gender_label,
            'messages': chat['message_count'],
            'status': 'active'
        })
    
    return result

def get_complaints() -> list:
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            c.id,
            c.chat_id,
            c.reason,
            c.status,
            c.created_at
        FROM complaints c
        ORDER BY c.created_at DESC
        LIMIT 50
    """)
    
    complaints = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for complaint in complaints:
        result.append({
            'id': f"R-{str(complaint['id']).zfill(3)}",
            'chatId': f"CH-{str(complaint['chat_id']).zfill(3)}",
            'reason': complaint['reason'],
            'status': complaint['status'],
            'time': complaint['created_at'].strftime('%H:%M')
        })
    
    return result

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    try:
        params = event.get('queryStringParameters', {}) or {}
        endpoint = params.get('endpoint', 'stats')
        
        if endpoint == 'stats':
            data = get_stats()
        elif endpoint == 'chats':
            data = get_active_chats()
        elif endpoint == 'complaints':
            data = get_complaints()
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid endpoint'})
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(data),
            'isBase64Encoded': False
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
