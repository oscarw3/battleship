import battleship_types as b_types
import board

class Game(object):
    def __init__(self, player_name):
        self.players = [HumanPlayer(player_name), AIPlayer()]
        self.board = board.Board([p.name for p in self.players])
        self.player_turn_index = 0 # should randomize
    
    def start_game(self):
        for ship_type in b_types.get_ship_sizes().keys():
            for player in self.players:
                player.choose_ship(ship_type, self.board)
        
        print("Ships are all set, time to play!")

        print(self.board.get_loser())
        while not self.board.get_loser():
            player = self.players[self.player_turn_index]
            attack_response = player.choose_attack(self.board)
            self.player_turn_index = (self.player_turn_index + 1) % 2
            next_player = self.players[self.player_turn_index]  

            if attack_response.sunk_ship_type:
                print("%s sunk %s's ship!"% (player.name, next_player.name))  
            elif attack_response.ship_hit:
                print("%s hit %s's ship!"% (player.name, next_player.name))  
            else: 
                print("miss by %s"% player.name)

            player = next_player
        loser = self.board.get_loser()
        print("%s has lost the game!"% loser)


    def iterate_turn(self):
        player = self.players[self.player_turn_index]
        self.player_turn_index = (self.player_turn_index + 1) % 2
        self.board.print_boards(player.name)


class Player(object):
    name = None

    def choose_ship(self, ship_type, board):
        pass  # to be implemented by subclass

    def choose_attack(self, board):
        pass  # to be implemented by subclass


class AIPlayer(Player):
    attacks = {}
    name = "AI"

    i_counter = 0  # TODO: for testing, need to remove these counters and make AI smarter
    j_counter = 0
    i_counter_attack = 0  # TODO: for testing, need to remove these counters and make AI smarter
    j_counter_attack = 0
    def choose_ship(self, ship_type, board):
         board.set_ship(b_types.Coordinate(
             self.i_counter, 
             self.j_counter), b_types.Coordinate(0, 1), ship_type, self.name)
         self.i_counter += 1
         self.j_counter += 1
    
    def choose_attack(self, board):
        # attack_resp = board.set_attack(b_types.Coordinate(
        #      self.i_counter_attack, 
        #      self.j_counter_attack), self.name)
        # self.i_counter_attack = (self.i_counter_attack + 1) % 10
        # self.j_counter_attack = (self.j_counter_attack + 1) % 10
        # return attack_resp
        return b_types.AttackResponse(False, None)


class HumanPlayer(Player):
    def __init__(self, name):
        self.name = name

    def _get_ship_direction(self):
        direction_string = input("Please select the ship direction of your choice (up, down, left, right).\n")
        if direction_string == "down":
            return b_types.Coordinate(1, 0)
        elif direction_string == "up":
            return b_types.Coordinate(-1, 0)
        elif direction_string == "right":
            return b_types.Coordinate(0, 1)
        elif direction_string == "left":
            return b_types.Coordinate(0, -1)
        else:
            print("Invalid direction! Please try again (make sure casing and spelling match)")
            return self._get_ship_direction()
        return None  # will never reach return, but removes lint error
        
    def _get_coordinate(self):
        error_msg = "Invalid Location! Try again."
        coordinate_string = input("Please select the coordinate of your choice in the format of <Letter><Number> (ie. A6).\n")
        if len(coordinate_string) < 2:
            print(error_msg)
            return self._get_coordinate()

        # first character will be converted from uppercase letter to number from 0 to 25, where the number if the letter of the alphabet
        # we don't need to worry about inbounds here since it's handled by set_ship on the board
        char = coordinate_string[0]
        row = ord(char.lower()) - 97  

        try:
            col = int(coordinate_string[1:]) - 1
            return b_types.Coordinate(row, col)
        except ValueError:
            print(error_msg)
            return self._get_coordinate()
        

    def _choose_ship(self, ship_type, board):
        coordinate = self._get_coordinate()
        direction = self._get_ship_direction()
        
        try:
            board.set_ship(coordinate, direction, ship_type, self.name)
        except b_types.BattleshipError:
            print("Invalid Coordinate! Make sure the entire ship is in bounds and it doesn't overlap with another ship.")
            self._choose_ship(ship_type, board)

    def choose_ship(self, ship_type, board):
        self.print_boards(board)
        ship_size = b_types.get_ship_sizes().get(ship_type)
        print("%s, please choose where to set your ship!"% self.name)
        print("The ship you are setting is %s, with size %s."% (ship_type.name, ship_size))
        self._choose_ship(ship_type, board)

    def _choose_attack(self, board):
        coordinate = self._get_coordinate()
        try:
            return board.set_attack(coordinate, self.name)
        except b_types.BattleshipError:
            print("Invalid Coordinate! Make sure the attack is in bounds and there isn't another attack at that location")
            return self._choose_attack(board)

    def choose_attack(self, board):
        self.print_boards(board)
        print("%s, please choose where to attack!"% self.name)
        return self._choose_attack(board)

    def _print_board(self, matrix):
        columns = [str(i) for i in range(1, len(matrix) + 1)]
        print("   %s"% columns)  # spaces to offset the row letter
        for i in range(len(matrix)):
            print("%s: %s"% (
                chr(i+97).upper(), # convert the row number to letter
                matrix[i]))

    def print_boards(self, board):  
        """
        H denotes Hit in attack board
        M denotes Miss in attack board
        H denotes Hit in ocean (ship) board
        S denotes part of ship not hit in ocean (ship) board
        """
        
        attacks_matrix, ships_matrix = board.get_matrixes(self.name)
        print("Attacks:")
        self._print_board(attacks_matrix)

        print("Ocean:")
        self._print_board(ships_matrix)

