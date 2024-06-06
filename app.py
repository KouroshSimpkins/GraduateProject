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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
