# Docker Event Listener with Queue Processing

This project is a Python application that listens to Docker events in real-time, logs them, and processes them asynchronously using a queue.

## Features
- **Docker Event Listening**: The application listens for Docker events such as `start`, `stop`, `kill`, and `die`.
- **Queue Processing**: Events are added to a queue and processed asynchronously for more efficient handling.
- **Logging**: All events received from Docker are logged with details.

## Prerequisites
- Python 3.x
- Docker installed and running
- Python `docker` package
