# Stage 1

FROM node:20 AS frontend_builder

WORKDIR /app

ARG VITE_API_BASE_URL

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN npm run build 


# Stage 2

FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=frontend_builder /app/dist /usr/share/nginx/html

EXPOSE 3000
