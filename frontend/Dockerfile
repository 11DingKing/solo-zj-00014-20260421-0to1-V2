FROM node:20-alpine AS builder

WORKDIR /app

RUN npm config set registry https://registry.npmmirror.com

COPY package.json ./

RUN npm install --no-fund --no-audit

COPY . .

RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

COPY --from=builder /app/build ./build

EXPOSE 3000

ENV PORT=3000
ENV HOST=0.0.0.0
ENV ORIGIN=http://localhost:3000

CMD ["node", "build/index.js"]
