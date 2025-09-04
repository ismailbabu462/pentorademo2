FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Expose port
EXPOSE 3010

# Set port environment variable
ENV PORT=3010

# Start the application
CMD ["npm", "start"]