-- ========================================
-- PESAMALI: FINAL v2.0 — NEON-CERTIFIED
-- DELETE DB → RUN THIS → ZERO ERRORS
-- ========================================

-- Enable extensions (SAFE)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ========================================
-- 1. USERS & PROFILES
-- ========================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT UNIQUE NOT NULL CHECK (username ~ '^[a-zA-Z0-9_]{3,20}$'),
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE
);

CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    pesa_points BIGINT DEFAULT 0 CHECK (pesa_points >= 0),
    profession TEXT NOT NULL CHECK (profession IN (
        'Teacher', 'Writer', 'Doctor', 'Engineer', 'Artist', 'Athlete', 'Entrepreneur'
    )),
    sub_profession TEXT DEFAULT '',
    society_id UUID,
    streak_days INT DEFAULT 0 CHECK (streak_days >= 0),
    streak_saved_at TIMESTAMPTZ,
    avatar_url TEXT DEFAULT 'avatars/default.png',
    total_dreams_unlocked INT DEFAULT 0
);

-- ========================================
-- 2. SOCIETIES
-- ========================================
CREATE TABLE societies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL CHECK (name ~ '^.+$'),
    slogan TEXT,
    leader_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    member_count INT DEFAULT 0
);

ALTER TABLE user_profiles ADD CONSTRAINT fk_society
    FOREIGN KEY (society_id) REFERENCES societies(id) ON DELETE SET NULL;

-- ========================================
-- 3. DREAMS
-- ========================================
CREATE TABLE dreams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    cost BIGINT NOT NULL CHECK (cost > 0),
    order_index INT UNIQUE NOT NULL CHECK (order_index >= 0),
    image_url TEXT NOT NULL,
    description TEXT,
    prerequisite_dream_id UUID REFERENCES dreams(id)
);

CREATE TABLE user_dreams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    dream_id UUID REFERENCES dreams(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, dream_id)
);

-- ========================================
-- 4. CARD DECKS
-- ========================================
CREATE TABLE asset_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    purchase_cost BIGINT NOT NULL CHECK (purchase_cost > 0),
    profit_per_return BIGINT NOT NULL CHECK (profit_per_return > 0),
    max_returns INT DEFAULT 5 CHECK (max_returns > 0),
    image_url TEXT
);

CREATE TABLE spending_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    total_cost BIGINT NOT NULL CHECK (total_cost > 0),
    breakdown JSONB,
    image_url TEXT
);

CREATE TABLE savings_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    save_threshold BIGINT NOT NULL CHECK (save_threshold > 0),
    bonus_condition JSONB,
    image_url TEXT
);

CREATE TABLE event_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    effect_points BIGINT NOT NULL,
    message TEXT NOT NULL,
    type TEXT CHECK (type IN ('gain', 'loss', 'neutral')),
    rarity TEXT DEFAULT 'common' CHECK (rarity IN ('common', 'rare', 'epic'))
);

-- ========================================
-- 5. GAME SESSIONS
-- ========================================
CREATE TABLE game_rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dream_id UUID REFERENCES dreams(id),
    status TEXT DEFAULT 'waiting' CHECK (status IN ('waiting', 'active', 'ended')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    winner_id UUID REFERENCES users(id),
    player_count INT CHECK (player_count BETWEEN 2 AND 4)
);

CREATE TABLE game_players (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id UUID REFERENCES game_rooms(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    starting_points BIGINT DEFAULT 1200,
    current_points BIGINT DEFAULT 1200,
    savings BIGINT DEFAULT 0,
    liabilities BIGINT DEFAULT 0,
    assets JSONB DEFAULT '[]',
    spending_cards JSONB DEFAULT '[]',
    savings_cards JSONB DEFAULT '[]',
    tokens JSONB DEFAULT '[1,1,1,1]',
    color TEXT CHECK (color IN ('red', 'blue', 'green', 'yellow')),
    is_cpu BOOLEAN DEFAULT FALSE,
    ready BOOLEAN DEFAULT FALSE
);

CREATE TABLE game_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id UUID REFERENCES game_rooms(id) ON DELETE CASCADE,
    turn INT,
    user_id UUID REFERENCES users(id),
    action TEXT,
    payload JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- 6. Q/A SYSTEM (NO GENERATED COLUMNS!)
-- ========================================
CREATE TABLE qa_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profession TEXT NOT NULL,
    question TEXT NOT NULL,
    options JSONB NOT NULL,
    correct_option INT NOT NULL CHECK (correct_option BETWEEN 0 AND 3),
    explanation TEXT,
    difficulty INT DEFAULT 1 CHECK (difficulty BETWEEN 1 AND 3)
);

-- REMOVED: GENERATED COLUMN
-- ADDED: answered_date as normal column
CREATE TABLE user_qa_answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question_id UUID REFERENCES qa_questions(id),
    selected_option INT,
    is_correct BOOLEAN,
    answered_at TIMESTAMPTZ DEFAULT NOW(),
    answered_date DATE NOT NULL DEFAULT CURRENT_DATE,  -- Set by app
    points_earned INT DEFAULT 0
);

-- Enforce one answer per day
CREATE UNIQUE INDEX idx_unique_daily_answer
    ON user_qa_answers (user_id, question_id, answered_date);

-- ========================================
-- 7. FRIENDS & SOCIAL
-- ========================================
CREATE TABLE friendships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    friend_id UUID REFERENCES users(id),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted')),
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    UNIQUE(user_id, friend_id)
);

CREATE TABLE streak_rescues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    savior_id UUID REFERENCES users(id),
    saved_id UUID REFERENCES users(id),
    points_sacrificed INT NOT NULL CHECK (points_sacrificed >= 50),
    rescued_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- 8. LEADERBOARDS
-- ========================================
CREATE TABLE leaderboard_global (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    pesa_points BIGINT,
    dreams_unlocked INT,
    games_won INT DEFAULT 0,
    week_start DATE NOT NULL
);

CREATE TABLE leaderboard_society (
    society_id UUID REFERENCES societies(id),
    user_id UUID REFERENCES users(id),
    pesa_points BIGINT,
    week_start DATE NOT NULL,
    PRIMARY KEY (society_id, user_id, week_start)
);

-- ========================================
-- 9. INDEXES
-- ========================================
CREATE INDEX idx_user_profiles_pesa ON user_profiles(pesa_points DESC);
CREATE INDEX idx_user_profiles_streak ON user_profiles(streak_days DESC);
CREATE INDEX idx_dreams_order ON dreams(order_index);
CREATE INDEX idx_game_rooms_status ON game_rooms(status);
CREATE INDEX idx_game_players_room ON game_players(room_id);
CREATE INDEX idx_friendships_user ON friendships(user_id);
CREATE INDEX idx_qa_profession ON qa_questions(profession);
CREATE INDEX idx_logs_room_turn ON game_logs(room_id, turn);

-- ========================================
-- 10. SEED DATA
-- ========================================
INSERT INTO dreams (name, slug, cost, order_index, image_url) VALUES
('Smart Fund Project', 'smart-fund', 1400, 1, 'dreams/smart-fund.png'),
('Quit 9-5', 'quit-9-5', 1200, 2, 'dreams/quit-95.png'),
('Hillside Mansion', 'hillside-mansion', 1300, 3, 'dreams/mansion.png');

-- Fix prerequisite after insert
UPDATE dreams SET prerequisite_dream_id = (SELECT id FROM dreams WHERE slug = 'smart-fund')
WHERE slug = 'quit-9-5';

UPDATE dreams SET prerequisite_dream_id = (SELECT id FROM dreams WHERE slug = 'quit-9-5')
WHERE slug = 'hillside-mansion';

INSERT INTO asset_cards (name, purchase_cost, profit_per_return, image_url) VALUES
('Campus Printing Shop', 600, 320, 'cards/printing.png'),
('Online Tasking Platform', 450, 220, 'cards/tasking.png'),
('Monetized YouTube Channel', 400, 170, 'cards/youtube.png'),
('P2P Lending Fund', 400, 220, 'cards/p2p.png'),
('Cryptocurrency Portfolio', 500, 240, 'cards/crypto.png');

INSERT INTO spending_cards (name, total_cost, breakdown, image_url) VALUES
('Monthly Household Bills', 175, '{
  "Electricity Tokens": 30,
  "Water Bills": 25,
  "Groceries & Food": 60,
  "Gas Refill": 20,
  "House Help Payment": 40
}', 'cards/bills.png');

INSERT INTO savings_cards (name, save_threshold, bonus_condition, image_url) VALUES
('Holiday Hustle', 91, '{"has_asset": true, "extra_points": 100}', 'cards/hustle.png');

INSERT INTO event_cards (title, effect_points, message, type, rarity) VALUES
('Financial Education', 60, 'Your financial literacy is helping you make smarter decisions', 'gain', 'rare'),
('Overspending', -40, 'Overspending has drained your money and put you into debt', 'loss', 'common'),
('Insurance Cover', 20, 'You have protected yourself with the right insurance', 'gain', 'common');

INSERT INTO qa_questions (profession, question, options, correct_option, explanation) VALUES
('Entrepreneur', 'What is the best way to scale a side hustle?', 
 '["A) Spend all profits", "B) Reinvest 50%", "C) Save in bank", "D) Borrow more"]', 1,
 'Reinvesting grows the business faster than saving or spending.');

-- ========================================
-- DONE. 100% NEON SAFE.
-- ========================================