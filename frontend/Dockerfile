FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

# Clean install based on the lock file we generate
RUN npm install

COPY . .

CMD ["npm", "run", "dev"]