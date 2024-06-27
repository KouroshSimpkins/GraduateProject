import socketio
import requests
from PIL import Image
import numpy as np
import base64
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
            # Decode the base64 string back to binary data
            decoded_data = base64.b64decode(fingerprint_data)
            # Convert the binary data to a string and then load it as a JSON object
            pixel_data = json.loads(decoded_data.decode('utf-8'))
            # Flatten the deeply nested list structure
            flat_image_data = [pixel[0] for image in pixel_data for row in image for pixel in row]
            # Convert the flat list into a 2D array
            image_side_length = int(len(flat_image_data) ** 0.5)  # Assuming the image is square
            image_array = np.array(flat_image_data, dtype=np.uint8).reshape(image_side_length, image_side_length)
            # Create a PIL image from the NumPy array
            image = Image.fromarray(image_array, 'L')  # 'L' mode for grayscale images
            # Assuming your display library has a function `display_image`:
            display_image(image)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data for fingerprint '{finger_name}': {e}")
        except Exception as e:
            print(f"Unexpected error for fingerprint '{finger_name}': {e}")

# Function to display image on the round display (you need to replace this with your actual display library code)
def display_image(image):
    # This is a placeholder function. Replace it with your actual code to display an image on your specific round display.
    # For example, if using an SPI display with a library like `luma.lcd` or `PIL`, implement the display code here.
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
