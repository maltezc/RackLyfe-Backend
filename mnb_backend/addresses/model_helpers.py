import random
from geopy.distance import geodesic


# region geo fuzzer

def fuzz_coordinates(y, x, distance_in_meters=200):
    """
    Fuzzes the coordinates of the location point by a random amount within a specified radius."""

    # Calculate a random angle and distance within the specified radius
    distance_in_meters = 200
    random_angle = random.uniform(0, 360)  # Random angle in degrees
    random_distance = random.uniform(0, distance_in_meters)

    # Calculate the destination point based on angle and distance using geodesic
    new_point = geodesic(kilometers=random_distance / 1000).destination((y, x), random_angle)

    return new_point.longitude, new_point.latitude

# endregion
