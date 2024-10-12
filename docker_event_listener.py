import docker
import logging
import queue
from threading import Thread

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Docker client
client = docker.from_env()

# Create a Queue
event_queue = queue.Queue()

# Function to listen for Docker events
def docker_event_listener():
    for event in client.events(decode=True):
        logging.info(f"Event received: {event}")
        event_queue.put(event)  # Add event to queue

# Function to process the queued events asynchronously
def process_event():
    while True:
        event = event_queue.get()  # Get event from the queue
        if event is None:
            break  # Stop if no more events
        # logging.info(f"Processing event: {event}")
        # Here you can add more processing logic based on event type
        event_queue.task_done()

# Create and start the listener thread
listener_thread = Thread(target=docker_event_listener)
listener_thread.start()

# Create and start the processor thread
processor_thread = Thread(target=process_event)
processor_thread.start()

# Wait for both threads to finish (in real-world app you would handle this differently)
listener_thread.join()
processor_thread.join()
