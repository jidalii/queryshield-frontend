# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py

   ```

## Database Schema

### 1. User

#### `user_role` Enum:
1. analyst
2. data_owner

#### `user` table:
| Column Name    | Column Type |
| -------- | ------- |
| uid  | SERIAL ->PK    |
| first_name | VARCHAR(50)     |
| last_name    | VARCHAR(50)    |
| role    | user_rol]   |


### 2. Analysis

#### `analysis_status` Enum:

1. Created
2. Ready
3. Running
4. Failed
5. Completed

#### `analysis` table

| Column Name    | Column Type |
| -------- | ------- |
| aid  | SERIAL ->PK |
| analysis_name | TEXT NOT NULL |
| analyst_id    |  INTEGER REFERENCES user(user_id) |
| time_created    | datetime DEFAULT NOW() |
| details    | JSONB NOT NULL  |
| owners_registered    | SERIAL[]   |
| status    | analysis_status NOT NULL |


