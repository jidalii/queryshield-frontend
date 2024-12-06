FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Navigate to the frontend component and build it
WORKDIR /app/secret_share_component/template/secret_share_component/frontend
RUN npm install -g pnpm \
    && pnpm install \
    && pnpm run build

# Return to the application root directory
WORKDIR /app

# Install the project in editable mode
RUN pip install -e .

EXPOSE 8501

CMD ["python", "src/Create_Analysis.py", "--server.port=8501", "--server.enableCORS=true"]