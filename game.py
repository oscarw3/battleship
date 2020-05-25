import random
import battleship_types as b_types
import board
import players


class Game(object):
    """
    Primary class for the battleships game
    """
    def __init__(self, player_name):
        self.players = [players.HumanPlayer(player_name), players.AIPlayer()]
        self.board = board.Board([p.name for p in self.players])
        self.player_turn_index = random.randrange(0, 2)
        self.turn_count = 1  # counts both players turns, ie. one players turn here counts as a single turn
    
    def start_game(self):
        """
        start game iterates through choosing ships, and choosing attacks.
        """
        print("Let's start by setting the ships!")
        for ship_type in b_types.get_ship_sizes().keys():
            for player in self.players:
                player.choose_ship(ship_type, self.board)
        
        print("Ships are all set, time to play!")

        print(self.board.get_loser())
        while not self.board.get_loser():
            self.turn_count += 1
            print("Turn %s"% str(self.turn_count // 2))  # Both players going counts as a single turn, hence the division
            player = self.players[self.player_turn_index]
            attack_result = player.choose_attack(self.board)
            self.player_turn_index = (self.player_turn_index + 1) % 2
            next_player = self.players[self.player_turn_index]  

            if attack_result.sunk_ship_type:
                print("%s sunk %s's ship!"% (player.name, next_player.name))  
            elif attack_result.ship_hit:
                print("%s hit %s's ship!"% (player.name, next_player.name))  
            else: 
                print("miss by %s"% player.name)

            player = next_player
        loser = self.board.get_loser()
        print("%s has lost the game!"% loser)
