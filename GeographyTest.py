import random
import math
import requests


def generate_random_point(center, radius):
    radius_in_degrees = radius / 111.32
    u = random.uniform(0, 1)
    v = random.uniform(0, 1)
    w = radius_in_degrees * (u ** 0.5)
    t = 2 * 3.141592653589793 * v
    x = w * math.cos(t)
    y = w * math.sin(t)

    new_lat = center[0] + x
    new_lon = center[1] + y / math.cos(math.radians(center[0]))

    return new_lat, new_lon


def is_residential_address(address_info):
    if 'features' in address_info and len(address_info['features']) > 0:
        properties = address_info['features'][0]['properties']
        return 'housenumber' in properties
    return False


def extract_required_info(address_info):
    properties = address_info['features'][0]['properties']
    required_info = {
        'house_number': properties.get('housenumber', ''),
        'street': properties.get('street', ''),
        'city': properties.get('city', ''),
        'post_code': properties.get('postcode', ''),
        'country': properties.get('country', ''),
        'latitude': properties.get('lat', 0),
        'longitude': properties.get('lon', 0)
    }
    return required_info


def get_address_from_point(api_key, point):
    lat, lon = point
    url = f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        address_info = response.json()
        if is_residential_address(address_info):
            return extract_required_info(address_info)
    return None


def get_random_residential_address(api_key, center_point, radius):
    address = None
    while address is None:
        random_point = generate_random_point(center_point, radius)
        address = get_address_from_point(api_key, random_point)

    required_info = {}

    if address:
        required_info = {
            'house_number': address['house_number'],
            'street': address['street'],
            'city': address['city'],
            'post_code': address['post_code'],
            'country': address['country'],
            'latitude': address['latitude'],
            'longitude': address['longitude']
        }

    return required_info


# Example usage
center_point = (51.4765609, -0.0702247)  # Example: Berlin city center
radius = 5  # Radius in kilometers
api_key = 'INSERT_API_KEY'

if __name__ == "__main__":
    address = get_random_residential_address(api_key, center_point, radius)
    print(address)
