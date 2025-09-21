import csv
from pathlib import Path

print("Attempting to load data using csv module...")
DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data"

combined_data = []
DATA_LENGTH = 0

try:
    # Read all csv files and store their data
    clinker_data = list(csv.DictReader((DATA_PATH / "clinker.csv").open()))
    energy_data = list(csv.DictReader((DATA_PATH / "energy.csv").open()))
    fuel_mix_data = list(csv.DictReader((DATA_PATH / "fuel_mix.csv").open()))
    
    # Combine the data row by row
    for i in range(len(clinker_data)):
        combined_row = {
            **clinker_data[i],
            **energy_data[i],
            **fuel_mix_data[i],
        }
        # Convert numeric values from string to float
        for key, value in combined_row.items():
            if key != 'timestamp':
                try:
                    combined_row[key] = float(value)
                except (ValueError, TypeError):
                    pass # Keep as string if conversion fails
        
        combined_data.append(combined_row)

    DATA_LENGTH = len(combined_data)
    print("Data loaded and combined successfully!")
except FileNotFoundError as e:
    print(f"Error: Data file not found. {e}")
    combined_data = []
    DATA_LENGTH = 0
except Exception as e:
    print(f"An error occurred during data loading: {e}")
    combined_data = []
    DATA_LENGTH = 0
