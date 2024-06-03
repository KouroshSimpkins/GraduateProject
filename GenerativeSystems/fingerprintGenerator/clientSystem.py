# A program for testing the fingerprint generator endpoint


def clientTestSystem():
    import requests
    from PIL import Image
    import numpy as np

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
