import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from checkers import (
    Piece, King, Board, HumanPlayer, AIPlayer,
    PlayerFactory, FileHandler, Game
)


class TestPiece(unittest.TestCase):
    def test_piece_creation(self):
        piece = Piece("white", 5, 0)
        self.assertEqual(piece.color, "white")
        self.assertEqual(piece.row, 5)
        self.assertEqual(piece.col, 0)
        self.assertFalse(piece.is_captured)

    def test_piece_symbol_white(self):
        self.assertEqual(Piece("white", 0, 0).symbol(), "w")

    def test_piece_symbol_black(self):
        self.assertEqual(Piece("black", 0, 0).symbol(), "b")

    def test_king_symbol_white(self):
        self.assertEqual(King("white", 0, 0).symbol(), "W")

    def test_king_symbol_black(self):
        self.assertEqual(King("black", 0, 0).symbol(), "B")

    def test_piece_capture(self):
        piece = Piece("white", 3, 3)
        piece.capture()
        self.assertTrue(piece.is_captured)

    def test_king_is_instance_of_piece(self):
        self.assertIsInstance(King("white", 0, 0), Piece)

    def test_piece_row_col_setter(self):
        piece = Piece("white", 3, 3)
        piece.row = 5
        piece.col = 1
        self.assertEqual(piece.row, 5)
        self.assertEqual(piece.col, 1)


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.board.setup_pieces()

    def test_initial_white_piece_count(self):
        self.assertEqual(len(self.board.white_pieces), 12)

    def test_initial_black_piece_count(self):
        self.assertEqual(len(self.board.black_pieces), 12)

    def test_in_bounds_valid(self):
        self.assertTrue(self.board.in_bounds(0, 0))
        self.assertTrue(self.board.in_bounds(7, 7))

    def test_in_bounds_invalid(self):
        self.assertFalse(self.board.in_bounds(-1, 0))
        self.assertFalse(self.board.in_bounds(8, 8))

    def test_get_piece_returns_none_on_empty(self):
        self.assertIsNone(self.board.get_piece(3, 0))

    def test_get_piece_returns_piece(self):
        piece = self.board.get_piece(0, 1)
        self.assertIsNotNone(piece)
        self.assertEqual(piece.color, "black")

    def test_move_piece(self):
        piece = self.board.get_piece(5, 0)
        self.board.move_piece(piece, 4, 1)
        self.assertEqual(self.board.get_piece(4, 1), piece)
        self.assertIsNone(self.board.get_piece(5, 0))

    def test_capture_piece_removes_from_list(self):
        piece = self.board.get_piece(0, 1)
        self.board.capture_piece(piece)
        self.assertEqual(len(self.board.black_pieces), 11)
        self.assertTrue(piece.is_captured)

    def test_promotion_white_reaches_row_0(self):
        board = Board()
        piece = Piece("white", 1, 1)
        board._grid[1][1] = piece
        board._white_pieces.append(piece)
        board.move_piece(piece, 0, 0)
        self.assertIsInstance(board.get_piece(0, 0), King)

    def test_promotion_black_reaches_row_7(self):
        board = Board()
        piece = Piece("black", 6, 1)
        board._grid[6][1] = piece
        board._black_pieces.append(piece)
        board.move_piece(piece, 7, 0)
        self.assertIsInstance(board.get_piece(7, 0), King)

    def test_has_pieces_true(self):
        self.assertTrue(self.board.has_pieces("white"))
        self.assertTrue(self.board.has_pieces("black"))

    def test_has_pieces_false_after_all_captured(self):
        for piece in list(self.board.white_pieces):
            self.board.capture_piece(piece)
        self.assertFalse(self.board.has_pieces("white"))


class TestPieceMoves(unittest.TestCase):
    def test_white_piece_moves_upward(self):
        board = Board()
        piece = Piece("white", 4, 4)
        board._grid[4][4] = piece
        board._white_pieces.append(piece)
        destinations = [(m[0], m[1]) for m in piece.get_possible_moves(board)]
        self.assertIn((3, 3), destinations)
        self.assertIn((3, 5), destinations)

    def test_black_piece_moves_downward(self):
        board = Board()
        piece = Piece("black", 3, 3)
        board._grid[3][3] = piece
        board._black_pieces.append(piece)
        destinations = [(m[0], m[1]) for m in piece.get_possible_moves(board)]
        self.assertIn((4, 2), destinations)
        self.assertIn((4, 4), destinations)

    def test_piece_captures_in_all_4_directions(self):
        """Regular piece can capture backwards (chain capture rule)."""
        board = Board()
        white = Piece("white", 4, 4)
        black_behind = Piece("black", 5, 3)
        board._grid[4][4] = white
        board._grid[5][3] = black_behind
        board._white_pieces.append(white)
        board._black_pieces.append(black_behind)
        captures = white.get_captures(board)
        destinations = [(m[0], m[1]) for m in captures]
        self.assertIn((6, 2), destinations)

    def test_capture_move_available(self):
        board = Board()
        white = Piece("white", 4, 4)
        black = Piece("black", 3, 3)
        board._grid[4][4] = white
        board._grid[3][3] = black
        board._white_pieces.append(white)
        board._black_pieces.append(black)
        captures = [m for m in white.get_possible_moves(board) if m[2] is not None]
        self.assertTrue(len(captures) > 0)

    def test_chain_capture_follow_up(self):
        """After first capture, follow-up capture should be available."""
        board = Board()
        white = Piece("white", 4, 4)
        black1 = Piece("black", 3, 3)
        black2 = Piece("black", 1, 1)
        board._grid[4][4] = white
        board._grid[3][3] = black1
        board._grid[1][1] = black2
        board._white_pieces.append(white)
        board._black_pieces.extend([black1, black2])
        board.move_piece(white, 2, 2, black1)
        follow_ups = white.get_captures(board)
        self.assertTrue(len(follow_ups) > 0)
        self.assertEqual(follow_ups[0][:2], (0, 0))

    def test_king_moves_multiple_squares(self):
        board = Board()
        king = King("white", 4, 4)
        board._grid[4][4] = king
        board._white_pieces.append(king)
        destinations = [(m[0], m[1]) for m in king.get_possible_moves(board)]
        self.assertIn((2, 2), destinations)
        self.assertIn((0, 0), destinations)

    def test_king_captures_from_distance(self):
        board = Board()
        king = King("white", 7, 7)
        black = Piece("black", 4, 4)
        board._grid[7][7] = king
        board._grid[4][4] = black
        board._white_pieces.append(king)
        board._black_pieces.append(black)
        captures = king.get_captures(board)
        landed = [(m[0], m[1]) for m in captures]
        self.assertIn((3, 3), landed)
        self.assertIn((2, 2), landed)

    def test_king_blocked_by_own_piece(self):
        board = Board()
        king = King("white", 4, 4)
        own = Piece("white", 2, 2)
        board._grid[4][4] = king
        board._grid[2][2] = own
        board._white_pieces.extend([king, own])
        destinations = [(m[0], m[1]) for m in king.get_possible_moves(board)]
        self.assertNotIn((2, 2), destinations)
        self.assertNotIn((1, 1), destinations)


class TestPlayerFactory(unittest.TestCase):
    def test_create_human_player(self):
        player = PlayerFactory.create_player("human", "Alice", "white")
        self.assertIsInstance(player, HumanPlayer)
        self.assertEqual(player.name, "Alice")

    def test_create_ai_player(self):
        player = PlayerFactory.create_player("ai", "Bot", "black")
        self.assertIsInstance(player, AIPlayer)

    def test_invalid_type_raises_error(self):
        with self.assertRaises(ValueError):
            PlayerFactory.create_player("robot", "X", "white")

    def test_case_insensitive(self):
        player = PlayerFactory.create_player("HUMAN", "Alice", "white")
        self.assertIsInstance(player, HumanPlayer)


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.fh = FileHandler(save_dir="test_saves")
        self.board = Board()
        self.board.setup_pieces()

    def tearDown(self):
        import shutil
        if os.path.exists("test_saves"):
            shutil.rmtree("test_saves")

    def test_save_creates_file(self):
        path = self.fh.save_game(self.board, "white", "test_save.csv")
        self.assertTrue(os.path.exists(path))

    def test_load_returns_correct_data(self):
        path = self.fh.save_game(self.board, "black", "test_load.csv")
        data, current_color = self.fh.load_game(path)
        self.assertEqual(current_color, "black")
        self.assertEqual(len(data), 24)

    def test_load_nonexistent_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            self.fh.load_game("nonexistent.csv")

    def test_save_and_load_roundtrip(self):
        path = self.fh.save_game(self.board, "white", "roundtrip.csv")
        board2 = Board()
        data, color = self.fh.load_game(path)
        board2.load_from_data(data)
        self.assertEqual(len(board2.white_pieces), 12)
        self.assertEqual(len(board2.black_pieces), 12)


class TestGame(unittest.TestCase):
    def setUp(self):
        p1 = PlayerFactory.create_player("ai", "Bot1", "white")
        p2 = PlayerFactory.create_player("ai", "Bot2", "black")
        self.game = Game(p1, p2)
        self.game.start()

    def test_initial_no_winner(self):
        self.assertIsNone(self.game.check_winner())

    def test_switch_player(self):
        first = self.game.current_player
        self.game.switch_player()
        self.assertNotEqual(first, self.game.current_player)
        self.game.switch_player()
        self.assertEqual(first, self.game.current_player)

    def test_winner_when_no_white_pieces(self):
        for piece in list(self.game.board.white_pieces):
            self.game.board.capture_piece(piece)
        self.assertEqual(self.game.check_winner().color, "black")

    def test_move_history_empty_at_start(self):
        self.assertEqual(len(self.game.move_history), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
