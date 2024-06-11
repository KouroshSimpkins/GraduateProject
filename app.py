from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv
from Database_Interaction import connect_to_db

load_dotenv()

db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')

app = Flask(__name__)
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
        SELECT person_id, first_name, last_name, email, date_of_birth
        FROM test_identity_system.persons
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
