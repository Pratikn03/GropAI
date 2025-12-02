FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm install || true
EXPOSE 3000
CMD ["npm","run","dev"]
