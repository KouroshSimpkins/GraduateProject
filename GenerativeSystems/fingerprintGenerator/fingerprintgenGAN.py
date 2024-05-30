import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt


# Load the old_model
old_model = tf.saved_model.load('fingerprintGAN_model')

# If the old_model has a signature, try to access it
try:
    infer = old_model.signatures['serving_default']
    print("Model loaded successfully with signature: ", infer)
except Exception as e:
    print("Error accessing serving_default signature: ", str(e))

# tf.saved_model.save(old_model, 'new_model_test')


def generateFingerprints(no=1):
    random_latent_vectors = tf.random.normal(shape=(no, 128))
    testImages = old_model(random_latent_vectors)
    testImages *= 255
    testImages = testImages.numpy()

    return testImages


def devFingerprintGen():
    prints = generateFingerprints(5)
    print(prints.shape)

    for i in range(prints.shape[0]):
        plt.subplot(3, 3, i+1)
        plt.imshow(prints[i, :, :, 0] * 127.5 + 127.5, cmap='gray')
        plt.axis('off')
    plt.show()


def clientTestSystem():
    import requests
    from PIL import Image

    response = requests.get("http://127.0.0.1:4999/fingerprint_gen_api")

    response_data = response.json()

    # Extract pixel values and flatten the deeply nested list structure
    flat_image_data = [pixel[0] for image in response_data for row in image for pixel in row]

    # Convert the flat list into a 2D array
    image_side_length = int(len(flat_image_data) ** 0.5)  # Assuming the image is square
    image_array = np.array(flat_image_data, dtype=np.uint8).reshape(image_side_length, image_side_length)

    # Create a PIL image from the NumPy array
    img = Image.fromarray(image_array, 'L')  # 'L' mode for grayscale images

    # Show the image
    img.show()

    print(response_data)


if __name__ == "__main__":
    # devFingerprintGen()
    clientTestSystem()
