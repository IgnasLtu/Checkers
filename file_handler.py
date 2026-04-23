import csv
import os
from datetime import datetime


class FileHandler:

    DEFAULT_DIR = "saves"

    def __init__(self, save_dir: str = DEFAULT_DIR):
        self._save_dir = save_dir
        os.makedirs(self._save_dir, exist_ok=True)

    def save_game(self, board, current_color: str, filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_{timestamp}.csv"
        filepath = os.path.join(self._save_dir, filename)
        piece_data = board.to_grid_data()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["meta", "current_turn", current_color])
            writer.writerow(["row", "col", "color", "type"])
            for item in piece_data:
                writer.writerow([item["row"], item["col"], item["color"], item["type"]])
        print(f"Game saved: {filepath}")
        return filepath

    def load_game(self, filepath: str) -> tuple:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        piece_data = []
        current_color = "white"
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                if row[0] == "meta":
                    current_color = row[2]
                elif row[0] == "row":
                    continue
                else:
                    try:
                        piece_data.append({
                            "row": int(row[0]), "col": int(row[1]),
                            "color": row[2], "type": row[3]
                        })
                    except (IndexError, ValueError) as e:
                        raise ValueError(f"Corrupted save file: {e}")
        print(f"Game loaded: {filepath}")
        return piece_data, current_color

    def list_saves(self) -> list:
        saves = [f for f in os.listdir(self._save_dir) if f.endswith(".csv")]
        return sorted(saves)

    def save_history(self, history: list, filename: str = "history.csv"):
        filepath = os.path.join(self._save_dir, filename)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["move_number", "player", "from_row", "from_col", "to_row", "to_col", "captured"])
            for entry in history:
                writer.writerow(entry)
