import psycopg2
import random
import requests
from faker import Faker
import datetime
import os
from dotenv import load_dotenv
from networkx.algorithms.components import connected
import logging
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import GeographyTest

fake = Faker('en_GB')


def pick_random_address():
    """
    Select a random address within a radius, storing it in the database, and then adding a person to that address.

    :return:
    """
    # Select a random point within a 2km radius of a given address, using Nominatim to get the coordinates.
    geolocator = Nominatim(user_agent="Safari")
    location = geolocator.geocode("42 Bonar Road, London, SE15 5JY")
    latitude = location.latitude
    longitude = location.longitude

    # Generate a random point within a 2km radius of the selected point
    point = (latitude, longitude)
    radius = 5

    address = GeographyTest.get_random_residential_address(os.getenv('GEOAPIFY_API_KEY'), point, radius)

    print(address)

    # Store the random point in the database
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("SET search_path = 'test_identity_system';")
    cur.execute("""
        INSERT INTO Addresses (house_number, street, city, post_code, country, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (address['house_number'], address['street'], address['city'], address['post_code'], address['country'], address['latitude'], address['longitude']))

    conn.commit()
    cur.close()
    conn.close()


def generate_email(first_name, last_name, date_of_birth):
    """
    Generate an email address for a person

    :param date_of_birth: The date of birth of the person - datetime object
    :param first_name: The first name of the person
    :param last_name: The last name of the person
    :return: An email address
    """
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "protonmail.com"]
    current_year = datetime.datetime.now().year
    age = current_year - date_of_birth.year

    if age < 28:
        patterns = [
            "{first}{last}{random_digits}@{domain}",
            "{random_chars}@{domain}",
            "{first}.{last}@{domain}",
            "{first}{last}@{domain}",
            "{first}.{last}{random_digits}@{domain}",
            "{first}{last}{year}@{domain}",
            "{first}{last}{random_chars}@{domain}"
        ]
    else:
        patterns = [
            "{first}.{last}@{domain}",
            "{first}{last}@{domain}",
            "{first}{random_digits}@{domain}",
            "{f}{last}@{domain}",
            "{first}{l}@{domain}"
        ]

    # Select a random pattern
    pattern = random.choice(patterns)

    # Format the pattern
    email = pattern.format(first=first_name.lower(), last=last_name.lower(),
                           f=first_name[0].lower(), l=last_name[0].lower(),
                           random_digits=random.randint(0, 9999),
                           random_chars=fake.lexify("?????????"),
                           year=date_of_birth.year,
                           domain=random.choice(domains))

    return email


load_dotenv()

# !TODO: Tidy up environment variable locations.
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')


def connect_to_db():
    return psycopg2.connect(user=db_user,
                            password=db_password,
                            host=db_host,
                            port="5432",
                            database=db_name)


def generate_person_data():
    """
    Generate data for a single person

    :return: A dictionary of person data
    """
    first_name = fake.first_name()
    last_name = fake.last_name()
    date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=75)
    email = generate_email(first_name, last_name, date_of_birth)

    person_data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'date_of_birth': date_of_birth
    }

    return person_data


def insert_person(person_data):
    """
    Insert a new person into the database

    :param person_data: A dictionary of person data
    :return: The id of the new person
    """
    connection = connect_to_db()
    cursor = connection.cursor()

    # !TODO: Remove the below line of code when switching to next test database.
    cursor.execute("SET search_path = 'test_identity_system';")

    cursor.execute("INSERT INTO persons (first_name, last_name, email, date_of_birth) "
                   "VALUES (%s, %s, %s, %s) RETURNING persons.uuid;",
                   (person_data['first_name'], person_data['last_name'], person_data['email'],
                    person_data['date_of_birth']))

    new_person_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return new_person_id


def insert_passport(person_id):
    conn = connect_to_db()
    cur = conn.cursor()

    # !TODO: Sort out database schema, this is getting fucking silly.
    cur.execute("SET search_path = 'test_identity_system';")

    # Start date is a random date in the last 7 years
    start_date = fake.past_date(start_date="-7y")
    # End date is 10 years after start date
    end_date = start_date + datetime.timedelta(days=365 * 10)

    cur.execute("""
        INSERT INTO Passports (person_id, passport_number, nationality, date_of_issue, expiration_date, place_of_issue)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (person_id, fake.bothify(text='??########'), fake.country(), start_date, end_date, fake.city()))
    conn.commit()
    cur.close()
    conn.close()


def insert_drivers_license(person_id):
    conn = connect_to_db()
    cur = conn.cursor()

    # !TODO: Sort out database schema, this is getting fucking silly.
    cur.execute("SET search_path = 'test_identity_system';")

    # !TODO: Maybe remove end date? Not sure if drivers licenses have an end date...
    # Start date is a random date in the last 7 years
    start_date = fake.past_date(start_date="-7y")
    # End date is 10 years after start date
    end_date = start_date + datetime.timedelta(days=365 * 10)

    cur.execute("""
        INSERT INTO DriversLicenses (person_id, license_number, date_of_issue,
         expiration_date, categories, restrictions)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (person_id, fake.bothify(text='##########'), start_date, end_date, 'B, A', 'None'))
    conn.commit()
    cur.close()
    conn.close()


def insert_fingerprints(person_id, finger_name, fingerprint_data):
    conn = connect_to_db()

    try:
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO test_identity_system.fingerprints (person_id, finger_name, fingerprint_data)
        VALUES (%s, %s, %s);
        """, (person_id, finger_name, psycopg2.Binary(fingerprint_data)))
        conn.commit()
    except psycopg2.DatabaseError as e:
        print(f"Error inserting fingerprint data: {e}")
        conn.rollback()
    finally:
        if conn is not connected:
            conn.close()


def get_fingerprint_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to retrieve data")
        return None


def generate_connection(person1_id, person2_id):
    """
    Generate a connection between two distinct people ensuring no duplicates, with warnings.

    :param person1_id: Identifier for the first person
    :param person2_id: Identifier for the second person
    :return: None
    """
    # Set up basic logging (configure as needed for your application)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Ensure the two IDs are different
    if person1_id == person2_id:
        logging.warning("Attempted to create a relationship with oneself. Operation skipped.")
        return  # Exit the function early

    conn = connect_to_db()
    cur = conn.cursor()

    try:
        # Set the schema
        cur.execute("SET search_path TO 'test_identity_system';")

        # Check if a relationship already exists between the two, regardless of order
        cur.execute("""
        SELECT COUNT(*) FROM relationships
        WHERE (person1_id = %s AND person2_id = %s) OR (person1_id = %s AND person2_id = %s);
        """, (person1_id, person2_id, person2_id, person1_id))

        if cur.fetchone()[0] > 0:
            logging.warning(
                "A relationship already exists between person ID {} and person ID {}. Operation skipped.".format(
                    person1_id, person2_id))
            return  # Exit the function early

        # Generate a random relationship type
        relationship = fake.random_element(elements=['friend', 'colleague', 'family', 'business_partner'])

        # Insert the new relationship
        cur.execute("""
        INSERT INTO relationships (person1_id, person2_id, relationship_type)
        VALUES (%s, %s, %s);
        """, (person1_id, person2_id, relationship))

        conn.commit()
    finally:
        cur.close()
        conn.close()


def generate_person():
    person_data = generate_person_data()
    uuid = insert_person(person_data)

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SET search_path = 'test_identity_system';")

    cur.execute("SELECT * FROM Persons WHERE uuid = %s;", (uuid,))
    person_record = cur.fetchone()
    person_id = person_record[0]  # Assuming person_id is the first column.

    num_of_connections = random.randint(20, 40)
    connections = []

    for _ in range(num_of_connections):
        cur.execute("SELECT uuid FROM persons ORDER BY RANDOM() LIMIT 1;")
        random_uuid = cur.fetchone()[0]

        cur.execute("SELECT person_id FROM Persons WHERE uuid = %s;", (random_uuid,))
        person2_id = cur.fetchone()[0]

        generate_connection(person_id, person2_id)
        connections.append(person2_id)

    finger_names = ['Right Thumb', 'Right Index', 'Right Middle', 'Right Ring', 'Right Little',
                    'Left Thumb', 'Left Index', 'Left Middle', 'Left Ring', 'Left Little']
    fingerprints = []

    api_url = "http://127.0.0.1:4999/fingerprint_gen_api"
    for finger_name in finger_names:
        fingerprint_data = get_fingerprint_data(api_url)
        insert_fingerprints(person_id, finger_name, fingerprint_data)
        fingerprints.append({finger_name: fingerprint_data})

    cur.close()

    # Additional personal documents
    passport_id = insert_passport(person_id)
    drivers_license_id = insert_drivers_license(person_id)

    pick_random_address()

    # The last generated address will be the one linked to the person
    cur = conn.cursor()
    cur.execute("SET search_path = 'test_identity_system';")
    cur.execute("SELECT address_id FROM addresses ORDER BY RANDOM() LIMIT 1;")
    address_id = cur.fetchone()[0]
    cur.execute("UPDATE Persons SET home_address_id = %s WHERE person_id = %s;", (address_id, person_id))
    conn.commit()
    cur.close()

    cur = conn.cursor()
    cur.execute("SET search_path = 'test_identity_system';")
    cur.execute("SELECT * FROM Persons WHERE person_id = %s;", (person_id,))
    person_record = cur.fetchone()
    cur.close()

    # Compile all generated data into a result dictionary
    result = {
        "uuid": uuid,
        "person_record": person_record,
        "connections": connections,
        "fingerprints": fingerprints,
        "passport_id": passport_id,
        "drivers_license_id": drivers_license_id
    }

    print(f"New person inserted with id: {uuid}")
    return result


def main():
    # !TODO: Hardcode tailscale IP address (for showcase)
    api_url = "http://127.0.0.1:4999/fingerprint_gen_api"
    finger_names = ['Right Thumb', 'Right Index', 'Right Middle', 'Right Ring', 'Right Little', 'Left Thumb',
                    'Left Index', 'Left Middle', 'Left Ring', 'Left Little']

    person_data = generate_person_data()
    uuid = insert_person(person_data)

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SET search_path = 'test_identity_system';")

    cur.execute("SELECT person_id FROM Persons WHERE uuid = %s;", (uuid,))
    person_id = cur.fetchone()[0]

    num_of_connections = random.randint(20, 40)

    # This generations system assumes a database that already has people in it.
    # If for the showcase, I want a fresh database I'll need to make some changes.

    for _ in range(num_of_connections):
        cur.execute("SELECT uuid FROM persons ORDER BY RANDOM() LIMIT 1;")
        random_uuid = cur.fetchone()[0]

        cur.execute("SELECT person_id FROM Persons WHERE uuid = %s;", (random_uuid,))
        person2_id = cur.fetchone()[0]

        generate_connection(person_id, person2_id)

    for finger_name in finger_names:
        fingerprint_data = get_fingerprint_data(api_url)
        insert_fingerprints(person_id, finger_name, fingerprint_data)

    cur.close()

    insert_passport(person_id)
    insert_drivers_license(person_id)

    print(f"New person inserted with id: {uuid}")


if __name__ == "__main__":
    pick_random_address()
