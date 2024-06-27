from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import psycopg2
import os
from dotenv import load_dotenv
from Database_Interaction import connect_to_db, generate_person
import base64

load_dotenv()

db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)  # Development only
# !TODO: Remove CORS in production


@app.route('/data')
def get_data():
    conn = connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT person_id, first_name, last_name, email, date_of_birth
        FROM test_identity_system.persons;
        """)
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(data)
    except psycopg2.DatabaseError as e:
        return jsonify({"error": f"Error loading person data: {e}"})


@app.route('/newest_person')
def get_newest_person():
    conn = connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT p.person_id, p.first_name, p.last_name, p.email, p.date_of_birth,
        pa.passport_number, pa.nationality, pa.date_of_issue, pa.expiration_date,
        dr.license_number, dr.date_of_issue, dr.expiration_date, dr.categories,
        a.street, a.post_code, a.house_number
        FROM test_identity_system.persons p
        LEFT JOIN test_identity_system.passports pa ON p.person_id = pa.person_id
        LEFT JOIN test_identity_system.driverslicenses dr ON p.person_id = dr.person_id
        LEFT JOIN test_identity_system.addresses a on p.home_address_id = a.address_id
        ORDER BY person_id DESC
        LIMIT 1;
        """)
        data = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify(data)
    except psycopg2.DatabaseError as e:
        return jsonify({"error": f"Error loading person data: {e}"})


@app.route('/details/<int:person_id>')
def get_person_details(person_id):
    conn = connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT p.person_id, p.first_name, p.last_name, p.email, p.date_of_birth,
        f.finger_name,
        pa.passport_number, pa.nationality, pa.date_of_issue, pa.expiration_date,
        dr.license_number, dr.date_of_issue, dr.expiration_date, dr.categories
        FROM test_identity_system.persons p
        LEFT JOIN test_identity_system.fingerprints f ON p.person_id = f.person_id
        LEFT JOIN test_identity_system.passports pa ON p.person_id = pa.person_id
        LEFT JOIN test_identity_system.driverslicenses dr ON p.person_id = dr.person_id
        WHERE p.person_id = %s;
        """, (person_id,))
        data = cur.fetchone()  # More fucking Jank
        cur.close()
        conn.close()
        return jsonify(data)
    except psycopg2.DatabaseError as e:
        return jsonify({"error": f"Error loading person data: {e}"})


@app.route('/relationships')
def get_relationships():
    conn = connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT p1.person_id, p1.first_name, p1.last_name, p2.person_id, p2.first_name, p2.last_name, c.relationship_type
        FROM test_identity_system.persons p1
        INNER JOIN test_identity_system.relationships c ON p1.person_id = c.person1_id
        INNER JOIN test_identity_system.persons p2 ON p2.person_id = c.person2_id;
        """)
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(data)
    except psycopg2.DatabaseError as e:
        return jsonify({"error": f"Error loading person data: {e}"})


@app.route('/relationships/<int:person_id>')
def get_person_relationships(person_id):
    conn = connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT p1.person_id, p1.first_name, p1.last_name, p2.person_id, p2.first_name, p2.last_name, c.relationship_type
        FROM test_identity_system.persons p1
        INNER JOIN test_identity_system.relationships c ON p1.person_id = c.person1_id
        INNER JOIN test_identity_system.persons p2 ON p2.person_id = c.person2_id
        WHERE p1.person_id = %s OR p2.person_id = %s;
        """, (person_id, person_id))
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(data)
    except psycopg2.DatabaseError as e:
        return jsonify({"error": f"Error loading person data: {e}"})


@app.route('/relationships/newest_person')
def get_newest_person_relationships():
    conn = connect_to_db()

    try:
        cur = conn.cursor()

        # Step 1: Get the newest person ID
        cur.execute("""
        SELECT person_id, first_name, last_name 
        FROM test_identity_system.persons
        ORDER BY person_id DESC
        LIMIT 1;
        """)
        newest_person = cur.fetchone()
        if not newest_person:
            cur.close()
            conn.close()
            return jsonify({"error": "No persons found in the database."})

        newest_person_id = newest_person[0]

        # Step 2: Get all relationships involving the newest person
        cur.execute("""
        SELECT p1.person_id, p1.first_name, p1.last_name, p2.person_id, p2.first_name, p2.last_name, c.relationship_type
        FROM test_identity_system.relationships c
        INNER JOIN test_identity_system.persons p1 ON p1.person_id = c.person1_id
        INNER JOIN test_identity_system.persons p2 ON p2.person_id = c.person2_id
        WHERE p1.person_id = %s OR p2.person_id = %s;
        """, (newest_person_id, newest_person_id))

        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(data)
    except psycopg2.DatabaseError as e:
        return jsonify({"error": f"Error loading person data: {e}"})


@app.route('/new_person', methods=['POST'])
def add_new_person():
    generate_person()
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT person_id
    FROM test_identity_system.persons
    ORDER BY person_id DESC
    LIMIT 1;
    """)
    person_id = cur.fetchone()[0]
    cur.close()

    socketio.emit('new_identity_generated', {'data': 'New person added', 'person_id': person_id})
    return jsonify({"message": "Person added"})


@app.route('/fingerprints/<int:person_id>')
def get_fingerprints(person_id):
    conn = connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT f.finger_name, f.fingerprint_data
        FROM test_identity_system.fingerprints f
        WHERE f.person_id = %s;
        """, (person_id,))
        data = cur.fetchall()

        encoded_data = []
        for record in data:
            finger_name, fingerprint_data = record
            if fingerprint_data is not None:
                fingerprint_data = base64.b64encode(fingerprint_data).decode('utf-8')
            encoded_data.append({'finger_name': finger_name, 'fingerprint_data': fingerprint_data})

        cur.close()
        conn.close()
        return jsonify(encoded_data)
    except psycopg2.DatabaseError as e:
        return jsonify({"error": f"Error loading person data: {e}"})


@app.route('/newest_address')
def get_newest_address():
    conn = connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT a.latitude, a.longitude
        FROM test_identity_system.addresses a
        ORDER BY address_id DESC
        LIMIT 1;
        """)
        data = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify(data)
    except psycopg2.DatabaseError as e:
        return jsonify({"error": f"Error loading address data: {e}"})


@app.route('/newest_person_address')
def get_newest_person_address():
    conn = connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT a.latitude, a.longitude, p.first_name, p.last_name
        FROM test_identity_system.persons p
        INNER JOIN test_identity_system.addresses a ON p.home_address_id = a.address_id
        ORDER BY p.person_id DESC
        LIMIT 1;
        """)
        data = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify(data)
    except psycopg2.DatabaseError as e:
        return jsonify({"error": f"Error loading address data: {e}"})


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
