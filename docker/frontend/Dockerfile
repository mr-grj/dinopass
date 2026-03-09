FROM node:20-alpine AS builder

ARG REACT_APP_API_URL=http://localhost:8000/api
ENV REACT_APP_API_URL=$REACT_APP_API_URL

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci

COPY frontend/ .

RUN npm run build


FROM node:20-alpine AS runtime

RUN addgroup -S dinopass && adduser -S dinopass -G dinopass

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/build ./build

USER dinopass

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
