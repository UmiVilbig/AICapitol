FROM oven/bun:latest

# Set the working directory in the container
WORKDIR /app

# Copy the files from the bg_info dir but ignore the node_modules dir
COPY . .

# Install dependencies
RUN bun install

# Copy the rest of the application code
COPY . .

# Run the start command
CMD ["bun", "start"]