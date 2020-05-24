
from enum import Enum
from collections import namedtuple

class ShipType(Enum):
  Carrier = "Carrier"
  Battleship = "Battleship"
  Cruiser = "Cruiser"
  Submarine = "Submarine"
  Destroyer = "Destroyer"

def get_ship_sizes():
  return {
    ShipType.Carrier: 5, 
    ShipType.Battleship: 4, 
    ShipType.Cruiser: 3, 
    ShipType.Submarine: 3,
    ShipType.Destroyer: 2,
  }

def get_ship_symbols():
  return {
    ShipType.Carrier: "C", 
    ShipType.Battleship: "B", 
    ShipType.Cruiser: "R", 
    ShipType.Submarine: "S",
    ShipType.Destroyer: "D",
  }


class Coordinate(namedtuple('Coordinate',['row','col'])):
  def within_bounds(self, board_size):
    if self.row < 0 or self.col < 0 or \
      self.row >= board_size or self.col >= board_size:
      return False
    return True

  def __add__(self, other):  # only handle adding two tuples, not integers
    return Coordinate(self.row + other.row, self.col + other.col)

  def __mul__(self, other):  # only handle multiplying by integer, not tuple
    return Coordinate(self.row * other, self.col * other)

class BattleshipError(Exception):
  pass

invalid_coordinate = BattleshipError("Invalid Coordinate")

class AttackResponse(namedtuple('AttackResponse',['ship_hit','sunk_ship_type'])):
  pass
