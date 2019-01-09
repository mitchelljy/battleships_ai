from utils import *

# The icons/keys used to represent board display
chars = {'unknown':   '■',
         'hit':       'X',
         'miss':      '□',
         'sea':       '■',
         'destroyed': '*'}


# The Board class which all other boards are subclasses of
class Board:
    def __init__(self, size):
        self.size = size
        self.board = np.zeros((size, size), dtype=np.int8)

    # Getter needed to return the board, either as a copy or as a reference
    def get_board(self, copy=False):
        if copy:
            return self.board.copy()
        else:
            return self.board

    # Print the board to the screen
    def print_board(self, text):
        print(text)
        print("   ", end='')
        for i in range(self.size):
            print(i + 1, end=' ')
        print('')
        for i, x in enumerate(self.get_board()):
            print(chr(i + 65), end='  ')
            for y in x:
                print(chars[self.square_states[y]], end=' ')
            print('')


# Stores the position of placed ships
class DefenseBoard(Board):
    def __init__(self, size, ships_array):
        Board.__init__(self, size)
        self.attack_board = None
        self.square_states = {0: 'sea',
                              1: 'ship'}
        self.inv_square_states = {v: k for k, v in self.square_states.items()}
        self.ships = []
        self.available_ships = ships_array  # Stores the available ships to place

        self.init_from_array()

    # Place all available ships randomly
    def init_from_array(self):
        for ship_length in self.available_ships:
            place_random_ship(self, ship_length, [self.inv_square_states['ship']])


# Stores the positions attacked by a player
class AttackBoard(Board):
    def __init__(self, defense_board):
        Board.__init__(self, defense_board.size)
        self.defense_board = defense_board
        self.squares_left = np.sum(self.defense_board.get_board())  # The number of non-empty locations left
        self.ship_counts = self.defense_board.available_ships.copy()  # The number of ships left,  to calculate victory
        self.hits = []
        self.square_states = {0: 'unknown',
                              1: 'hit',
                              2: 'destroyed',
                              3: 'miss'}
        self.inv_square_states = {v: k for k, v in self.square_states.items()}

    # Sends a hit to the defense board, checks the outcome and then applies the change to the attack board. Returns
    # the outcome and whether or not the game is over yet
    def send_hit(self, x, y):
        assert self.legal_hit(x, y), "Invalid attack square"

        if self.defense_board.get_board()[x, y] == self.defense_board.inv_square_states['ship']:
            self.get_board()[x, y] = self.inv_square_states['hit']
            self.hits.append((x, y))
            self.squares_left -= 1

            # Determine if the ship was destroyed
            for i, ship in enumerate(self.defense_board.ships):
                if (x, y) in ship:
                    self.ship_counts[i] -= 1
                if self.ship_counts[i] == 0:
                    for crds in ship:
                        self.get_board()[crds[0], crds[1]] = self.inv_square_states['destroyed']
            return f'hit', self.squares_left == 0

        self.get_board()[x, y] = self.inv_square_states['miss']
        return 'miss', False

    # Check if the target is located within the board and is empty
    def legal_hit(self, x, y):
        for cd in [x, y]:
            if not 0 <= cd < self.size:
                return False

        if self.get_board()[x, y] != self.inv_square_states['unknown']:
            return False

        return True


# Provides an environment for the monte-carlo algorithm to simulate in
class SimulationBoard(Board):
    def __init__(self, attack_board):
        Board.__init__(self, attack_board.size)
        self.attack_board = attack_board
        self.board = self.attack_board.get_board(copy=True)
        self.square_states = {0: 'unknown',
                              1: 'hit',
                              2: 'destroyed',
                              3: 'miss',
                              4: 'ship'}
        self.inv_square_states = {v: k for k, v in self.square_states.items()}
        self.ships = []

    def simulate_ship(self):

        # Select a random ship length we haven't destroyed yet and place it onto the board in a valid locatipn
        index = np.random.choice(np.nonzero(self.attack_board.ship_counts)[0])
        length = self.attack_board.defense_board.available_ships[index]
        place_random_ship(self, length, [self.inv_square_states['miss'], self.inv_square_states['destroyed']])

        # Check if the ship intersects an existing hit. If it does, we want to emphasise it to the algorithm
        intersect = 0
        for coord in self.ships[0]:
            if coord in self.attack_board.hits:
                intersect += 1
        if intersect == len(self.ships[0]):
            intersect = 0

        # Make sure to remove all non-ship squares to avoid messing with frequencies
        sim_board = self.get_board(copy=True)
        sim_board[sim_board != self.inv_square_states['ship']] = 0

        return sim_board, intersect  # Return tuple with True if intersect, False if not

    # Reset the simulation
    def update(self, attack_board):
        self.__init__(attack_board)

