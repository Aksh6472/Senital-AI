# ── Build Stage ──────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

# Install npm dependencies
COPY package*.json ./
RUN npm ci

# Copy code and build
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ── Runner Stage ─────────────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Copy build artifacts and dependencies
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start the Next.js production server
CMD ["npm", "start"]
