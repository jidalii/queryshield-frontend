-- Create ENUM type for user_role if it does not exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM (
            'analyst',
            'data_owner'
        );
    END IF;
END $$;

-- Create users table if it does not exist
CREATE TABLE IF NOT EXISTS users (
    uid serial PRIMARY KEY,
    first_name varchar(50) NOT NULL,
    last_name varchar(50) NOT NULL,
    email varchar(50) NOT NULL,
    pin varchar(50) NOT NULL,
    role user_role
);

-- Create ENUM type for analysis_status if it does not exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'analysis_status') THEN
        CREATE TYPE analysis_status AS ENUM (
            'Created',
            'Ready',
            'Running',
            'Failed',
            'Completed'
        );
    END IF;
END $$;

-- Create analysis table if it does not exist
CREATE TABLE IF NOT EXISTS analysis (
    aid serial PRIMARY KEY,
    analysis_name TEXT NOT NULL,
    analyst_id INT REFERENCES users(uid) ON DELETE CASCADE,
    time_created TIMESTAMP DEFAULT NOW(),
    details JSONB NOT NULL,
    status analysis_status
);

-- Create analysis_owners table if it does not exist
CREATE TABLE IF NOT EXISTS analysis_owners (
    analysis_id INT REFERENCES analysis(aid) ON DELETE CASCADE,
    user_id INT REFERENCES users(uid) ON DELETE CASCADE,
    PRIMARY KEY (analysis_id, user_id)
);
