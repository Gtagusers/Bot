# Use an official Python image as base
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (if needed for your bot)
RUN apt-get update && apt-get install -y python3-venv python3-pip

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install Poetry (if you're using Poetry for dependency management)
RUN pip install --upgrade pip && pip install poetry==1.3.1

# Copy your project files into the container
COPY . /app/

# Install Python dependencies (using Poetry or pip)
RUN pip install discord
RUN pip install python-dotenv

# Set the command to run your bot
CMD ["python", "bot.py"]
