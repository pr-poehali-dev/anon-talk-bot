-- Обновляем CHECK constraint для gender, чтобы разрешить 'not_set' для VK пользователей
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_gender_check;
ALTER TABLE users ADD CONSTRAINT users_gender_check CHECK (gender IN ('male', 'female', 'not_set'));