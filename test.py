import requests
import time
import csv
import statistics
import matplotlib.pyplot as plt
import os

def test_load_routes(base_url):
    start_time = time.time()
    response = requests.get(f"{base_url}/routes")
    end_time = time.time()
    duration = end_time - start_time
    success = response.status_code == 200
    return success, duration

def test_load_route_details(base_url):
    start_time = time.time()
    response_polyline = requests.get(f"{base_url}/polyline/1")
    response_directions = requests.get(f"{base_url}/directions/1")
    end_time = time.time()
    duration = end_time - start_time
    success = response_polyline.status_code == 200 and response_directions.status_code == 200
    return success, duration

def test_upload_route(base_url, csv_path):
    start_time = time.time()
    with open(csv_path, 'rb') as file:
        response = requests.post(f"{base_url}/upload", files={"file": file})
    end_time = time.time()
    duration = end_time - start_time
    success = response.status_code == 200 or response.status_code == 302
    return success, duration

def run_tests(base_url, csv_paths, repetitions=10):
    results = {
        "load_routes": [],
        "load_route_details": [],
        "upload_route": {path: [] for path in csv_paths}
    }

    for _ in range(repetitions):
        success, duration = test_load_routes(base_url)
        results["load_routes"].append(duration)

        success, duration = test_load_route_details(base_url)
        results["load_route_details"].append(duration)

        for csv_path in csv_paths:
            success, duration = test_upload_route(base_url, csv_path)
            results["upload_route"][csv_path].append(duration)

    return results

def calculate_statistics(results):
    statistics_summary = {}

    statistics_summary["load_routes"] = {
        "average": statistics.mean(results["load_routes"]),
        "stdev": statistics.stdev(results["load_routes"]),
        "min": min(results["load_routes"]),
        "max": max(results["load_routes"]),
    }

    statistics_summary["load_route_details"] = {
        "average": statistics.mean(results["load_route_details"]),
        "stdev": statistics.stdev(results["load_route_details"]),
        "min": min(results["load_route_details"]),
        "max": max(results["load_route_details"]),
    }

    statistics_summary["upload_route"] = {}
    for csv_path, durations in results["upload_route"].items():
        statistics_summary["upload_route"][csv_path] = {
            "average": statistics.mean(durations),
            "stdev": statistics.stdev(durations),
            "min": min(durations),
            "max": max(durations),
        }

    return statistics_summary

def save_statistics_to_txt(statistics_summary, output_file):
    with open(output_file, 'w') as f:
        for test_name, stats in statistics_summary.items():
            if test_name == "upload_route":
                for csv_path, csv_stats in stats.items():
                    f.write(f"Názov testu: {test_name} ({os.path.basename(csv_path)})\n")
                    f.write(f"  Priemerné trvanie: {csv_stats['average']:.2f} sekúnd\n")
                    f.write(f"  Štandardná odchýlka: {csv_stats['stdev']:.2f} sekúnd\n")
                    f.write(f"  Minimálne trvanie: {csv_stats['min']:.2f} sekúnd\n")
                    f.write(f"  Maximálne trvanie: {csv_stats['max']:.2f} sekúnd\n")
            else:
                f.write(f"Názov testu: {test_name}\n")
                f.write(f"  Priemerné trvanie: {stats['average']:.2f} sekúnd\n")
                f.write(f"  Štandardná odchýlka: {stats['stdev']:.2f} sekúnd\n")
                f.write(f"  Minimálne trvanie: {stats['min']:.2f} sekúnd\n")
                f.write(f"  Maximálne trvanie: {stats['max']:.2f} sekúnd\n")

def generate_graphs(statistics_summary):
    test_names = []
    averages = []
    stdevs = []

    for test_name, stats in statistics_summary.items():
        if test_name == "upload_route":
            for csv_path, csv_stats in stats.items():
                test_names.append(f"{test_name} ({os.path.basename(csv_path)})")
                averages.append(csv_stats['average'])
                stdevs.append(csv_stats['stdev'])
        else:
            test_names.append(test_name)
            averages.append(stats['average'])
            stdevs.append(stats['stdev'])

    plt.figure(figsize=(12, 6))
    plt.bar(test_names, averages, yerr=stdevs, color='blue', alpha=0.7, label='Priemer')
    plt.xlabel('Názov testu')
    plt.ylabel('Trvanie (sekundy)')
    plt.title('Priemerné trvanie testov s odchýlkou')
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('test_durations.png')
    plt.show()

if __name__ == "__main__":
    base_url = "http://localhost:8080"
    csv_paths = [f"test_data/{points}_points.csv" for points in [2, 5, 10, 15, 25, 50, 100]]
    results = run_tests(base_url, csv_paths)
    statistics_summary = calculate_statistics(results)
    save_statistics_to_txt(statistics_summary, "test_results_summary.txt")
    generate_graphs(statistics_summary)
