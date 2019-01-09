from game_env_interface import Game
from ai import AI
from utils import letter_to_coords
import argparse

import numpy as np

winner = {(True, False): 'Computer',
          (False, True): 'Player'}

# Takes size paramater (the board will be size * size) and ships as an array of lengths)
def init_game(size, ships, samples):
    # Build the AI boards and init the AI
    ai_env = Game(size, ships)
    computer = AI(ai_env, samples)

    # Build the Player boards
    player_env = Game(size, ships)

    # Cycle through each players turn until a player wins
    c_done = False
    p_done = False
    while not c_done and not p_done:
        c_state, c_outcome, c_done = computer.move()
        p_state, p_outcome, p_done = player_env.step(execute_player_move(player_env))

        c_state.print_board(f"=Your Board (Computer Target Ships)= [Last Outcome: {c_outcome}]")
        p_state.print_board(f"=Your Target Ships= [Last Outcome: {p_outcome}]")

    print("="*10 + "GAME OVER" + "="*10)
    print(f"The winner is: {winner[(c_done, p_done)]}")


# Get the input move from the player
def execute_player_move(player_env):
    p_move = np.zeros(shape=[player_env.size, player_env.size])
    x, y = player_input(player_env)
    p_move[x, y] = 1
    return p_move


# Validate the input move
def player_input(player_env):
    success = False
    while not success:
        ltr, nbr = input("Enter letter: ").upper(), input("Enter number: ")
        try:
            x, y = letter_to_coords(ltr, nbr)
            while player_env.attack_board.get_board()[x, y] != 0:
                x, y = player_input()
            success = True
        except:
            print("Invalid Input!")
            continue
    return x, y


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--board_size', help='The size of the board, default: 10', default=10)
    parser.add_argument('--ship_sizes', help='Array of ship sizes to randomly place, default: "5,4,3,3,2"', default='5,4,3,3,2')
    parser.add_argument('--monte_carlo_samples', help='The number of samples to get the algorithm to do, default: 10000', default=10000)

    args = parser.parse_args()

    try:
        print("Chosen args: ", args.board_size, [int(x) for x in args.ship_sizes.split(',')], args.monte_carlo_samples)
        init_game(args.board_size, [int(x) for x in args.ship_sizes.split(',')], args.monte_carlo_samples)
    except:
        print("Incorrect Args!")
        exit(1)
