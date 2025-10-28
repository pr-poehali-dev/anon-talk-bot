CREATE INDEX idx_messages_photo_sent_at ON t_p14838969_anon_talk_bot.messages(sent_at) 
WHERE photo_url IS NOT NULL;