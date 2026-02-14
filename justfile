set dotenv-load

_load_local := "set -a; [ -f .env.local ] && . .env.local; set +a"
_load_env := "set -a; [ -f .env ] && . .env; set +a"
_load_example := "set -a; [ -f .env.example ] && . .env.example; set +a"

dev-backend:
    uv run python manage.py runserver

[working-directory: 'react-ui/src']
dev-frontend:
    npm i
    npm run dev --watch

dev:
    {{_load_local}}; \
    trap 'kill 0' SIGINT; \
    docker compose up -d mysql minio; \
    echo "Waiting for MySQL..."; \
    until docker compose exec mysql mysqladmin ping -h localhost -u root -ppassword --silent 2>/dev/null; do sleep 1; done; \
    echo "MySQL ready!"; \
    uv run python manage.py migrate; \
    uv run python manage.py runserver & \
    (cd react-ui && npm i && npm run dev --watch) & \
    wait

seed:
    {{_load_local}}; \
    uv run python manage.py seed

unseed:
    {{_load_local}}; \
    uv run python manage.py unseed

docker-deploy:
    if [ ! -f ".env" ]; then cp .env.example .env; fi
    cd react-ui && npm ci && npm run build
    docker compose up -d --build

docker-seed:
    docker compose exec samy python manage.py seed

docker-unseed:
    docker compose exec samy python manage.py unseed