FROM node:20-alpine AS base

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000
ENV PORT 3000
ENV NODE_ENV production
ENV HOSTNAME "0.0.0.0"

# next build with output:"standalone" copies server.js to .next/standalone/
CMD ["node", ".next/standalone/server.js"]
