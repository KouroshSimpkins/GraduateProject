from faker import Faker
import Database_Interaction

fake = Faker()


def insert_passport(person_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Passports (person_id, passport_number, nationality, date_of_issue, expiration_date, place_of_issue)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (person_id, fake.bothify(text='??########'), fake.country(), fake.past_date(start_date="-7y"), fake.future_date(end_date="+10y"), fake.city()))
    conn.commit()
    cur.close()
    conn.close()


def insert_drivers_license(person_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO DriversLicenses (person_id, license_number, date_of_issue, expiration_date, categories, restrictions)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (person_id, fake.bothify(text='##########'), fake.past_date(), fake.future_date(end_date="+10y"), 'B, A', 'None'))
    conn.commit()
    cur.close()
    conn.close()
