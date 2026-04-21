from abc import ABC, abstractmethod
import random
import csv
import os
from datetime import datetime

class GamePiece(ABC):

    def __init__(self, color: str, row: int, col: int):
        self._color = color
        self._row = row
        self._col = col
        self._is_captured = False

    @abstractmethod
    def get_possible_moves(self, board) -> list:
        pass

    @abstractmethod
    def get_captures(self, board, skip=None) -> list:
        pass

    @abstractmethod
    def symbol(self) -> str:
        pass

    @property
    def color(self) -> str:
        return self._color

    @property
    def row(self) -> int:
        return self._row

    @property
    def col(self) -> int:
        return self._col

    @row.setter
    def row(self, value: int):
        self._row = value

    @col.setter
    def col(self, value: int):
        self._col = value

    @property
    def is_captured(self) -> bool:
        return self._is_captured

    def capture(self):
        self._is_captured = True

    def __repr__(self):
        return f"{self.__class__.__name__}(color={self._color}, row={self._row}, col={self._col})"


class Piece(GamePiece):
    def get_possible_moves(self, board) -> list:
        captures = self.get_captures(board)
        return captures if captures else self._get_steps(board)

    def _get_steps(self, board) -> list:
        moves = []
        direction = -1 if self._color == "white" else 1
        for dc in [-1, 1]:
            nr, nc = self._row + direction, self._col + dc
            if board.in_bounds(nr, nc) and board.get_piece(nr, nc) is None:
                moves.append((nr, nc, None))
        return moves

    def get_captures(self, board, skip=None) -> list:
        moves = []
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                nr, nc = self._row + dr, self._col + dc
                if board.in_bounds(nr, nc):
                    target = board.get_piece(nr, nc)
                    if target and target != skip and target.color != self._color:
                        jr, jc = nr + dr, nc + dc
                        if board.in_bounds(jr, jc) and board.get_piece(jr, jc) is None:
                            moves.append((jr, jc, target))
        return moves

    def symbol(self) -> str:
        return "w" if self._color == "white" else "b"


class King(Piece):
    def get_possible_moves(self, board) -> list:
        captures = self.get_captures(board)
        return captures if captures else self._get_steps(board)

    def _get_steps(self, board) -> list:
        moves = []
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                r, c = self._row + dr, self._col + dc
                while board.in_bounds(r, c) and board.get_piece(r, c) is None:
                    moves.append((r, c, None))
                    r += dr
                    c += dc
        return moves

    def get_captures(self, board, skip=None) -> list:
        moves = []
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                r, c = self._row + dr, self._col + dc
                found_enemy = None
                while board.in_bounds(r, c):
                    target = board.get_piece(r, c)
                    if target is None:
                        if found_enemy:
                            moves.append((r, c, found_enemy))
                    elif target == skip:
                        pass
                    elif target.color == self._color:
                        break
                    else:
                        if found_enemy:
                            break
                        found_enemy = target
                    r += dr
                    c += dc
        return moves

    def symbol(self) -> str:
        return "W" if self._color == "white" else "B"

class Board:
    SIZE = 8
    def __init__(self):
        self._grid = [[None] * self.SIZE for _ in range(self.SIZE)]
        self._white_pieces: list = []
        self._black_pieces: list = []

    def setup_pieces(self):
        self._grid = [[None] * self.SIZE for _ in range(self.SIZE)]
        self._white_pieces = []
        self._black_pieces = []
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                if (row + col) % 2 == 1:
                    if row < 3:
                        piece = Piece("black", row, col)
                        self._grid[row][col] = piece
                        self._black_pieces.append(piece)
                    elif row > 4:
                        piece = Piece("white", row, col)
                        self._grid[row][col] = piece
                        self._white_pieces.append(piece)

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.SIZE and 0 <= col < self.SIZE

    def get_piece(self, row: int, col: int):
        if self.in_bounds(row, col):
            return self._grid[row][col]
        return None

    def move_piece(self, piece, to_row: int, to_col: int, captured=None):
        self._grid[piece.row][piece.col] = None
        piece.row = to_row
        piece.col = to_col
        self._grid[to_row][to_col] = piece
        if captured:
            self.capture_piece(captured)
        self.check_promotion(piece)

    def capture_piece(self, piece):
        self._grid[piece.row][piece.col] = None
        piece.capture()
        if piece.color == "white":
            self._white_pieces = [p for p in self._white_pieces if not p.is_captured]
        else:
            self._black_pieces = [p for p in self._black_pieces if not p.is_captured]

    def check_promotion(self, piece):
        if isinstance(piece, King):
            return
        if piece.color == "white" and piece.row == 0:
            self._promote(piece)
        elif piece.color == "black" and piece.row == self.SIZE - 1:
            self._promote(piece)

    def _promote(self, piece):
        king = King(piece.color, piece.row, piece.col)
        self._grid[piece.row][piece.col] = king
        if piece.color == "white":
            self._white_pieces = [king if p is piece else p for p in self._white_pieces]
        else:
            self._black_pieces = [king if p is piece else p for p in self._black_pieces]

    def get_all_moves(self, color: str) -> list:
        pieces = self._white_pieces if color == "white" else self._black_pieces
        all_moves = []
        for piece in pieces:
            for move in piece.get_possible_moves(self):
                all_moves.append((piece, move))
        return all_moves

    def has_pieces(self, color: str) -> bool:
        pieces = self._white_pieces if color == "white" else self._black_pieces
        return len(pieces) > 0

    @property
    def white_pieces(self):
        return list(self._white_pieces)

    @property
    def black_pieces(self):
        return list(self._black_pieces)

    def to_grid_data(self) -> list:
        data = []
        for row in range(self.SIZE):
            for col in range(self.SIZE):
                piece = self._grid[row][col]
                if piece:
                    data.append({
                        "row": row, "col": col,
                        "color": piece.color,
                        "type": "king" if isinstance(piece, King) else "piece"
                    })
        return data

    def load_from_data(self, data: list):
        self._grid = [[None] * self.SIZE for _ in range(self.SIZE)]
        self._white_pieces = []
        self._black_pieces = []
        for item in data:
            row, col, color, ptype = item["row"], item["col"], item["color"], item["type"]
            piece = King(color, row, col) if ptype == "king" else Piece(color, row, col)
            self._grid[row][col] = piece
            if color == "white":
                self._white_pieces.append(piece)
            else:
                self._black_pieces.append(piece)

    def display(self):
        print("  " + " ".join(str(i) for i in range(self.SIZE)))
        for row in range(self.SIZE):
            row_str = f"{row} "
            for col in range(self.SIZE):
                piece = self._grid[row][col]
                if piece:
                    row_str += piece.symbol() + " "
                elif (row + col) % 2 == 0:
                    row_str += ". "
                else:
                    row_str += "_ "
            print(row_str)
        print()

class Player(ABC):

    def __init__(self, name: str, color: str):
        self._name = name
        self._color = color
        self._score = 0
        self._pending_command = None

    @abstractmethod
    def make_move(self, board) -> tuple:
        pass

    @abstractmethod
    def choose_chain_capture(self, piece, moves) -> tuple:
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def color(self) -> str:
        return self._color

    @property
    def score(self) -> int:
        return self._score

    def add_score(self, points: int = 1):
        self._score += points

    def __str__(self):
        return f"{self._name} ({self._color})"


class HumanPlayer(Player):
    def make_move(self, board) -> tuple:
        all_moves = board.get_all_moves(self._color)
        if not all_moves:
            return None

        captures = [(p, m) for p, m in all_moves if m[2] is not None]
        available = captures if captures else all_moves

        print(f"\n{self._name}, your move ({self._color}):")
        print("Available moves:")
        for i, (piece, move) in enumerate(available):
            action = "capture" if move[2] else "move"
            print(f"  [{i}] ({piece.row},{piece.col}) -> ({move[0]},{move[1]}) {action}")
        print("Commands: save | quit | board | help")

        while True:
            raw = input("Choose a number or command: ").strip().lower()

            if raw == "save":
                self._pending_command = "save"
                return "COMMAND"
            elif raw in ("quit", "exit"):
                self._pending_command = "quit"
                return "COMMAND"
            elif raw == "board":
                board.display()
                continue
            elif raw == "help":
                print("  save  - save the game")
                print("  quit  - quit the game")
                print("  board - show the currentboard")
                continue

            try:
                choice = int(raw)
                if 0 <= choice < len(available):
                    return available[choice]
                print("Invalid number, try again.")
            except ValueError:
                print("Enter a number or command (help).")

    def choose_chain_capture(self, piece, moves) -> tuple:
        print(f"\n Can capture again! Piece at ({piece.row},{piece.col}) ")
        print("Follow-up captures:")
        for i, move in enumerate(moves):
            print(f"  [{i}] -> ({move[0]},{move[1]})")

        while True:
            raw = input("Choose a number: ").strip()
            try:
                idx = int(raw)
                if 0 <= idx < len(moves):
                    return moves[idx]
                print("Invalid number.")
            except ValueError:
                print("Enter a number.")


class AIPlayer(Player):
    def make_move(self, board) -> tuple:
        all_moves = board.get_all_moves(self._color)
        if not all_moves:
            return None

        captures = [(p, m) for p, m in all_moves if m[2] is not None]
        available = captures if captures else all_moves

        choice = random.choice(available)
        piece, move = choice
        print(f"\n{self._name} (AI) moves: ({piece.row},{piece.col}) -> ({move[0]},{move[1]})")
        return choice

    def choose_chain_capture(self, piece, moves) -> tuple:
        chosen = random.choice(moves)
        print(f"{self._name} (AI) captures again: ({piece.row},{piece.col}) -> ({chosen[0]},{chosen[1]})")
        return chosen

class PlayerFactory:
    PLAYER_TYPES = ["human", "ai"]

    @staticmethod
    def create_player(player_type: str, name: str, color: str) -> Player:
        player_type = player_type.lower().strip()
        if player_type == "human":
            return HumanPlayer(name, color)
        elif player_type == "ai":
            return AIPlayer(name, color)
        else:
            raise ValueError(
                f"Unknown player type: '{player_type}'. "
                f"Available: {PlayerFactory.PLAYER_TYPES}"
            )

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

class Game:
    def __init__(self, player1: Player, player2: Player):
        self._board = Board()          
        self._player1 = player1       
        self._player2 = player2      
        self._current_player = player1
        self._file_handler = FileHandler()
        self._move_history = []
        self._move_count = 0
        self._is_running = False

    def start(self):
        self._board.setup_pieces()
        self._current_player = self._player1
        self._move_history = []
        self._move_count = 0
        self._is_running = True
        print(f"\n Let the game begin! ")
        print(f"{self._player1} vs {self._player2}")
        print("Legend: w=white, b=black, W=white king, B=black king\n")

    def switch_player(self):
        if self._current_player is self._player1:
            self._current_player = self._player2
        else:
            self._current_player = self._player1

    def check_winner(self) -> Player | None:
        if not self._board.has_pieces("white"):
            return self._player2
        if not self._board.has_pieces("black"):
            return self._player1
        if not self._board.get_all_moves("white"):
            return self._player2
        if not self._board.get_all_moves("black"):
            return self._player1
        return None

    def _record_move(self, piece, move):
        self._move_count += 1
        self._move_history.append([
            self._move_count,
            self._current_player.name,
            piece.row, piece.col,
            move[0], move[1],
            1 if move[2] else 0
        ])

    def _handle_chain_captures(self, piece):
        while True:
            follow_ups = piece.get_captures(self._board)
            if not follow_ups:
                break
            move = self._current_player.choose_chain_capture(piece, follow_ups)
            self._record_move(piece, move)
            self._board.move_piece(piece, move[0], move[1], move[2])

    def save(self, filename: str = None):
        self._file_handler.save_game(self._board, self._current_player.color, filename)
        self._file_handler.save_history(self._move_history)

    def load(self, filepath: str):
        piece_data, current_color = self._file_handler.load_game(filepath)
        self._board.load_from_data(piece_data)
        self._current_player = self._player1 if current_color == self._player1.color else self._player2
        self._is_running = True
        print(f"Resuming game. Current player: {self._current_player}")

    def run(self):
        if not self._is_running:
            self.start()

        while self._is_running:
            self._board.display()
            print(f"Move #{self._move_count + 1} | Current player: {self._current_player}")

            winner = self.check_winner()
            if winner:
                self._board.display()
                print(f"\nWinner: {winner}!")
                winner.add_score()
                self._file_handler.save_history(self._move_history)
                self._is_running = False
                break

            result = self._current_player.make_move(self._board)

            if result is None:
                print(f"{self._current_player} has no moves. Other player wins!")
                break

            if result == "COMMAND":
                cmd = getattr(self._current_player, "_pending_command", None)
                if cmd == "save":
                    self.save()
                elif cmd == "quit":
                    print("Game quit.")
                    self._is_running = False
                continue

            piece, move = result
            self._record_move(piece, move)
            self._board.move_piece(piece, move[0], move[1], move[2])

            if move[2]:
                self._handle_chain_captures(piece)

            self.switch_player()
