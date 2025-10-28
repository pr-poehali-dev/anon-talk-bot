CREATE TABLE t_p14838969_anon_talk_bot.messages (
    id BIGSERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL REFERENCES t_p14838969_anon_talk_bot.chats(id),
    sender_telegram_id BIGINT NOT NULL REFERENCES t_p14838969_anon_talk_bot.users(telegram_id),
    content_type VARCHAR(20) NOT NULL DEFAULT 'text',
    photo_url TEXT NULL,
    text_content TEXT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_chat_id ON t_p14838969_anon_talk_bot.messages(chat_id);
CREATE INDEX idx_messages_photo_url ON t_p14838969_anon_talk_bot.messages(photo_url) WHERE photo_url IS NOT NULL;