FROM node:20-slim AS builder

WORKDIR /app

ARG VITE_API_URL=http://localhost:8080/
ENV VITE_API_URL=$VITE_API_URL

COPY package.json package-lock.json* ./

RUN npm install --legacy-peer-deps

RUN ./node_modules/.bin/tsc --version && \
    ./node_modules/.bin/vite --version

COPY . .

RUN ./node_modules/.bin/tsc -b && ./node_modules/.bin/vite build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

