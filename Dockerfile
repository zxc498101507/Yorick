# syntax=docker/dockerfile:1
# ---------- Stage 1: Build frontend ----------
FROM node:22-alpine AS builder
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Copy source code and build (if a build script exists)
COPY . ./
# If you have a build script, uncomment the next line:
# RUN npm run build

# ---------- Stage 2: Serve with Nginx ----------
FROM nginx:alpine
# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*
# Copy built files (or the whole src directory if no build step) from builder
COPY --from=builder /app/src/static /usr/share/nginx/html
# Optional: copy a custom nginx config if you have one
# COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# ---------- Optional Python environment (for tests or API) ----------
# If your project also needs a Python runtime, you can spin it up in a separate container
# using a similar multi‑stage approach, or add a python base image here and install
# the requirements from requirements.txt. The above image focuses on serving the
# static front‑end.
