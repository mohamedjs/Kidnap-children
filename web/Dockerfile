# Build the Vue app, serve the static files with Caddy (SPA fallback to index.html).
# The edge Caddy (deploy/Caddyfile) terminates HTTPS and routes /api to the api service.
FROM node:22-alpine AS build
WORKDIR /web
COPY package.json package-lock.json ./
RUN PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci --no-audit --no-fund
COPY . .
RUN npm run build

FROM caddy:2.10-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /web/dist /srv
EXPOSE 80
HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
