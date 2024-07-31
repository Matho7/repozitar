import pandas as pd
import matplotlib.pyplot as plt

# Načítanie dát z CSV
data = pd.read_csv('load_time_results.csv')

# Vytvorenie grafu
plt.figure(figsize=(10, 6))
plt.plot(data['Number of Points'], data['Load Time (seconds)'], marker='o')

# Nastavenie popisov a názvov
plt.title('Čas načítania vs. Počet bodov')
plt.xlabel('Počet bodov')
plt.ylabel('Čas načítania (sekundy)')
plt.grid(True)

# Uloženie grafu
plt.savefig('load_time_plot.png')
plt.show()
