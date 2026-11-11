# Frontend de Proyecto Aurora: build con Vite y servicio con Caddy (HTTPS automático y proxy de /api).
# La compilación corre en la arquitectura del runner ($BUILDPLATFORM): el resultado (HTML/JS/CSS) no depende de la
# arquitectura, y emular arm64 con QEMU hacía que npm ci tardara más de 40 minutos. Solo la imagen final es multi-arch.
FROM --platform=$BUILDPLATFORM public.ecr.aws/docker/library/node:22-alpine AS build
WORKDIR /src
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY index.html vite.config.ts tsconfig*.json postcss.config.js tailwind.config.js eslint.config.js ./
COPY src ./src
# Archivos estáticos sin procesar: theme-init.js (tema antes del primer render, sin script inline por la CSP) y favicon
COPY public ./public
# La API se sirve en el mismo dominio, bajo /api (sin CORS)
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM public.ecr.aws/docker/library/caddy:2.11-alpine
COPY deploy/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /src/dist /srv
EXPOSE 80 443
