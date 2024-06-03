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

