# IoT Control Fullstack

Fullstack IoT climate control platform. Sensor devices (e.g. Arduino) publish temperature and humidity readings over secure MQTT. A Django backend stores the readings and exposes a REST API. A React dashboard shows live and historical data and lets you control an air conditioner.

## 🔗 Related Repositories

This repository contains the **Web & Cloud Infrastructure**. The hardware/embedded side can be found here:

- **Embedded Firmware:** [`iot_control_firmware`](https://github.com/adrianp59/iot_control_firmware) — C++ source code for the Arduino Uno R4 WiFi / ESP32 node managing IR emissions, BME280 sensor data, and local LCD display.

## Features

- **Secure MQTT Ingestion:** MQTTS on port 8883 via Eclipse Mosquitto running behind Traefik v3.
- **Django REST API:** Handles authentication (JWT), sensor telemetry, and climate control commands.
- **Background MQTT Worker:** Async worker (`manage.py mqtt_listen`) that consumes incoming sensor metrics and persists them to PostgreSQL.
- **AC Control Endpoints:** `/api/.../ac-control/` and `/ac-control/v2/` transform structured UI user intent into compact device payloads sent over MQTT.
- **React + Vite Dashboard:** Interactive UI built with Recharts, context-adaptive controls, time-range selectors, and JWT auto-refresh handling.
- **Automatic SSL/TLS:** Automatic HTTPS certificate issuance and renewal via Let's Encrypt through Traefik.
- **Containerized Architecture:** Fully orchestrated using Docker Compose with isolated public and private networks.

## Architecture

| Service | Tech | Purpose |
|---|---|---|
| `traefik` | Traefik v3 | Reverse proxy, edge router, TLS termination & MQTTS (8883) |
| `db` | PostgreSQL 15 | Relational data storage for telemetry and users |
| `redis` | Redis 7 | Caching and API rate limiting (throttling) |
| `mosquitto` | Eclipse Mosquitto 2.0 | Lightweight MQTT broker |
| `web` | Django 6 + Gunicorn | Core REST API, administration, and command translator |
| `mqtt_worker` | Django management command | Background listener for telemetry ingestion |
| `frontend` | React + Vite (served by Caddy) | Single Page Application (SPA) dashboard |

## Project Structure

```
.
├── django_app/      # Django backend (apps: auth, sensors, core)
├── frontend/        # React (Vite) frontend application
├── mosquitto/       # Mosquitto broker configuration, data, and logs
├── traefik/         # Traefik ACME certificate storage
├── docker-compose.yml
└── .env.example
```

## Prerequisites

- Docker and Docker Compose
- A public domain name pointing to your server IP (required for Let's Encrypt TLS)
- Open ports: `80` (HTTP), `443` (HTTPS), and `8883` (MQTTS)

## Setup & Deployment

1. **Clone the repository**

   ```bash
   git clone https://github.com/adrianp59/iot_control_fullstack.git
   cd iot_control_fullstack
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Fill in `.env` with your production settings:

   | Variable | Description |
   |---|---|
   | `DOMAIN` | Your public domain (e.g. `iot.example.com`) |
   | `SSL_EMAIL` | Email address for Let's Encrypt notifications |
   | `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL database credentials |
   | `DJANGO_SECRET_KEY` | Secret key for the Django application |
   | `MQTT_PASSWORD` | Password for the `django_backend` MQTT user |

3. **Configure Mosquitto authentication**

   Create the Mosquitto password file and register the `django_backend` user:

   ```bash
   docker run --rm -it -v $(pwd)/mosquitto/config:/mosquitto/config eclipse-mosquitto:2.0 \
     mosquitto_passwd -c /mosquitto/config/passwd django_backend
   ```

4. **Prepare ACME certificate storage**

   ```bash
   mkdir -p traefik/acme
   chmod 600 traefik/acme
   ```

5. **Build and start the container stack**

   ```bash
   docker compose -p iot-platform up -d --build
   ```

6. **Apply database migrations & create an admin user**

   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

7. **Access the application**

   Navigate to `https://<DOMAIN>`. The REST API is accessible under `/api`.

> **Note:** Traefik labels reference the Docker network `iot-platform_traefik-public`. Ensure you run Compose with the project name `iot-platform` (`docker compose -p iot-platform ...`) or update the network labels accordingly.

## Local Development (Without Docker)

### Backend Setup

```bash
cd django_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env   # Update with local settings (e.g., SQLite / local Redis)
python manage.py migrate
python manage.py runserver
```

In a separate terminal, start the MQTT listener worker:

```bash
python manage.py mqtt_listen
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## API Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/token/` | POST | Obtain JWT access and refresh tokens |
| `/api/token/refresh/` | POST | Refresh JWT access token |
| `/api/sensors/` | GET | List registered sensor nodes |
| `/api/readings/` | GET | Retrieve temperature telemetry (supports filtering) |
| `/api/humidity-readings/` | GET | Retrieve humidity telemetry (supports filtering) |
| `/api/ac-control/` | POST | Basic AC command endpoint |
| `/api/ac-control/v2/` | POST | Structured v2 AC control endpoint (with validation & status wait) |

## Useful Commands

```bash
# View live logs for web server and worker
docker compose logs -f web mqtt_worker

# Stop the entire stack
docker compose down

# Rebuild a single service (e.g. frontend)
docker compose up -d --build frontend
```

## License

This project is open-source software licensed under the MIT License.