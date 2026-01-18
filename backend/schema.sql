-- SusBonk Database Schema (UUID-based)
-- PostgreSQL schema aligned with Django admin panel
-- Migrated from BIGINT platform IDs to UUID primary keys

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- Internal user with platform-specific IDs as separate columns
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- User profile
    username VARCHAR(50),
    email VARCHAR(100),
    password_hash VARCHAR(255),
    
    -- Platform-specific user IDs (external identifiers)
    telegram_user_id BIGINT UNIQUE,
    discord_user_id BIGINT UNIQUE,
    
    -- Metadata (matches Django BaseModel)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- ============================================================================
-- CHATS TABLE
-- Chat configuration with platform type and platform-specific chat ID
-- Aligned with Senior backend (TGAntiSpamBot-V2)
-- ============================================================================
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Owner relationship
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Platform identification
    type VARCHAR(16) NOT NULL CHECK (type IN ('telegram', 'discord')),
    platform_chat_id BIGINT NOT NULL,
    
    -- Chat info
    title VARCHAR(255),
    chat_link VARCHAR(512),
    
    -- AI configuration
    enable_ai_check BOOLEAN DEFAULT false,
    prompts_threshold FLOAT DEFAULT 0.35 CHECK (prompts_threshold >= 0 AND prompts_threshold <= 1),
    custom_prompt_threshold FLOAT DEFAULT 0.35 CHECK (custom_prompt_threshold >= 0 AND custom_prompt_threshold <= 1),
    
    -- Cleanup settings (aligned with Senior backend)
    cleanup_mentions BOOLEAN DEFAULT false,
    allowed_mentions JSONB,  -- Added for Senior compatibility
    
    cleanup_emojis BOOLEAN DEFAULT false,
    max_emoji_count INTEGER DEFAULT 0,  -- Added for Senior compatibility
    
    cleanup_links BOOLEAN DEFAULT false,
    allowed_link_domains JSONB,
    
    cleanup_emails BOOLEAN DEFAULT false,  -- Added for Senior compatibility
    
    -- Statistics counters (Junior-specific, kept for backward compatibility)
    processed_messages INTEGER DEFAULT 0,
    spam_detected INTEGER DEFAULT 0,
    messages_deleted INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    -- Unique constraint: one chat per platform
    CONSTRAINT uk_chats_type_platform_chat_id UNIQUE (type, platform_chat_id)
);

-- ============================================================================
-- PROMPTS TABLE
-- Pre-made AI prompts for spam detection
-- ============================================================================
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100),
    prompt_text TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- ============================================================================
-- CUSTOM PROMPTS TABLE
-- User-created custom prompts
-- ============================================================================
CREATE TABLE custom_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100),
    prompt_text TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- ============================================================================
-- USER STATES TABLE
-- User state tracking per chat (note: plural table name for Django)
-- ============================================================================
CREATE TABLE user_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    
    -- External platform user ID (not FK - external identifier)
    external_user_id BIGINT NOT NULL,
    
    -- Trust and activity tracking
    trusted BOOLEAN DEFAULT false,
    joined_at TIMESTAMP,
    valid_messages INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- ============================================================================
-- CHAT PROMPTS TABLE
-- Many-to-many: Link pre-made prompts to chats
-- ============================================================================
CREATE TABLE chat_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    prompt_id UUID NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    priority INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT uk_chat_prompts_chat_id_prompt_id UNIQUE (chat_id, prompt_id)
);

-- ============================================================================
-- CHAT CUSTOM PROMPTS TABLE
-- Many-to-many: Link custom prompts to chats
-- ============================================================================
CREATE TABLE chat_custom_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    custom_prompt_id UUID NOT NULL REFERENCES custom_prompts(id) ON DELETE CASCADE,
    priority INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    CONSTRAINT uk_chat_custom_prompts_chat_id_custom_prompt_id UNIQUE (chat_id, custom_prompt_id)
);

-- ============================================================================
-- RUNTIME STATISTICS TABLE
-- System metrics tracking (NEW - from senior implementation)
-- ============================================================================
CREATE TABLE runtime_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE DEFAULT 'default_stats',
    
    messages_checked INTEGER DEFAULT 0,
    ai_requests_made INTEGER DEFAULT 0,
    messages_deleted INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_users_telegram ON users(telegram_user_id) WHERE telegram_user_id IS NOT NULL;
CREATE INDEX idx_users_discord ON users(discord_user_id) WHERE discord_user_id IS NOT NULL;
CREATE INDEX idx_users_active ON users(is_active);

CREATE INDEX idx_chats_user ON chats(user_id);
CREATE INDEX idx_chats_type ON chats(type);
CREATE INDEX idx_chats_active ON chats(is_active);

CREATE INDEX idx_prompts_active ON prompts(is_active);

CREATE INDEX idx_custom_prompts_user ON custom_prompts(user_id);

CREATE INDEX idx_user_states_chat_extuser ON user_states(chat_id, external_user_id);

CREATE INDEX idx_chat_prompts_chat ON chat_prompts(chat_id);
CREATE INDEX idx_chat_custom_prompts_chat ON chat_custom_prompts(chat_id);

-- ============================================================================
-- TRIGGER FUNCTION FOR updated_at
-- Auto-updates updated_at column on every UPDATE
-- ============================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS FOR ALL TABLES
-- ============================================================================
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_chats_updated_at
    BEFORE UPDATE ON chats
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_prompts_updated_at
    BEFORE UPDATE ON prompts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_custom_prompts_updated_at
    BEFORE UPDATE ON custom_prompts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_user_states_updated_at
    BEFORE UPDATE ON user_states
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_chat_prompts_updated_at
    BEFORE UPDATE ON chat_prompts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_chat_custom_prompts_updated_at
    BEFORE UPDATE ON chat_custom_prompts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_runtime_statistics_updated_at
    BEFORE UPDATE ON runtime_statistics
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================================
-- DEFAULT DATA
-- ============================================================================

-- Default prompts for spam detection
INSERT INTO prompts (name, prompt_text) VALUES
('crypto_scam', 'Analyze this message for cryptocurrency scams, pump-and-dump schemes, fake investment opportunities, or suspicious financial promises. Look for urgency tactics, unrealistic returns, or pressure to invest quickly.'),
('spam_links', 'Check if this message contains spam links, phishing attempts, or suspicious URLs. Look for shortened links, suspicious domains, or messages designed to trick users into clicking.'),
('adult_content', 'Determine if this message contains adult content, sexual material, or NSFW content that would be inappropriate for a general audience.'),
('harassment', 'Analyze this message for harassment, bullying, hate speech, or toxic behavior directed at individuals or groups.'),
('commercial_spam', 'Check if this message is commercial spam, unwanted advertising, or promotional content that disrupts normal conversation flow.');

-- Default runtime statistics entry
INSERT INTO runtime_statistics (name) VALUES ('default_stats');
