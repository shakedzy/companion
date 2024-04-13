# Use Alpine Linux as base image
FROM python:3.12-alpine

# Install required packages
RUN apk update && \
    apk add --no-cache \
    ffmpeg \
    git \
    build-base 
# Clone the companion repository
RUN git clone https://github.com/shakedzy/companion.git /app

# Set the working directory
WORKDIR /app

RUN python -m venv venv \
    && source venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Define command to run your application
CMD ["venv/bin/python", "companion.py"]
