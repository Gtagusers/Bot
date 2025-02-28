# Use an official Python image as base
FROM python:3.9-slim

# Install Node.js (which includes npm)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs

# Set working directory inside the container
WORKDIR /app

# Install system dependencies for Python
RUN apt-get update && apt-get install -y python3-venv python3-pip

# Create a virtual environment & activate it
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip & install Poetry
RUN pip install --upgrade pip && pip install poetry==1.3.1

# Copy project files to the container
COPY . /app/

# Install Python dependencies using Poetry
RUN poetry install --no-dev --no-interaction --no-ansi

# Run the bot
CMD ["python", "bot.py"]
