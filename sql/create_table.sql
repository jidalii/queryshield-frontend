CREATE TYPE user_role AS ENUM (
    'analyst',
    'data_owner'
);

CREATE TABLE users (
    uid serial PRIMARY KEY,
    first_name varchar(50) NOT NULL,
    last_name varchar(50) NOT NULL,
    email varchar(50) NOT NULL,
    pin varchar(50) NOT NULL,
    role user_role
);

CREATE TYPE analysis_status AS ENUM (
    'Created',
    'Ready',
    'Running',
    'Failed',
    'Completed'
);

CREATE TABLE analysis (
    aid serial PRIMARY KEY,
    analysis_name TEXT NOT NULL,
    analyst_id INT REFERENCES users(uid) ON DELETE CASCADE,
    time_created TIMESTAMP DEFAULT NOW(),
    details JSONB NOT NULL,
    status analysis_status
);

CREATE TABLE analysis_owners (
    analysis_id INT REFERENCES analysis(aid) ON DELETE CASCADE,
    user_id INT REFERENCES users(uid) ON DELETE CASCADE,
    PRIMARY KEY (analysis_id, user_id)
);
