-- Initialize database for Discord Bot
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table untuk menyimpan message history
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_type VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    server_name VARCHAR(255),
    server_id BIGINT,
    channel_name VARCHAR(255) NOT NULL,
    channel_id BIGINT NOT NULL,
    author_name VARCHAR(255) NOT NULL,
    author_id BIGINT NOT NULL,
    content TEXT,
    attachments JSONB DEFAULT '[]',
    embeds INTEGER DEFAULT 0,
    reactions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index untuk query performance
CREATE INDEX IF NOT EXISTS idx_messages_channel_id ON messages(channel_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_author_id ON messages(author_id);

-- Table untuk monitored channels
CREATE TABLE IF NOT EXISTS monitored_channels (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT UNIQUE NOT NULL,
    channel_name VARCHAR(255),
    server_id BIGINT,
    server_name VARCHAR(255),
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Table untuk client connections tracking
CREATE TABLE IF NOT EXISTS client_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_ip INET NOT NULL,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    disconnected_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_monitored_channels_active ON monitored_channels(is_active);
CREATE INDEX IF NOT EXISTS idx_client_connections_active ON client_connections(is_active);
