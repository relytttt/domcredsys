-- Domain Credit System - Database Schema
-- This schema is designed for Supabase/PostgreSQL

-- NOTE: This implementation uses plain-text passwords for simplicity.
-- For production use, passwords should be hashed using a secure algorithm
-- (e.g., bcrypt, argon2) before storage. The application code would need
-- to be updated accordingly to hash passwords on registration/login.

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL CHECK (length(code) = 4),
    password TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default admin user (code: 4757, password: 4757)
INSERT INTO users (code, password, is_admin) 
VALUES ('4757', '4757', TRUE)
ON CONFLICT (code) DO NOTHING;

-- 2. Stores table
CREATE TABLE IF NOT EXISTS stores (
    id SERIAL PRIMARY KEY,
    store_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. User-Store assignments (many-to-many relationship)
CREATE TABLE IF NOT EXISTS user_stores (
    id SERIAL PRIMARY KEY,
    user_code TEXT NOT NULL REFERENCES users(code) ON DELETE CASCADE,
    store_id TEXT NOT NULL REFERENCES stores(store_id) ON DELETE CASCADE,
    UNIQUE(user_code, store_id)
);

-- 4. Credits table (updated for item-based system)
CREATE TABLE IF NOT EXISTS credits (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    items TEXT NOT NULL,
    reason TEXT NOT NULL,
    date_of_issue DATE NOT NULL DEFAULT CURRENT_DATE,
    store_id TEXT NOT NULL REFERENCES stores(store_id),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'claimed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    claimed_at TIMESTAMP WITH TIME ZONE,
    claimed_by TEXT,
    created_by TEXT REFERENCES users(code)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_credits_store_id ON credits(store_id);
CREATE INDEX IF NOT EXISTS idx_credits_status ON credits(status);
CREATE INDEX IF NOT EXISTS idx_credits_code ON credits(code);
CREATE INDEX IF NOT EXISTS idx_user_stores_user_code ON user_stores(user_code);
CREATE INDEX IF NOT EXISTS idx_user_stores_store_id ON user_stores(store_id);
