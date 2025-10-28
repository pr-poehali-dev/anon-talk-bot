-- Добавляем уникальный индекс для пары platform + platform_id
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_platform_platform_id ON t_p14838969_anon_talk_bot.users(platform, platform_id);

-- Обновляем существующие записи: заполняем platform_id значением telegram_id для telegram пользователей
UPDATE t_p14838969_anon_talk_bot.users 
SET platform_id = CAST(telegram_id AS VARCHAR), 
    platform = 'telegram'
WHERE platform IS NULL OR platform_id IS NULL;