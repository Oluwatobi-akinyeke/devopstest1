# Frontend Dockerfile (frontend/Dockerfile)

# Stage 1: Build stage
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci  && \
    npm cache clean --force

# Copy all frontend source files
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production stage with nginx
FROM nginx:alpine

# Install necessary packages for runtime
RUN apk add --no-cache \
    curl \
    && rm -rf /var/cache/apk/*

# Create non-root user for nginx
RUN adduser -D -H -u 1000 -s /sbin/nologin appuser

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY --chown=appuser:appuser nginx.conf /etc/nginx/conf.d/default.conf

# Create nginx cache and pid directories with correct permissions
RUN mkdir -p /var/cache/nginx /var/run/nginx && \
    chown -R appuser:appuser /var/cache/nginx /var/run/nginx /usr/share/nginx/html && \
    touch /var/run/nginx.pid && \
    chown appuser:appuser /var/run/nginx.pid

# Switch to non-root user
USER appuser

# Expose port 3000 (as requested)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]