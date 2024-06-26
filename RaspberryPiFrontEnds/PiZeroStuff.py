import socketio
import requests
from PIL import Image
from io import BytesIO
import base64
import numpy as np
import json

# Replace with your Flask server URL
FLASK_SERVER_URL = 'http://kouroshs-macbook-pro:5001'


# Function to fetch fingerprint data from Flask server
def fetch_fingerprints(person_id):
    response = requests.get(f"{FLASK_SERVER_URL}/fingerprints/{person_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching fingerprints: {response.status_code}")
        return []


# Function to display images on the round display
def display_images(fingerprints):
    for fingerprint in fingerprints:
        finger_name = fingerprint['finger_name']
        fingerprint_data = fingerprint['fingerprint_data']
        try:
            # Parse the JSON string into a Python list
            pixel_values = json.loads(fingerprint_data)
            # Convert the list to a NumPy array
            image_array = np.array(pixel_values, dtype=np.uint8)
            # Create an image from the NumPy array
            image = Image.fromarray(image_array)
            # Assuming your display library has a function `display_image`:
            display_image(image)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data for fingerprint '{finger_name}': {e}")
        except Exception as e:
            print(f"Unexpected error for fingerprint '{finger_name}': {e}")


# Function to display image on the round display (you need to replace this with your actual display library code)
def display_image(image):
    image.show()  # This line is just for testing; replace it with actual display code


# Create a Socket.IO client
sio = socketio.Client()


@sio.event
def connect():
    print('Connected to server')


@sio.event
def disconnect():
    print('Disconnected from server')


@sio.event
def new_identity_generated(data):
    print('Broadcast message received:', data)
    person_id = data.get('person_id')
    if person_id:
        fingerprints = fetch_fingerprints(person_id)
        display_images(fingerprints)


# Connect to the Socket.IO server
sio.connect('http://kouroshs-macbook-pro:5001')

# Wait indefinitely, processing events
sio.wait()
