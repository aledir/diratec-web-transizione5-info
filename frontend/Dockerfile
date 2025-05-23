# Fase di build
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Imposta le variabili d'ambiente per la build
ARG NEXT_PUBLIC_CCAT_URL
ARG NEXT_PUBLIC_CCAT_WS_URL
ARG CCAT_API_KEY
# Assegna le variabili per la build
ENV NEXT_PUBLIC_CCAT_URL=${NEXT_PUBLIC_CCAT_URL}
ENV NEXT_PUBLIC_CCAT_WS_URL=${NEXT_PUBLIC_CCAT_WS_URL}
ENV CCAT_API_KEY=${CCAT_API_KEY}
# Correzione permessi e build
RUN chmod -R 755 ./node_modules/.bin
RUN chmod -R 755 ./node_modules/next/dist/bin
RUN npx --no-install next build
# Fase di runtime
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/next.config.ts ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]