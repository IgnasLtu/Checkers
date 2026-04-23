from abc import ABC, abstractmethod


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
