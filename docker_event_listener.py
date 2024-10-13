import docker
import logging
import threading
import queue

client = docker.from_env()
event_queue = queue.Queue()
logged_containers = {}

# Function to get container status dynamically
def get_container_status(container_name):
    try:
        container = client.containers.get(container_name)
        return container.status
    except docker.errors.NotFound:
        return 'Not found'


# Function to process Docker events and update container logs
def process_event():
    global logged_containers
    while True:
        event = event_queue.get()  # Get event from the queue
        if event is None:
            break  # Stop if no more events
        logging.info(f"Processing event: {event}")



        # Process event and log container details
        if 'Actor' in event:
            container_id = event['Actor']['ID']
            container_name = event['Actor']['Attributes'].get('name', 'unknown')
            status = event.get('status', 'unknown')

            # Update logged container statuses
            logged_containers[container_name] = status
        event_queue.task_done()


# Function to listen for Docker events and add them to the queue
def listen_to_docker_events():
    for event in client.events(decode=True):
        event_queue.put(event)  # Add event to the queue


# Function to display and handle user interactions for container status changes
def handle_user_input():
    while True:
        command = input("Press '0' to enter the status changer panel or continue logging: ")
        if command == '0':
            if not logged_containers:
                print("There is no information about containers.")
            else:
                # Show status changer panel
                print("Containers:")
                for i, (container_name, status) in enumerate(logged_containers.items(), start=1):
                    print(f"{container_name} --> {status}, press {i} to change")

                while True:
                    user_input = input(
                        "Enter the number of the container to change its status, or press '0' to go back: ")

                    if user_input == '0':
                        break  # Go back to the main panel
                    try:
                        index = int(user_input) - 1
                        container_name = list(logged_containers.keys())[index]
                        current_status = get_container_status(container_name)

                        print(f"Container '{container_name}' is currently '{current_status}'.")
                        if current_status == 'exited':
                            print(f"Press '1' to start '{container_name}'")
                        elif current_status == 'running':
                            print(f"Press '2' to stop '{container_name}'")
                        else:
                            print("Unknown status. Unable to change.")

                        # Capture user's action to change container state
                        action = input("Enter your action (1: start, 2: stop, 0: go back): ")
                        if action == '1' and current_status == 'exited':
                            container = client.containers.get(container_name)
                            container.start()
                            print(f"Container '{container_name}' started.")
                        elif action == '2' and current_status == 'running':
                            container = client.containers.get(container_name)
                            container.stop()
                            print(f"Container '{container_name}' stopped.")
                        elif action == '0':
                            break
                        else:
                            print("Invalid action or status.")
                    except (IndexError, ValueError):
                        print("Invalid selection, please try again.")


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Start Docker event listener in a background thread
listener_thread = threading.Thread(target=listen_to_docker_events, daemon=True)
listener_thread.start()

# Start event processing in a background thread
processor_thread = threading.Thread(target=process_event, daemon=True)
processor_thread.start()

# Start user input handling in the main thread
handle_user_input()

# Ensure all events are processed before exiting
event_queue.join()
