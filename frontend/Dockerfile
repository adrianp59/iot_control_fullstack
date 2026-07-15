# --- ЕТАП 1: Сглобяване на React приложението (използвайки Debian Node.js 20 Slim) ---
FROM node:20-slim AS builder
WORKDIR /app

# Копиране на конфигурационните файлове за зависимостите
COPY package*.json ./

# Чиста и сигурна инсталация на производствените зависимости
RUN npm ci

# Копиране на останалия сорс код на React
COPY . .

# Компилиране на проекта за продукция (генерира папка dist/)
RUN npm run build

# --- ЕТАП 2: Лек, сигурен и високопроизводителен сървър Caddy за продукция ---
FROM caddy:2-alpine

# Копиране на конфигурирания Caddyfile
COPY Caddyfile /etc/caddy/Caddyfile

# Копиране на компилираните статични активи от Етап 1 в директорията на Caddy
COPY --from=builder /app/dist /usr/share/caddy

# Излагане на порт 80 за вътрешната Docker мрежа на Traefik
EXPOSE 80

# Стартиране на Caddy сървъра
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
