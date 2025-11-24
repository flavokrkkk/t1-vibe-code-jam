FROM node:20-slim AS builder

WORKDIR /app

ARG VITE_API_URL=http://localhost:8080/
ENV VITE_API_URL=$VITE_API_URL

RUN npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm config set fetch-timeout 300000 && \
    npm config set registry https://registry.npmjs.org/ && \
    npm config set maxsockets 1

COPY package.json package-lock.json* ./

RUN npm install --legacy-peer-deps || \
    (sleep 5 && npm install --legacy-peer-deps) || \
    (sleep 10 && npm install --legacy-peer-deps)

RUN ./node_modules/.bin/tsc --version && \
    ./node_modules/.bin/vite --version

COPY . .

RUN ./node_modules/.bin/tsc -b && ./node_modules/.bin/vite build

FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

