from factory import PlayerFactory
from game import Game
from file_handler import FileHandler


def get_player_setup(player_num: int, color: str) -> tuple:
    print(f"\n--- Player {player_num} ({color}) ---")
    while True:
        ptype = input("Type (human/ai): ").strip().lower()
        if ptype in ["human", "ai"]:
            break
        print("Enter 'human' or 'ai'.")
    if ptype == "human":
        name = input("Name: ").strip() or f"Player{player_num}"
    else:
        name = input("AI name (Enter = Bot): ").strip() or "Bot"
    return ptype, name


def main():
    print("Welcome to Checkers!")
    print("\nIn-game commands: save, quit, board, help")

    while True:
        print("\nMenu")
        print("[1] New game")
        print("[2] Load saved game")
        print("[3] Exit")

        choice = input("Choice: ").strip()

        if choice == "1":
            p1_type, p1_name = get_player_setup(1, "white")
            p2_type, p2_name = get_player_setup(2, "black")
            player1 = PlayerFactory.create_player(p1_type, p1_name, "white")
            player2 = PlayerFactory.create_player(p2_type, p2_name, "black")
            game = Game(player1, player2)
            game.start()
            game.run()

        elif choice == "2":
            fh = FileHandler()
            saves = fh.list_saves()
            if not saves:
                print("No saved games found.")
                continue
            print("\nSaved games:")
            for i, s in enumerate(saves):
                print(f"  [{i}] {s}")
            try:
                idx = int(input("Choose number: "))
                filepath = f"saves/{saves[idx]}"
                p1_type, p1_name = get_player_setup(1, "white")
                p2_type, p2_name = get_player_setup(2, "black")
                player1 = PlayerFactory.create_player(p1_type, p1_name, "white")
                player2 = PlayerFactory.create_player(p2_type, p2_name, "black")
                game = Game(player1, player2)
                game.load(filepath)
                game.run()
            except (ValueError, IndexError):
                print("Invalid choice.")

        elif choice == "3":
            print("See you later!")
            break
        else:
            print("Enter 1, 2 or 3.")


if __name__ == "__main__":
    main()
