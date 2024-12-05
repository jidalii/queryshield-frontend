# Queryshild Implementation

## Description

## Get Started



## Database Schema

### User

#### `user_role` Enum

- analyst
- data_owner

#### `user` table

| Column Name | Column Type |
| ----------- | ----------- |
| uid         | SERIAL ->PK |
| first_name  | VARCHAR(50) |
| last_name   | VARCHAR(50) |
| role        | user_role   |

### Analysis

#### `analysis_status` Enum

- Created
- Ready
- Running
- Failed
- Completed

#### `analysis` table

| Column Name       | Column Type                      |
| ----------------- | -------------------------------- |
| aid               | SERIAL ->PK                      |
| analysis_name     | TEXT NOT NULL                    |
| analyst_id        | INTEGER REFERENCES user(user_id) |
| time_created      | datetime DEFAULT NOW()           |
| details           | JSONB NOT NULL                   |
| owners_registered | SERIAL[]                         |
| status            | analysis_status NOT NULL         |
