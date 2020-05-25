import random
import battleship_types as b_types

class Player(object):
    """
    Base class for players, used by AI and Human players. Must implement name, choose_ship and choose_attack method.
    """
    name = None

    def choose_ship(self, ship_type, board):
        """
        Implemented by subclass for how to choose how the ship will be set on the board.
        """ 
        raise Exception("Unimplemented")

    def choose_attack(self, board):
        """
        Implemented by subclass for how the attack will be set on the board.
        """ 
        raise Exception("Unimplemented")


class AIPlayer(Player):
    """
    AI player that plays against a human
    """
    successful_attacks = set()
    failed_attacks = set()
    adjacent_coordinates = set()  # adjacent coordinates to failed attacks
    name = "AI"
    attack_stack = []  # list of attacks stored in a stack, see _pick_potential_coordinate for more
    potential_ship_direction = None

    def choose_ship(self, ship_type, board):
        """
        randomly chooses place to set ship in bounds, either horizontal or vertical
        """
        ship_size = b_types.get_ship_sizes().get(ship_type)

        if random.randrange(0, 2):  # to randomly decide vertical or horizontal
            vertical_offset = ship_size  
            horizontal_offset = 0
            direction = b_types.Coordinate(1, 0)
        else:
            vertical_offset = 0
            horizontal_offset = ship_size
            direction = b_types.Coordinate(0, 1)
        
        # offsets prevent ship from going off matrix
        row_val = random.randrange(0, board.get_board_size() - vertical_offset)
        col_val = random.randrange(0, board.get_board_size() - horizontal_offset)
        try:
            board.set_ship(b_types.Coordinate(
                row_val, 
                col_val), direction, ship_type, self.name)
        except b_types.BattleshipError:
            return self.choose_ship(ship_type, board)


    def _convert_int_to_coordinate(self, input_int, board_size):
        """
        assuming input is an integer from 0 to board length * board length, convert to corresponding coordinate
        """
        row = input_int // board_size
        col = input_int % board_size
        return b_types.Coordinate(row, col)

    def _convert_coordinate_to_int(self, coordinate, board_size):
        """
        assuming input is coordinate on the board, converts it to an integer version of the coordinate
        """
        return coordinate.row * board_size + coordinate.col

    def _failed_attacks_as_ints(self, board_size):
        return [ self._convert_coordinate_to_int(failed_attack, board_size) for failed_attack in self.failed_attacks]

    def _successful_attacks_as_ints(self, board_size):
        return [ self._convert_coordinate_to_int(successful_attack, board_size) for successful_attack in self.successful_attacks]

    def _adjacent_coordinates_as_ints(self, board_size):
        return [ self._convert_coordinate_to_int(adjacent_coordinate, board_size) for adjacent_coordinate in self.adjacent_coordinates]

    def _pick_unconnected_coordinate(self, board_size):
        """
        chooses an attack randomly out of any of the valid coordinates (in bounds and not previously attacked).
        try not to pick an adjacent coordinate to a failed attack, unless there are no other options.
        """
        excluded_coordinates = self._failed_attacks_as_ints(board_size) + self._successful_attacks_as_ints(board_size)
        adjacent_coordinates = self._adjacent_coordinates_as_ints(board_size)
        
        # if there is are any remaining coordinates without the adjacent ones to the failed attacks, choose out of those
        remaining_without_adjacent = [i for i in range(0, board_size * board_size) if i not in excluded_coordinates + adjacent_coordinates]
        if len(remaining_without_adjacent) > 0 :
            return self._convert_int_to_coordinate(random.choice(remaining_without_adjacent), board_size)

        # otherwise, choose out of the excluded
        unconnected_int = random.choice([i for i in range(0, board_size * board_size) if i not in excluded_coordinates])
        return self._convert_int_to_coordinate(unconnected_int, board_size)

    def _pick_potential_coordinate(self, board_size):
        """
        get_potential_coordinate uses the attack stack to help pick the successful coordinates
        if there were any attacks, they were stored in the attack stack.
        Use the last attack put in the attack stack as the next attack to iterate off of.
        if there was a potential ship direction saved (last direction that was traversed), use that plus the
        last attack to iterate to the next potential attack
        if that was already tried, use one of the other directions that haven't been attempted
        If all of the directions have been attempted, pop the last attack from the stack and try with the last attack
        If there are no attacks, return None. (We also have logic for removing potential ships from the stack whenk sunk, see: _remove_potential_ship_from_attack_stack)
        """
        if len(self.attack_stack) == 0:
            return None 

        # try using the last potential direction stored first
        if self.potential_ship_direction:
            potential_next_coordinate = self.attack_stack[-1] + self.potential_ship_direction
            if potential_next_coordinate.within_bounds(board_size) and \
                not (potential_next_coordinate in self.failed_attacks or potential_next_coordinate in self.successful_attacks):
                return potential_next_coordinate
            else:
                self.potential_ship_direction = None
                    
        # potential ship direction yielded an out of bounds or attack that was already attempted, try another direction
        # use random direction for order of trying different directions
        for direction in random.sample(b_types.ALL_DIRECTIONS, len(b_types.ALL_DIRECTIONS)): 
            potential_next_coordinate = self.attack_stack[-1] + direction
            if potential_next_coordinate.within_bounds(board_size) and \
                not (potential_next_coordinate in self.failed_attacks or potential_next_coordinate in self.successful_attacks):
                self.potential_ship_direction = direction
                return potential_next_coordinate
        
        # we exhausted all directions for this attack, try the last one
        self.attack_stack.pop()
        return self._pick_potential_coordinate(board_size)

    def _remove_potential_ship_from_attack_stack(self):
        """
        """
        curr = self.attack_stack.pop()
        while curr:
            if len(self.attack_stack) > 0 and self.potential_ship_direction and\
                (self.attack_stack[-1] + self.potential_ship_direction) == curr:
                curr = self.attack_stack.pop()
            else:
                return
            
    def choose_attack(self, board):
        """
        choose attack based on two primary strategies 
        (see _get_potential_coordinate and _pick_unconnected_coordinate for more).
        """
        board_size = board.get_board_size()
        
        coordinate = self._pick_potential_coordinate(board_size)
                    
        if not coordinate:
            coordinate = self._pick_unconnected_coordinate(board_size)
        attack_result = board.set_attack(coordinate, self.name)
        if attack_result.ship_hit:
            self.successful_attacks.add(coordinate)
            self.attack_stack.append(coordinate)
            if attack_result.sunk_ship_type:
                self._remove_potential_ship_from_attack_stack()
                self.potential_ship_direction = None 
        else: 
            self.potential_ship_direction = None
            self.failed_attacks.add(coordinate)
            for direction in b_types.ALL_DIRECTIONS:
                current_coordinate = coordinate + direction
                if current_coordinate.within_bounds(board_size):
                    self.adjacent_coordinates.add(current_coordinate)
        print("%s attacks %s%s"% (self.name, chr(coordinate.row +97).upper(), coordinate.col + 1))
        return attack_result


class HumanPlayer(Player):
    """
    For a human player to play in the terminal. Includes printing board, taking input, returning invalid inputs...etc.
    """

    def __init__(self, name):
        self.name = name

    def _get_ship_direction(self):
        """
        helper function to get ship direction from terminal input
        """
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
        """
        helper function to get coordinate from terminal input
        """
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
        """
        helper function to recursively choose ship incase of invalid input
        """
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
        """
        helper function to recursively choose attack incase of invalid input
        """
        coordinate = self._get_coordinate()
        try:
            return board.set_attack(coordinate, self.name)
        except b_types.BattleshipError:
            print("Invalid Coordinate! Make sure the attack is in bounds and there isn't another attack at that location")
            return self._choose_attack(board)

    def choose_attack(self, board):
        self.print_boards(board)
        print("The board is denoted by the following:")
        print("H = Hit Attack/Ship")
        print("M = Miss Attack")
        for ship_type, symbol in b_types.get_ship_symbols().items():
            print("%s = %s ship"% (symbol, ship_type.name))
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
        prints the board for human player to view. Adds the column and letters around the matrix
        """
        
        attacks_matrix, ships_matrix = board.get_matrixes(self.name)
        print("Attacks:")
        self._print_board(attacks_matrix)

        print("Ocean:")
        self._print_board(ships_matrix)
        