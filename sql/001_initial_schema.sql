-- Project Heimdall Database Schema
-- Version: 1.0.0
-- Description: Core tables for chat session management

BEGIN;

-- ===================================================================
-- 0. Schema Migrations Table (for tracking applied migrations)
-- ===================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert this migration record
INSERT INTO schema_migrations (version, description) 
VALUES ('001', 'Initial database schema with chat sessions and messages')
ON CONFLICT (version) DO NOTHING;

-- ===================================================================
-- 1. Chat Sessions Table
-- ===================================================================

CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    system_prompt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster session lookup
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);

-- ===================================================================
-- 2. Chat Messages Table
-- ===================================================================

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created ON chat_messages(session_id, created_at DESC);

-- ===================================================================
-- 3. Add updated_at trigger for chat_sessions
-- ===================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_chat_sessions_updated_at 
    BEFORE UPDATE ON chat_sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- 4. Constraints and Foreign Keys
-- ===================================================================

-- Add foreign key constraint (optional, can be added later)
-- ALTER TABLE chat_messages 
-- ADD CONSTRAINT fk_chat_messages_session_id 
-- FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) 
-- ON DELETE CASCADE;

-- ===================================================================
-- 5. Comments
-- ===================================================================

COMMENT ON TABLE chat_sessions IS 'Stores chat session metadata including system prompts';
COMMENT ON TABLE chat_messages IS 'Stores individual chat messages with session context';
COMMENT ON COLUMN chat_sessions.session_id IS 'Unique identifier for the chat session';
COMMENT ON COLUMN chat_sessions.system_prompt IS 'System prompt for the session';
COMMENT ON COLUMN chat_messages.session_id IS 'Reference to the chat session';
COMMENT ON COLUMN chat_messages.role IS 'Message role (user, assistant, tool, system)';
COMMENT ON COLUMN chat_messages.content IS 'Message content in JSON format';

COMMIT;