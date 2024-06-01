import sys
import time
import random


def slow_type(text, speed=0.05):
    """

    :param text:
    :param speed:
    :return:
    """

    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()


def generate_identity():
    """

    :return:
    """

    first_names = ["Alexandra", "Bobbie", "Caroline", "Vincent", "Diana", "Canace"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
                  "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez",
                  "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez"]
    year = random.randint(1950, 2000)

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)

    return f"{first_name} {last_name}, Born {year}"


def display_new_identity():
    """

    :return:
    """

    identity = generate_identity()
    prompt = "Generated Identity: "
    slow_type(prompt)
    slow_type(identity, speed=0.1)


if __name__ == "__main__":
    input("Press Enter to generate a new identity")
    display_new_identity()
