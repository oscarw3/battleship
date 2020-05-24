import battleship_types as b_types

class Board(object):
    def __init__(self, player_names):
        self.board_size = 10
        self.attacks = {}  # player_name to set of coordinates
        self.ships = {}  # player_name to dict of coordinates and ship types
        self.ships_health_count = {}  # player_name to dict of ship types and type of ships
        if len(player_names) != 2:
            raise b_types.BattleshipError("Invalid number of players")

        for player_name in player_names:
            self.attacks[player_name] = set()  # set of coordinates
            self.ships[player_name] = {}  # coordinates to ship types
            self.ships_health_count[player_name] = self._init_ships_health_count(player_name)
    
    def _get_opponents_attacks(self, player_name):
        for opponent_name, attacks in self.attacks.items():
            if opponent_name != player_name:
                return attacks

    def _decrement_opponents_ships(self, player_name, ship_type):
        for opponent_name, ships_health_count in self.ships_health_count.items():
            if opponent_name != player_name:
                ships_health_count[ship_type] -= 1

    def _get_opponents_ships(self, player_name):
        for opponent_name, ships in self.ships.items():
            if opponent_name != player_name:
                return ships

    def _get_opponents_ships_health_count(self, player_name):
        for opponent_name, ships_health_count in self.ships_health_count.items():
            if opponent_name != player_name:
                return ships_health_count

    def _init_ships_health_count(self, player_name):
        return b_types.get_ship_sizes() 

    def _validate_coordinate_within_bounds(self, coordinate):
        if not coordinate.within_bounds(self.board_size):
            raise b_types.invalid_coordinate

    def get_loser(self):
        for player_name, ships_health in self.ships_health_count.items():
            total_count = 0
            for ship_health_count in ships_health.values():
                total_count += ship_health_count
            if total_count <= 0:
                return player_name
        return None 

    def set_ship(self, 
        starting_coordinate, direction, ship_type, player_name):
        # must validate all coordinates before setting ship
        for i in range(b_types.get_ship_sizes().get(ship_type)):
            current_coordinate = starting_coordinate + direction * i
            self._validate_coordinate_within_bounds(current_coordinate)
            if self.ships[player_name].get(current_coordinate):
                raise b_types.invalid_coordinate


        for i in range(b_types.get_ship_sizes().get(ship_type)):
            current_coordinate = starting_coordinate + direction * i
            self.ships[player_name][current_coordinate] = ship_type

    def set_attack(self, coordinate, player_name):
        self._validate_coordinate_within_bounds(coordinate)
        if coordinate in self.attacks[player_name]:
            raise b_types.invalid_coordinate
        self.attacks[player_name].add(coordinate)
        opponent_ships = self._get_opponents_ships(player_name)
        if opponent_ships.get(coordinate):
            ship_type = opponent_ships[coordinate]
            self._decrement_opponents_ships(player_name, ship_type)
            if self._get_opponents_ships_health_count(player_name)[ship_type] <= 0:
                return b_types.AttackResponse(True, ship_type)
            else:
                return b_types.AttackResponse(True, None)
        return b_types.AttackResponse(False, None)

    def _create_empty_matrix(self):
        return [[' ' for i in range(self.board_size)] for j in range(self.board_size)]

    def get_matrixes(self, player_name):  
        """
        H denotes Hit in attack board
        M denotes Miss in attack board
        H denotes Hit in ocean (ship) board
        S denotes part of ship not hit in ocean (ship) board
        """
        
        opponents_ships = self._get_opponents_ships(player_name)

        attacks_matrix = self._create_empty_matrix()
        for attack_coordinate in self.attacks[player_name]:
            if opponents_ships.get(attack_coordinate):
                attacks_matrix[attack_coordinate.row][attack_coordinate.col] = 'H'
            else:
                attacks_matrix[attack_coordinate.row][attack_coordinate.col] = 'M'

        opponents_attacks = self._get_opponents_attacks(player_name)
        ships_matrix = self._create_empty_matrix()
        
        for ship_coordinate, ship_type in self.ships[player_name].items():
            if ship_coordinate in opponents_attacks:
                ships_matrix[ship_coordinate.row][ship_coordinate.col] = 'H'
            else:
                ships_matrix[ship_coordinate.row][ship_coordinate.col] = b_types.get_ship_symbols().get(ship_type)

        return attacks_matrix, ships_matrix
