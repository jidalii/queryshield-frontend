# Querysheild Implementation

## Table of Contents

- [Querysheild Implementation](#querysheild-implementation)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Tech Stack](#tech-stack)
  - [Functionalities](#functionalities)
  - [Get Started](#get-started)
    - [1) Configure environment variables](#1-configure-environment-variables)
    - [2-1) Deploy on Docker](#2-1-deploy-on-docker)
    - [2-2) Deploy on local](#2-2-deploy-on-local)
  - [File Structure](#file-structure)
  - [Database Schema](#database-schema)
    - [User](#user)
      - [`user_role` Enum](#user_role-enum)
      - [`user` table](#user-table)
    - [Analysis](#analysis)
      - [`analysis_status` Enum](#analysis_status-enum)
      - [`analysis` table](#analysis-table)
      - [`analysis_owners` table](#analysis_owners-table)

## Description

The repo is the frontend interface of Queryshield, a secure multiparty computation (MPC) cloud service. It leverages the power of cryptographic techniques to enable collaborative computation among multiple parties without compromising the privacy of their data.

## Tech Stack

- Frontend: Streamlit, Python
- Database: PostgreSQL
- Authentication: JWT library

## Functionalities

- **User Registration & Authentication**
  - Securely manage user registration and authentication with JWT-based token handling for enhanced security and session management.
- **Analyst Features**
  - Create Analysis Page: allows analysts to create new analyses with custom schemas, thread modes, and SQL queries.
  - Analysis History Page: allow analyst to trace his/her analysis status.
- **Data Owner Features**
  - Analysis Catalog Page: allows data owners to view all available analyses, providing an entry point for data sharing.
  - Share Data Page: allow data owner to do secret data sharing using MPC.
- Analysis Detail Page: wiew detailed metadata about specific analyses.


## Get Started

### 1) Configure environment variables

1. Create `.env` at the root:

    ```shell
    touch .env
    ```

2. Edit `.env` file with these variables:

    ```shell
    JWT_SECRET_KEY=secret
    DATABASE_URL=postgresql+psycopg2://user1:12345678!@host.docker.internal:5432/storage
    DATABASE_URL_VERIFICATION=postgresql+psycopg2://user1:12345678!@host.docker.internal:5432/verification
    POSTGRES_USER=user1
    POSTGRES_PASSWORD=12345678!
    POSTGRES_DB=storage
    POSTGRES_DB_VERIFICATION=verification
    ```

### 2-1) Deploy on Docker

The following instruction is for running the app on Docker, if you want to deploy on your local machine, you can go to [2-2) Deploy on Local](#2-2-deploy-on-local)

1. Start Docker.
2. Open a terminal and navigate to the [`scripts`](./scripts/) folder":

    ```shell
    cd scripts
    ```

3. Run the following commands:

    ```shell
    chmod +x start.sh
    ./start.sh
    ```

### 2-2) Deploy on local

You can also run the app on your local machine, rather than using Docker. The following is the instruction.

1. Create and activate a Python virtual environment:

    ```shell
    python -m venv venv
    source venv/bin/activate
    ```

2. Install all dependencies

    ```shell
    pip install -r requirements.txt
    ```

3. Compile the custom streamlit React component

    ```shell
    cd src/secret_share_component
    npm install
    npm run build
    ```

4. Run `python ./src/Create_Analysis.py`

    ```shell
    cd ../..
    python ./src/Create_Analysis.py
    ```

## File Structure

```shell
.
├── Dockerfile                   # Docker configuration file
├── LICENSE                      # License information
├── README.md                    # Project documentation
├── docker-compose.yml           # Docker Compose configuration
├── requirements.txt             # Python dependencies
├── setup.py                     # Python app setup file
├── scripts                      # Shell scripts
│   ├── cleanup.sh               # Script to remove the entire app from Docker
│   └── start.sh                 # Script to start/restart the app
├── sql                          # SQL scripts
│   ├── db_setup.sql             # Database setup script
│   └── db_storage_setup.sql     # Database storage setup script
├── secret_share_component/      # React.ts secret data sharing component
└── src                          # Source code
    ├── Create_Analysis.py       # Main app (entry point)
    ├── components/              # UI components
    ├── configs/                 # Configuration files
    ├── db/                      # Database connection and operations
    ├── models/                  # Data models
    ├── pages/                   # Application pages
    └── utils/                   # Utility functions
```

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
| email       | VARCHAR(50) |
| pin         | VARCHAR(50) |
| role        | user_role   |

### Analysis

#### `analysis_status` Enum

- Created
- Ready
- Running
- Failed
- Completed

#### `analysis` table

| Column Name       | Column Type                  |
| ----------------- | ---------------------------- |
| aid               | SERIAL ->PK                  |
| analysis_name     | TEXT NOT NULL                |
| analyst_id        | INTEGER REFERENCES user(uid) |
| time_created      | datetime DEFAULT NOW()       |
| details           | JSONB NOT NULL               |
| owners_registered | SERIAL[]                     |
| status            | analysis_status NOT NULL     |

#### `analysis_owners` table

| Column Name | Column Type                      |
| ----------- | -------------------------------- |
| analysis_id | INTEGER REFERENCES analysis(user_id) |
| user_id     | INTEGER REFERENCES user(aid) |
