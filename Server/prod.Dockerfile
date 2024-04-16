FROM python:3.9-slim

ARG PGID
ARG PUID

# Create a user and group with specified IDs
RUN addgroup --gid $PGID mygroup
RUN adduser --uid $PUID --ingroup mygroup --home /app --disabled-password --gecos "" myuser

# Set the working directory
WORKDIR /app

# Set ownership of the working directory to the created user
RUN chown -R myuser:mygroup /app

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Switch to the created user
USER myuser:mygroup

# Start the application
CMD ["python", "app.py"]
