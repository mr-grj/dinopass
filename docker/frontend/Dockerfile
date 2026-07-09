FROM node:20-alpine AS builder

ARG VITE_API_URL=http://localhost:8000/api
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ .

RUN npm run build


FROM node:20-alpine AS runtime

RUN addgroup -S dinopass && adduser -S dinopass -G dinopass

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/serve.json ./serve.json

USER dinopass

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000", "-c", "/app/serve.json"]
