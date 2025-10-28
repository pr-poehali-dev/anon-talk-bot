-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    gender VARCHAR(10) CHECK (gender IN ('male', 'female')),
    is_searching BOOLEAN DEFAULT FALSE,
    is_in_chat BOOLEAN DEFAULT FALSE,
    current_chat_id BIGINT,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица активных чатов
CREATE TABLE IF NOT EXISTS chats (
    id BIGSERIAL PRIMARY KEY,
    user1_telegram_id BIGINT NOT NULL,
    user2_telegram_id BIGINT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user1_telegram_id) REFERENCES users(telegram_id),
    FOREIGN KEY (user2_telegram_id) REFERENCES users(telegram_id)
);

-- Таблица жалоб
CREATE TABLE IF NOT EXISTS complaints (
    id BIGSERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    reporter_telegram_id BIGINT NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'resolved')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id),
    FOREIGN KEY (reporter_telegram_id) REFERENCES users(telegram_id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_searching ON users(is_searching) WHERE is_searching = TRUE;
CREATE INDEX IF NOT EXISTS idx_chats_active ON chats(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status) WHERE status = 'pending';
