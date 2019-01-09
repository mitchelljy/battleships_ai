from utils import *
import threading, os

import numpy as np
import matplotlib.pyplot as plt


# Class for an AI based on monte-carlo simulation
class AI:
    def __init__(self, env, samples):
        self.env = env
        self.move_sim = samples  # The number of moves to simulate
        self.priority = 5  # The priority to give simulations that intersect hits

    # Evaluate the model by running it many times and averaging the scores
    def eval_model(self, evals):
        scores = []
        for i in range(evals):
            scores.append(self.run(i))
            print(f"Game {i}/{evals} \n Score: {scores[-1]}")
        print(np.mean(scores))

    # Take in the board state and return probabilities of a ship being somewhere
    def monte_carlo(self, state, out_path):
        simulations = []

        #
        for i in range(self.move_sim):
            self.env.simulate_board.update(state)
            brd, intersect = self.env.simulate_board.simulate_ship()

            # If we intersect a hit, take into account priority and overlap
            if intersect:
                for i in range(self.priority):
                    for i in range(intersect):
                        simulations.append(brd)
            simulations.append(brd)

        # Mean the ship simulations down the stacked axis to calculate percentages
        simulations = np.array(simulations)
        percentages = np.mean(simulations, axis=0)

        # Output a heatmap if specified
        if out_path != '':
            fig = plt.figure(figsize=(8, 8))
            fig.add_subplot(1, 2, 1)
            plt.imshow(percentages, cmap='hot', interpolation='nearest')
            fig.add_subplot(1, 2, 2)
            plt.imshow(state.get_board() * 5, cmap='bwr', interpolation=None)
            plt.savefig(out_path)
            plt.close(fig)

        return percentages

    # Get the AI to run a game of battleships on it's own for testing
    def run(self, r_count):
        s = self.env.reset()
        done = False
        count = 0
        while not done:
            count += 1
            if not os.path.exists(f'save_file_{r_count}/'):
                os.mkdir(f'save_file_{r_count}/')
            s, done = self.env.step(self.monte_carlo(s, f'save_file_{r_count}/{count}.png'))
            # s.print_board()
        print(f"SCORE: {np.count_nonzero(s.get_board() == 0)}")
        return np.count_nonzero(s.get_board() == 0)

    # Use the monte carlo simulation algorithm to predict a move against a player and make that move
    def move(self):
        return self.env.step(self.monte_carlo(self.env.attack_board, ''))



