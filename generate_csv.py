import csv
import random
import os

def generate_coordinates(num_points, start_lat=49.1951, start_lng=16.6068):
    coordinates = []
    for _ in range(num_points):
        # Increment longitude to simulate "moving right" (east)
        start_lng += random.uniform(0.005, 0.05)  # Adjust increment range as needed (increased range)
        # Increment latitude to simulate "moving up" (north)
        start_lat += random.uniform(0.005, 0.05)  # Adjust increment range as needed (increased range)
        coordinates.append((start_lat, start_lng))
    return coordinates

def generate_csv(filename, num_points):
    coordinates = generate_coordinates(num_points)
    os.makedirs('test_data', exist_ok=True)  # Ensure the directory exists
    with open(os.path.join('test_data', filename), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        waypoints = ','.join([f"{lat},{lng}" for lat, lng in coordinates])
        writer.writerow([waypoints, f"Route with {num_points} points"])

if __name__ == "__main__":
    points = [2, 5, 10, 15, 25, 50, 100]
    for num_points in points:
        filename = f"{num_points}_points.csv"
        generate_csv(filename, num_points)
