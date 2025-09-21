import asyncio
import random
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
from .data_loader import combined_data, DATA_LENGTH

router = APIRouter()

# (generate_log_message function remains the same)
def generate_log_message(data_row):
    timestamp = datetime.now().isoformat()
    thresholds = {
        "spc": {"warn": 880, "alert": 950},
        "co2": {"warn": 18, "alert": 22},
        "clinker_quality": {"warn": 38, "alert": 35}
    }
    if data_row["spc"] > thresholds["spc"]["alert"]:
        return {"id": timestamp, "level": "Alert", "message": f"Critical SPC: {data_row['spc']:.1f} kWh/t!"}
    if data_row["co2"] > thresholds["co2"]["alert"]:
        return {"id": timestamp, "level": "Alert", "message": f"Critical CO₂: {data_row['co2']:.2f} t/t!"}
    if data_row["clinker_quality"] < thresholds["clinker_quality"]["alert"]:
        return {"id": timestamp, "level": "Alert", "message": f"Critical Quality: {data_row['clinker_quality']:.1f}%!"}
    if data_row["spc"] > thresholds["spc"]["warn"]:
        return {"id": timestamp, "level": "Warning", "message": f"High SPC: {data_row['spc']:.1f} kWh/t."}
    if data_row["co2"] > thresholds["co2"]["warn"]:
        return {"id": timestamp, "level": "Warning", "message": f"High CO₂: {data_row['co2']:.2f} t/t."}
    if data_row["clinker_quality"] < thresholds["clinker_quality"]["warn"]:
        return {"id": timestamp, "level": "Warning", "message": f"Quality Drop: {data_row['clinker_quality']:.1f}%."}
    if random.random() < 0.2:
        return {"id": timestamp, "level": "Info", "message": f"System stable. TSR: {data_row['tsr']:.1f}%."}
    return None


@router.websocket("/ws/live_data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to WebSocket.")
    current_index = 0
    try:
        while True:
            if DATA_LENGTH > 0:
                data_row = combined_data[current_index]
                log_message = generate_log_message(data_row)
                # data_row is already a dictionary, no .to_dict() needed
                payload = {"kpi_data": data_row, "log_entry": log_message}
                await websocket.send_json(payload)
                current_index = (current_index + 1) % DATA_LENGTH
                await asyncio.sleep(5)
            else:
                await websocket.send_json({"error": "Data not available"})
                await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
