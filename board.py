from piece import Piece, King


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
