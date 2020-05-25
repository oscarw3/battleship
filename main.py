import game

def main():
    player_name = input("Welcome to Battleships! What is your name?\n")
    game.Game(player_name).start_game()

main()
