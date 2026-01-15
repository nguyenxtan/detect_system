FROM python:3.12-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Run the bot
CMD ["python", "bot.py"]
