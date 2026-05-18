FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --omit=dev 2>/dev/null || npm install --omit=dev

COPY src ./src
RUN mkdir -p uploads

ENV NODE_ENV=production
ENV PORT=3001
ENV ML_URL=http://ml:8000

EXPOSE 3001

CMD ["node", "src/server.js"]
