from board import DefenseBoard, AttackBoard, SimulationBoard
import numpy as np


# Class that handles interaction between agent and environment
class Game:
    def __init__(self, size, ships):
        self.size = size  # Size of board, i.e. size * size = total squares
        self.ships = ships
        self.defense_board = DefenseBoard(self.size, self.ships)  # Initialise a new DefenseBoard for the env
        self.attack_board = AttackBoard(self.defense_board)  # Initialise a new AttackBoard for the env
        self.simulate_board = SimulationBoard(self.attack_board)  # Initialise a new SimulationBoard for the env

        self.attack_board.print_board("=Initial State=")

        # Count of the number of moves the agent has made
        self.count = 0

    # Reset the entire env and return the initial state
    def reset(self):
        self.__init__(self.size, self.ships)
        return self.attack_board

    # Takes a step in the environment using the given size * size set of frequencies
    def step(self, probs):
        x, y = np.unravel_index(probs.argmax(), probs.shape)

        while not self.attack_board.legal_hit(x, y):
            probs[x, y] = 0
            x, y = np.unravel_index(probs.argmax(), probs.shape)

        outcome, done = self.attack_board.send_hit(x, y)

        return self.attack_board, outcome, done



