# Cambia node:18-alpine por node:20-alpine o node:22-alpine
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./

# Instalación limpia
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]