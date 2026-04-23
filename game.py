from board import Board
from player import Player
from file_handler import FileHandler


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

    @property
    def board(self):
        return self._board

    @property
    def current_player(self):
        return self._current_player

    @property
    def move_history(self):
        return list(self._move_history)
