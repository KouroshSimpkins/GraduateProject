import sys
import os
import time
import requests


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


def send_request(url):
    """

    :param url:
    :return:
    """

    response = requests.get(url)
    return response.json()


def format_person_data(data):
    """
    Formats the person data into a readable string.

    :param data: List containing person details.
    :return: Formatted string.
    """
    formatted_string = f"""
    Person ID: {data[0]}
    Name: {data[1]} {data[2]}
    Email: {data[3]}
    Date of Birth: {data[4]}
    Address: {data[15]} {data[13]}, {data[14]}
    Additional Info: 
        Passport Number: {data[5]}
        Country: {data[6]}
        Passport Issue Date: {data[7]}
        Passport Expiry Date: {data[8]}
        Drivers License: {data[9]}
        Registration Date: {data[10]}
        Drivers License Expiry: {data[11]}
        Category: {data[12]}
    """
    return formatted_string


def send_post_request(url):
    """

    :param url:
    :return:
    """

    response = requests.post(url)
    return response.json()


if __name__ == "__main__":
    url_receive = "http://kouroshs-macbook-pro:5001/newest_person"
    url_post = "http://kouroshs-macbook-pro:5001/new_person"  # Endpoint to generate new person

    while True:
        os.system('clear')
        input("Press Enter to get Person Data")

        send_post_request(url_post)
        data = send_request(url_receive)
        formatted_data = format_person_data(data)
        slow_type(formatted_data)
