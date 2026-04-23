from abc import ABC, abstractmethod
import random


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
                print("  board - show the current board")
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
