# Main app.py file for the fingerprint generation system.

import fingerprintgenGAN as fpGAN
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/gen_fingerprints")
def gen_fingerprints():
    fpGAN.devFingerprintGen()
    return "Generated fingerprints!"


@app.route("/fingerprint_gen_api", methods=['GET'])
def fingerprint_gen_api():
    prints = fpGAN.generateFingerprints(5)
    return jsonify(prints.tolist())


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4999)
