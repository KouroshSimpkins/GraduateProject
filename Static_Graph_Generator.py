# File to read data from the database and generate a graph of the database

import psycopg2
import networkx as nx
from dotenv import load_dotenv
import os

from matplotlib import pyplot as plt

import Database_Interaction

load_dotenv()

db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')


def load_person_data():
    conn = Database_Interaction.connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT p1.person_id, p1.first_name, p1.last_name, p2.person_id, p2.first_name, p2.last_name, c.relationship_type
        FROM test_identity_system.persons p1
        INNER JOIN test_identity_system.relationships c ON p1.person_id = c.person1_id
        INNER JOIN test_identity_system.persons p2 ON p2.person_id = c.person2_id;
        """)
        return cur.fetchall()
    except psycopg2.DatabaseError as e:
        print(f"Error loading person data: {e}")


def generate_graph(data):
    g = nx.Graph()

    for row in data:
        g.add_node(row[0], first_name=row[1], last_name=row[2])
        g.add_node(row[3], first_name=row[4], last_name=row[5])
        g.add_edge(row[0], row[3], relationship=row[6])

    return g


if __name__ == "__main__":
    test_data = load_person_data()
    Graph = generate_graph(test_data)
    nx.draw(Graph, with_labels=True)
    plt.show()
