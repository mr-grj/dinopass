FROM node:20-alpine AS builder

ARG VITE_API_URL=http://localhost:8000/api
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ .

RUN npm run build


FROM node:20-alpine AS runtime

RUN addgroup -S ciphermoth && adduser -S ciphermoth -G ciphermoth

WORKDIR /app

RUN npm install -g serve

COPY --from=builder --chown=ciphermoth:ciphermoth /app/dist ./dist
COPY --from=builder /app/serve.json ./serve.json
COPY docker/frontend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER ciphermoth

EXPOSE 3000

CMD ["/app/entrypoint.sh"]
