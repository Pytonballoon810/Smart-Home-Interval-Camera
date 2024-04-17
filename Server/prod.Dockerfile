FROM python:3.9-alpine

ARG PGID
ARG PUID

# Create a user and group with specified IDs
RUN addgroup -g $PGID mygroup && \
    adduser -u $PUID -G mygroup -h /app -D myuser

# Set the working directory
WORKDIR /app

# Set ownership of the working directory to the created user
RUN chown -R myuser:mygroup /app

# Install ffmpeg and other dependencies
RUN apk update && \
    apk add --no-cache ffmpeg && \
    apk add --no-cache build-base && \
    apk add --no-cache jpeg-dev zlib-dev libjpeg && \
    apk add --no-cache postgresql-dev gcc python3-dev musl-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Switch to the created user
USER myuser:mygroup

# Start the application
CMD ["python", "app.py"]