# Use an official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y python3-venv python3-pip

# Create a virtual environment & activate it
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip & install Poetry
RUN pip install --upgrade pip && pip install poetry==1.3.1

# Copy project files into the container
COPY . /app/

# Install project dependencies using Poetry
RUN poetry install --no-dev --no-interaction --no-ansi

# Start the bot
CMD ["python", "bot.py"]
