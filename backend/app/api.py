import csv
from fastapi import APIRouter
from pathlib import Path

router = APIRouter()
DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data"

def read_csv_to_dict(file_name: str):
    """Helper function to read a CSV and return it as a list of dictionaries."""
    file_path = DATA_PATH / file_name
    if not file_path.exists():
        return []
    with file_path.open(mode='r', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))

@router.get("/data/clinker")
def get_clinker_data():
    return read_csv_to_dict("clinker.csv")

@router.get("/data/energy")
def get_energy_data():
    return read_csv_to_dict("energy.csv")

@router.get("/data/fuel_mix")
def get_fuel_mix_data():
    return read_csv_to_dict("fuel_mix.csv")

@router.get("/data/utilities")
def get_utilities_data():
    return read_csv_to_dict("utilities.csv")
