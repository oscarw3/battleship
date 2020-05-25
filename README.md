# Oscar's Battleship Game with simple AI

This is my attempt at building the classic battleship game with a relatively simple AI, without machine learning.

## Setup
Install Python 3
`python main.py`
 
The instructions should be self explanatory after that! It's easiest to play the game if the terminal window is large enough/ the text is small enough such that it includes all text relevant to the turn.

I used the rules based on this youtube tutorial: [https://www.youtube.com/watch?v=RY4nAyRgkLo](https://www.youtube.com/watch?v=RY4nAyRgkLo)

## Implementation Approach for game
I had a `Game` class, which had logic for deciding when the game should continue, end, decide how to iterate through the game.

I had a `Board` class, which contained logic for the state of the game (which attack/ship was on which coordinate). 

I had a `Player` base class, with two player subclasses, `HumanPlayer` and `AIPlayer`.
I also had a `battleship_types.py` file, with some simple types with methods, for example coordinate,
with methods for operations on the coordinates, and the length of ships.

The idea is it would be easy to extend by adding new players (maybe an ML version of the AI, or a test dummy AI player, or make the game two human players instead of against the AI). Having the board class contain the state of the game also meant it's more difficult to accidentally expose data the AI is not supposed to see. In the board, I tried to keep only 1 copy of most of the data and generate the actual board that players see on read (the only exception is the number of coordinates remaining for each ship, to make that calculation a little easier).

I added some basic, simple validation, but not extensive (ie. added spaces).

## Implementation for AI
I opted to just randomly choose where to place ships on the board. This is because I'm not as familiar with other people's playing styles, so don't want to make a decision based on assumptions I have and unless I know what they're likely to do, I don't think it makes sense to optimize this.

For choosing the attack, there are two primary methods:

 - If there was no previous attack or if all the attacks have been eliminated from the stack, pick a random coordinate that hasn't been attacked (first attempt coordinates that are at least not adjacent to any other attack since the shortest ship only has a length of 2). 
 - When there was a successful attack, store the attack in a stack, and the direction it moved in (if no direction, store none). Move in that direction if provided, otherwise pick a random direction, assuming the attack hasn't been done before and the attack is in bounds. If all options are exhausted, remove the coordinate from the attack stack and try again with the previous attack.

 See more in `AIPlayer` in `players.py`.

### Potential Optimizations
This solution works well for ships that aren't right next to each other, but runs into issues for some situations if two ships are placed next to each other. For example, if there is a 3 length ship horizontally, and another ship placed vertically right next to the end of the horizontal ship, the AI will think it sunk a 4 length ship and remove all of those from the stack. This is more difficult to code since the AI doesn't know for sure, so I chose to not implement this part for now. There are also easier minor optimizations I could do like adding a cap on the length of the ships removed based on which ships are still in play, but due to time constraints I chose not to implement. 

I also chose not to implement a learning portion of the AI in this case since I'm less familiar with ML techniques that would work, which is another potential optimization. An ML version of choosing ships could also work based on data of where most people place their ships and what typically works best.
