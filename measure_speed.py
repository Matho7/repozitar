import time
import requests


def measure_load_time(num_points):
    start_time = time.time()

    # Simulácia načítania údajov
    url = f'http://localhost:8080/simulate?points={num_points}'
    response = requests.get(url)

    end_time = time.time()
    load_time = end_time - start_time
    return load_time


if __name__ == "__main__":
    num_points_list = [10, 50, 100, 200, 500, 1000]
    results = []

    for num_points in num_points_list:
        load_time = measure_load_time(num_points)
        results.append((num_points, load_time))
        print(f"Number of points: {num_points}, Load time: {load_time:.4f} seconds")

    # Uloženie výsledkov do CSV
    with open('load_time_results.csv', 'w') as f:
        f.write("Number of Points,Load Time (seconds)\n")
        for num_points, load_time in results:
            f.write(f"{num_points},{load_time:.4f}\n")
