# Greenhouse Monitor

Полноценный локальный монорепозиторий для приёма, хранения и визуализации экспериментальных данных Arduino Mega 2560 + ESP8266 на Raspberry Pi 5.

## Архитектура

- Arduino/ESP8266 → `POST /api/v1/measurements` с `X-API-Key`.
- FastAPI валидирует пакет, сохраняет основную запись и 18 термопар одной транзакцией.
- PostgreSQL 16 хранит историю, JSON payload, устройства и эксперименты.
- React получает историю через REST и новые точки через WebSocket.
- Nginx раздаёт frontend и проксирует REST/WebSocket.
- Все даты хранятся timezone-aware; интерфейс показывает локальное время браузера.

## Запуск на Raspberry Pi

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin avahi-daemon
sudo usermod -aG docker "$USER"
# Перезайдите в систему

cp .env.example .env
nano .env
docker compose -f docker-compose.production.yml up -d --build
docker compose -f docker-compose.production.yml run --rm backend python -m app.cli create-admin
```

Откройте `http://raspberrypi.local` либо IP Raspberry Pi.

Обязательно замените `APP_SECRET_KEY`, `POSTGRES_PASSWORD`, `ADMIN_PASSWORD`.

## Development

```bash
cp .env.example .env
docker compose up --build
```

Frontend: `http://localhost:5173`  
Backend: `http://localhost:8000`  
OpenAPI: `http://localhost:8000/docs`

## Создание пользователя админа с данными из .env
'''bash
run file in docker apps/backend/app/cli.py
'''

## Создание устройства

Через страницу **Устройства** или API после входа:

```bash
curl -c cookies.txt -X POST http://raspberrypi.local/api/v1/auth/login   -H 'Content-Type: application/json'   -d '{"username":"admin","password":"your-password"}'

curl -b cookies.txt -X POST http://raspberrypi.local/api/v1/devices   -H 'Content-Type: application/json'   -d '{"device_id":"greenhouse-mega-01","name":"Основная Mega"}'
```

Полный API-ключ показывается только один раз.

## Пример POST от ESP8266

```bash
curl -X POST http://raspberrypi.local/api/v1/measurements   -H "Content-Type: application/json"   -H "X-API-Key: example-device-key"   -d @measurement.json
```

```json
{
  "device_id": "greenhouse-mega-01",
  "experiment_id": "experiment-001",
  "sample": 125,
  "timestamp": "2026-07-25T20:30:00+03:00",
  "uptime_ms": 380540,
  "thermocouples_c": [24.5, 24.75, 25.0, null],
  "lux": 183.33,
  "dht22": {"temperature_c": 24.6, "humidity_percent": 51.8},
  "bme680": {
    "temperature_c": 25.16,
    "humidity_percent": 49.82,
    "pressure_hpa": 1012.64,
    "gas_resistance_kohm": 74.53
  },
  "soil": {"raw": 650, "moisture_percent": 61}
}
```

Если `timestamp` отсутствует, используется серверное время. Повторный пакет с тем же `device + sample + experiment` возвращает существующую запись.

## Основные endpoints

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `POST /api/v1/measurements`
- `GET /api/v1/measurements`
- `GET /api/v1/measurements/latest`
- `GET /api/v1/measurements/{id}`
- `GET /api/v1/measurements/chart`
- `GET /api/v1/measurements/export.csv`
- `GET /api/v1/measurements/export.json`
- CRUD `/api/v1/devices`
- `POST /api/v1/devices/{id}/rotate-key`
- CRUD `/api/v1/experiments`
- `POST /api/v1/experiments/{id}/start`
- `POST /api/v1/experiments/{id}/finish`
- `GET /api/v1/system/status`
- `WS /api/v1/ws/measurements`

## Тестирование

```bash
cd apps/backend
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
ruff check app tests
mypy app

cd ../frontend
npm install
npm test -- --run
npm run typecheck
npm run build
```

## Backup / restore

```bash
set -a; . ./.env; set +a
./deploy/scripts/backup.sh
./deploy/scripts/restore.sh backups/greenhouse-YYYYMMDD-HHMMSS.sql.gz
```

## Обновление

```bash
git pull
docker compose -f docker-compose.production.yml up -d --build
docker image prune -f
```

## Диагностика

```bash
docker compose -f docker-compose.production.yml ps
docker compose -f docker-compose.production.yml logs -f --tail=200 backend
docker compose -f docker-compose.production.yml logs -f --tail=200 nginx
docker compose -f docker-compose.production.yml exec postgres pg_isready
```

Если ESP8266 не выполняет POST:

1. Проверьте общую сеть и доступность IP Raspberry Pi.
2. Используйте IP вместо `.local`, если в прошивке нет mDNS.
3. Проверьте `Content-Type`, `X-API-Key`, `device_id` и размер JSON.
4. `401` — неверный ключ; `413` — пакет слишком велик; `422` — ошибка данных; `503` — БД временно недоступна.
5. На ESP храните пакет на SD до подтверждённого ответа и повторяйте с exponential backoff.
