from django.db import migrations


SQL = """
-- =========================
-- 0) Extensions
-- =========================
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =========================
-- 1) UUID defaults (server-side)
--    (If app sends id explicitly, Postgres will accept it)
-- =========================
ALTER TABLE users               ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE chats               ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE prompts             ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE custom_prompts      ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE chat_prompts        ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE chat_custom_prompts ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE user_states         ALTER COLUMN id SET DEFAULT gen_random_uuid();
ALTER TABLE runtime_statistics  ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- =========================
-- 2) created_at / updated_at defaults (server-side)
--    Important: this fixes your FastAPI inserts
-- =========================
ALTER TABLE users               ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE users               ALTER COLUMN updated_at SET DEFAULT now();

ALTER TABLE chats               ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE chats               ALTER COLUMN updated_at SET DEFAULT now();

ALTER TABLE prompts             ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE prompts             ALTER COLUMN updated_at SET DEFAULT now();

ALTER TABLE custom_prompts      ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE custom_prompts      ALTER COLUMN updated_at SET DEFAULT now();

ALTER TABLE chat_prompts        ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE chat_prompts        ALTER COLUMN updated_at SET DEFAULT now();

ALTER TABLE chat_custom_prompts ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE chat_custom_prompts ALTER COLUMN updated_at SET DEFAULT now();

ALTER TABLE user_states         ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE user_states         ALTER COLUMN updated_at SET DEFAULT now();

ALTER TABLE runtime_statistics  ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE runtime_statistics  ALTER COLUMN updated_at SET DEFAULT now();

-- =========================
-- 3) Backfill existing NULLs (in case any were created earlier)
-- =========================
UPDATE users               SET created_at = now() WHERE created_at IS NULL;
UPDATE users               SET updated_at = now() WHERE updated_at IS NULL;

UPDATE chats               SET created_at = now() WHERE created_at IS NULL;
UPDATE chats               SET updated_at = now() WHERE updated_at IS NULL;

UPDATE prompts             SET created_at = now() WHERE created_at IS NULL;
UPDATE prompts             SET updated_at = now() WHERE updated_at IS NULL;

UPDATE custom_prompts      SET created_at = now() WHERE created_at IS NULL;
UPDATE custom_prompts      SET updated_at = now() WHERE updated_at IS NULL;

UPDATE chat_prompts        SET created_at = now() WHERE created_at IS NULL;
UPDATE chat_prompts        SET updated_at = now() WHERE updated_at IS NULL;

UPDATE chat_custom_prompts SET created_at = now() WHERE created_at IS NULL;
UPDATE chat_custom_prompts SET updated_at = now() WHERE updated_at IS NULL;

UPDATE user_states         SET created_at = now() WHERE created_at IS NULL;
UPDATE user_states         SET updated_at = now() WHERE updated_at IS NULL;

UPDATE runtime_statistics  SET created_at = now() WHERE created_at IS NULL;
UPDATE runtime_statistics  SET updated_at = now() WHERE updated_at IS NULL;

-- =========================
-- 4) Trigger function: always bump updated_at on UPDATE
-- =========================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Replace triggers (idempotent)
DROP TRIGGER IF EXISTS trg_users_set_updated_at               ON users;
CREATE TRIGGER trg_users_set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_chats_set_updated_at               ON chats;
CREATE TRIGGER trg_chats_set_updated_at
BEFORE UPDATE ON chats
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_prompts_set_updated_at             ON prompts;
CREATE TRIGGER trg_prompts_set_updated_at
BEFORE UPDATE ON prompts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_custom_prompts_set_updated_at      ON custom_prompts;
CREATE TRIGGER trg_custom_prompts_set_updated_at
BEFORE UPDATE ON custom_prompts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_chat_prompts_set_updated_at        ON chat_prompts;
CREATE TRIGGER trg_chat_prompts_set_updated_at
BEFORE UPDATE ON chat_prompts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_chat_custom_prompts_set_updated_at ON chat_custom_prompts;
CREATE TRIGGER trg_chat_custom_prompts_set_updated_at
BEFORE UPDATE ON chat_custom_prompts
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_user_states_set_updated_at         ON user_states;
CREATE TRIGGER trg_user_states_set_updated_at
BEFORE UPDATE ON user_states
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_runtime_statistics_set_updated_at  ON runtime_statistics;
CREATE TRIGGER trg_runtime_statistics_set_updated_at
BEFORE UPDATE ON runtime_statistics
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
"""

REVERSE_SQL = """
-- Drop triggers
DROP TRIGGER IF EXISTS trg_users_set_updated_at               ON users;
DROP TRIGGER IF EXISTS trg_chats_set_updated_at               ON chats;
DROP TRIGGER IF EXISTS trg_prompts_set_updated_at             ON prompts;
DROP TRIGGER IF EXISTS trg_custom_prompts_set_updated_at      ON custom_prompts;
DROP TRIGGER IF EXISTS trg_chat_prompts_set_updated_at        ON chat_prompts;
DROP TRIGGER IF EXISTS trg_chat_custom_prompts_set_updated_at ON chat_custom_prompts;
DROP TRIGGER IF EXISTS trg_user_states_set_updated_at         ON user_states;
DROP TRIGGER IF EXISTS trg_runtime_statistics_set_updated_at  ON runtime_statistics;

-- Drop function
DROP FUNCTION IF EXISTS set_updated_at();

-- Drop timestamp defaults
ALTER TABLE users               ALTER COLUMN created_at DROP DEFAULT;
ALTER TABLE users               ALTER COLUMN updated_at DROP DEFAULT;

ALTER TABLE chats               ALTER COLUMN created_at DROP DEFAULT;
ALTER TABLE chats               ALTER COLUMN updated_at DROP DEFAULT;

ALTER TABLE prompts             ALTER COLUMN created_at DROP DEFAULT;
ALTER TABLE prompts             ALTER COLUMN updated_at DROP DEFAULT;

ALTER TABLE custom_prompts      ALTER COLUMN created_at DROP DEFAULT;
ALTER TABLE custom_prompts      ALTER COLUMN updated_at DROP DEFAULT;

ALTER TABLE chat_prompts        ALTER COLUMN created_at DROP DEFAULT;
ALTER TABLE chat_prompts        ALTER COLUMN updated_at DROP DEFAULT;

ALTER TABLE chat_custom_prompts ALTER COLUMN created_at DROP DEFAULT;
ALTER TABLE chat_custom_prompts ALTER COLUMN updated_at DROP DEFAULT;

ALTER TABLE user_states         ALTER COLUMN created_at DROP DEFAULT;
ALTER TABLE user_states         ALTER COLUMN updated_at DROP DEFAULT;

ALTER TABLE runtime_statistics  ALTER COLUMN created_at DROP DEFAULT;
ALTER TABLE runtime_statistics  ALTER COLUMN updated_at DROP DEFAULT;

-- Drop UUID defaults
ALTER TABLE users               ALTER COLUMN id DROP DEFAULT;
ALTER TABLE chats               ALTER COLUMN id DROP DEFAULT;
ALTER TABLE prompts             ALTER COLUMN id DROP DEFAULT;
ALTER TABLE custom_prompts      ALTER COLUMN id DROP DEFAULT;
ALTER TABLE chat_prompts        ALTER COLUMN id DROP DEFAULT;
ALTER TABLE chat_custom_prompts ALTER COLUMN id DROP DEFAULT;
ALTER TABLE user_states         ALTER COLUMN id DROP DEFAULT;
ALTER TABLE runtime_statistics  ALTER COLUMN id DROP DEFAULT;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_runtimestatistics_chat_messages_deleted"),
    ]

    operations = [
        migrations.RunSQL(SQL, REVERSE_SQL),
    ]
