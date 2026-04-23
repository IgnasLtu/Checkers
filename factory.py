from player import Player, HumanPlayer, AIPlayer


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
