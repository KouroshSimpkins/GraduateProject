import psycopg2
import random
from faker import Faker
import datetime
import os
from dotenv import load_dotenv

fake = Faker('en_GB')


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

    if age < 25:
        patterns = [
            "{first}{last}{random_digits}@{domain}",
            "{random_chars}@{domain}",
            "{first}.{last}@{domain}",
            "{first}{last}@{domain}",
            "{first}.{last}{random_digits}@{domain}",
            "{first}{last}{year}@{domain}"
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


def main():
    person_data = generate_person_data()
    uuid = insert_person(person_data)
    print(f"New person inserted with id: {uuid}")


if __name__ == "__main__":
    for i in range(1000):
        main()
