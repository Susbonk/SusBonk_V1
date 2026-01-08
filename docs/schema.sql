-- SusBonk Database Schema
-- PostgreSQL schema for user data, prompts, and chat configurations

-- Global user information
CREATE TABLE users (
    id BIGINT PRIMARY KEY,  -- Platform-specific user ID
    platform VARCHAR(20) NOT NULL DEFAULT 'telegram',  -- 'telegram', 'discord', etc.
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10),
    is_bot BOOLEAN DEFAULT false,
    is_premium BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(id, platform)
);

-- Core chat configuration
CREATE TABLE chats (
    id BIGINT PRIMARY KEY,  -- Platform-specific chat ID
    platform VARCHAR(20) NOT NULL DEFAULT 'telegram',  -- 'telegram', 'discord', etc.
    owner_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255),
    chat_type VARCHAR(50) NOT NULL,  -- 'group', 'supergroup', 'channel', 'guild', etc.
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- AI sensitivity controls
    prompts_threshold FLOAT DEFAULT 0.7 CHECK (prompts_threshold >= 0 AND prompts_threshold <= 1),
    custom_prompt_threshold FLOAT DEFAULT 0.7 CHECK (custom_prompt_threshold >= 0 AND custom_prompt_threshold <= 1),
    
    -- Heuristic spam filter toggles
    cleanup_mentions BOOLEAN DEFAULT true,
    cleanup_emojis BOOLEAN DEFAULT true,
    cleanup_links BOOLEAN DEFAULT true,
    
    -- Whitelisted domains (JSON array)
    allowed_link_domains JSONB DEFAULT '[]'::jsonb,
    
    UNIQUE(id, platform)
);

-- Pre-made AI prompts for spam detection
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    prompt_text TEXT NOT NULL,
    category VARCHAR(50),  -- 'spam', 'scam', 'crypto', 'nsfw', etc.
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User-created custom prompts
CREATE TABLE custom_prompts (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    prompt_text TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, name)
);

-- Link pre-made prompts to chats (many-to-many)
CREATE TABLE chat_prompts (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    prompt_id INTEGER NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    is_enabled BOOLEAN DEFAULT true,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(chat_id, prompt_id)
);

-- Link custom prompts to chats (many-to-many, though custom_prompts already has chat_id)
CREATE TABLE chat_custom_prompts (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    custom_prompt_id INTEGER NOT NULL REFERENCES custom_prompts(id) ON DELETE CASCADE,
    is_enabled BOOLEAN DEFAULT true,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(chat_id, custom_prompt_id)
);

-- User state tracking per chat
CREATE TABLE user_state (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chat_id BIGINT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    
    -- Trust and activity tracking
    is_trusted BOOLEAN DEFAULT false,
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP,
    
    -- Moderation tracking
    warning_count INTEGER DEFAULT 0,
    is_banned BOOLEAN DEFAULT false,
    banned_at TIMESTAMP,
    ban_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, chat_id)
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_platform ON users(platform);
CREATE INDEX idx_chats_owner ON chats(owner_id);
CREATE INDEX idx_chats_platform ON chats(platform);
CREATE INDEX idx_chats_active ON chats(is_active);
CREATE INDEX idx_prompts_category ON prompts(category);
CREATE INDEX idx_prompts_active ON prompts(is_active);
CREATE INDEX idx_custom_prompts_user ON custom_prompts(user_id);
CREATE INDEX idx_chat_prompts_chat ON chat_prompts(chat_id);
CREATE INDEX idx_user_state_chat ON user_state(chat_id);
CREATE INDEX idx_user_state_user ON user_state(user_id);
CREATE INDEX idx_user_state_trusted ON user_state(chat_id, is_trusted);

-- Insert some default prompts
INSERT INTO prompts (name, description, prompt_text, category) VALUES
('crypto_scam', 'Detects cryptocurrency scams and pump-and-dump schemes', 'Analyze this message for cryptocurrency scams, pump-and-dump schemes, fake investment opportunities, or suspicious financial promises. Look for urgency tactics, unrealistic returns, or pressure to invest quickly.', 'scam'),
('spam_links', 'Identifies spam messages with suspicious links', 'Check if this message contains spam links, phishing attempts, or suspicious URLs. Look for shortened links, suspicious domains, or messages that seem designed to trick users into clicking.', 'spam'),
('adult_content', 'Filters adult and NSFW content', 'Determine if this message contains adult content, sexual material, or NSFW content that would be inappropriate for a general audience.', 'nsfw'),
('harassment', 'Detects harassment and toxic behavior', 'Analyze this message for harassment, bullying, hate speech, or toxic behavior directed at individuals or groups.', 'harassment'),
('commercial_spam', 'Identifies commercial spam and unwanted promotions', 'Check if this message is commercial spam, unwanted advertising, or promotional content that disrupts normal conversation flow.', 'spam');
