import random 

DIRS = [(0,-1),(0,1),(-1,0),(1,0)] # 0,-1 is up and -1,0 is left, as screen starts at top level then 
                                   # positive numbers increment it downwards, so -1 means move 1 in opposite dirxn
                                   # index 0 is up, 1 is down, 2 is left, 3 is right

OPPOSITE = {0:1,1:0,2:3,3:2} # opposite of each direction mapped using a dictionary as snake cant move opposite directions.

class SnakeEnv:
    def __init__(self, size=12, seed=None, max_idle=100):

        """def means “Im defining a recipe.” 
        __init__ is a special recipe that runs automatically when you make a new game.,
          self means “this particular game.”
          If you have two games running, self keeps their snakes separate.
          size=12 is a setting with a default: the grid is 12 by 12 unless you say otherwise.
          seed=None controls luck. Give it a number and the “random” food spots repeat identically every time. None means no fixed pattern.
          max_idle=100 means “if the snake wanders 100 moves without eating, we stop the game.”
            """
        
        if size < 3:
            raise ValueError("Board size must be at least 3")
        if max_idle <= 0:
            raise ValueError("max_idle must be positive")

        self.size = size
        self.max_idle = max_idle
        self.rng=random.Random(seed)  # just a random number generator, can be used at a list using .choice to randomly pick one element using the seed/dice given
        self.reset()

        """self.size = size means “this game remembers its grid size.” Without self., the value would be forgotten when the recipe ends.
        self.max_idle = max_idle does the same for the wander limit.
        random.Random(seed) creates this game’s own dice. We give it its own dice so the seed only affects this game. rng stands for “random number generator.”
        seed is None so game will be entirely random, if we pass some value then the fruits will spawn at same postions.
        self.reset() starts the first round, so the game is ready right after you build it.
        Seed = Starting state of the random generator.
        Same seed = Same pseudo-random sequence.
        Different seed = Different sequence.
        Fixed seeds = Reproducible experiments."""

    def reset(self):
        c = self.size//2  
        # c is center of the board, as the size is 12x12, center is 6x6, so 12//2 auto gives 6.
        # // is floor division, it removes the decimals from the number and only gives raw numbers.

        # snake is a list of squares, head is at center and the 2 squares/body is as c,c+1 and c,c+2
        #  |  (c,c)
        #  |  (c,c+1)
        #  |  (c,c+2)
        
        self.snake = [(c,c),(c,c+1),(c,c+2)]

        self.heading = 0      # snakes starts facing up as 0 is up 

        self.score = 0        # how many fruits eaten. reset it to 0
        self.steps = 0        # how many steps taken/ reset is to 0
        self.idle = 0         # idle counter for max_idle, if it reached 100 then games auto ends
        self.done = False     # game is done? False as game is about to start and its not done

        self._place_food()    # puts the first good on the board
 
        return None # hands back what the snake can "see". important for MLP later


    def _place_food(self):  # underscore in _place_food is a naming habit to tell that this method should be only used inside the class and not outside

        """range(self.size) means the numbers 0 up to size minus 1. For 12, that’s 0 to 11, which are the 12 columns.
        Two loops, one inside the other, visit every square: (0,0), (0,1), (0,2) ... (11,11). That’s 144 squares.
        (x, y) not in self.snake asks “is this square missing from the snake’s list?” If yes, it’s empty, so it goes into free.
        The one-line version in the real code is called a list comprehension. It’s the same thing, squeezed into one line. Read it left to right: “make a list of (x, y) for each x, for each y, but only if that square isn’t in the snake.”
        Why build a list of free squares first? The lazy alternative is picking any random square and retrying if it’s covered by the snake. That can loop for a long time when the snake is huge. Making the free list first guarantees one pick always works.
        Line 3: if not free:
        An empty list counts as “false” in Python, so not free means “there are no free squares.” That only happens when the snake fills the entire board, which means the snake won.
        Lines 4 and 5
        self.done = True: the game is over (a win).
        self.food = None: there’s nowhere to put food, so None means “no food exists.”
        Lines 6 and 7: else:
        There’s at least one free square, so:
        choice picks one item from the list at random. We use self.rng, the game’s private dice from earlier, so a seed makes this repeatable."""

        free = [(x,y) for x in range(self.size)
                for y in range(self.size) if (x,y) not in self.snake]

        if not free: # if free is false i.e has 0 elements
            self.done = True
            self.food = None

        else:
            self.food = self.rng.choice(free)


    def _blocked(self,p): 

        """The goal: answer “if the head went to square p, would that be a crash?” It returns True or False.
        def _blocked(self, p):
        p is the square we’re asking about, a pair like (5, 3).
        
        x, y = p
        Unpacks the pair into two named variables. If p is (5, 3), then x is 5 and y is 3. We need them separately to check each side of the board.
        
        out = x < 0 or y < 0 or x >= self.size or y >= self.size
        This checks “is the square off the board?” The board runs from 0 to 11, so:
        
        x < 0: too far left
        y < 0: too far up
        x >= self.size: too far right (12 or more is off the board)
        y >= self.size: too far down
        
        or means “if any of these is true, the whole thing is true.” So out is True if the square is outside on any side.
        
        return out or p in self.snake
        Two reasons a square is blocked: it’s off the board (out), or the snake’s body is already there (p in self.snake). If either is true, it returns True.
        
        Why a separate helper? observe() will call it 4 times to check the squares around the head for the danger inputs, so it’s written once and reused."""

        x,y = p
        out = x<0 or y<0 or x>=self.size or y>=self.size

        return out or p in self.snake  # either returns true if the block is outside the board or true if p is already inside the snakes body(self.snake)
                                       # in both cases its blocked and at a wrong postion
    
    def step(self, action):
    # action is a number: 0 up, 1 down, 2 left, 3 right.
    # This method moves the snake exactly one square.

    # ---------- PART 1: work out where the head will go ----------
        if action == OPPOSITE[self.heading]:
            # OPPOSITE[self.heading] is the direction that would make a U-turn.
            # If the player asks for that, the snake would fold into its own neck.
            action = self.heading
            # So we ignore the request and keep going the way we were already going.

        self.heading = action
        # Remember the direction we are now facing.
        # Next turn we need it to catch U-turns.

        dx, dy = DIRS[action]
        # Look up the move for this direction, e.g. up gives (0, -1).
        # dx is how far to move across, dy is how far to move down.

        hx, hy = self.snake[0]
        # snake[0] is the head (the list is head first).
        # hx is the head's column, hy is the head's row.

        new = (hx + dx, hy + dy)
        # The square the head is about to enter.
        # Nothing has moved yet, we have only calculated the destination.

        self.steps += 1
    # Count this move in the total number of moves.

        self.idle += 1
        # Count one more move without eating.
        # If this gets too high, the snake is probably circling, so we stop it.

        # ---------- PART 2: did the snake crash? ----------

        eating = new == self.food
        # True if the square we are moving into holds the food.

        if self._blocked(new):
            # Crash: hit a wall, or hit the snake's own body.
            self.done = True
            # Mark the game as over.
            return
            # Leave the method right now so the moving code below never runs.

        # ---------- PART 3: actually move ----------

        self.snake.insert(0, new)
        # Put the new head at the front of the list (position 0).
        # The snake is now one square longer.

        if eating:
            self.score += 1
            # One more food eaten.

            self.idle = 0
            # Reset the wander counter, since we just ate.

            self._place_food()
            # Drop a new piece of food somewhere empty.
            # We do NOT remove the tail here, so the snake stays longer (it grew).
        else:
            self.snake.pop()
            # No food, so remove the last item (the tail).
            # Added a head and removed a tail, so the snake slides forward
            # without changing length.

        if self.idle >= self.max_idle:
            # Too many moves without eating (default 100).
            self.done = True
            # End the game so snakes that run in circles get a bad score.

    def observe(self):
    # Turns the board into 12 numbers (0.0 or 1.0) for the neural network.
    # Layout: [4 danger] + [4 heading] + [4 food direction]

        hx, hy = self.snake[0]
        # Head position. hx is the column, hy is the row.
        # Every input is measured relative to the head.

        # ---------- DANGER (4 numbers) ----------
        danger = [float(self._blocked((hx + dx, hy + dy))) for dx, dy in DIRS]
        # For each direction (up, down, left, right, in DIRS order):
        #   1. Compute the square next to the head: (hx + dx, hy + dy)
        #   2. Ask _blocked: would stepping there crash? (True or False)
        #   3. float() converts True to 1.0 and False to 0.0
        # Example: [0.0, 1.0, 0.0, 0.0] means only "down" is dangerous.

        # ---------- HEADING (4 numbers) ----------
        heading = [float(i == self.heading) for i in range(4)]
        # One-hot encoding: exactly one slot is 1.0, the rest are 0.0.
        # i goes 0, 1, 2, 3. The slot matching our current direction becomes 1.0.
        # Example: facing up gives [1.0, 0.0, 0.0, 0.0].
        # We avoid feeding the raw number 0 to 3, because the network would
        # treat "3" as bigger than "0", which means nothing for directions.

        # ---------- FOOD DIRECTION (4 numbers) ----------
        fx, fy = self.food if self.food else (hx, hy)
        # Unpack the food square. If there is no food (snake filled the board,
        # food is None), use the head's own square so the line below does not crash.

        food = [float(fy < hy), float(fy > hy), float(fx < hx), float(fx > hx)]
        # Four yes/no questions, in the same order as DIRS:
        #   fy < hy : food row is smaller, so food is ABOVE  (up)
        #   fy > hy : food is BELOW                          (down)
        #   fx < hx : food column is smaller, so food is LEFT
        #   fx > hx : food is to the RIGHT
        # We use direction instead of exact coordinates so the same rule
        # ("food is on my left, go left") works anywhere on the board.

        return danger + heading + food
        # Joins the three lists into one list of 12 numbers.
        # This length (12) must match the first layer size of the MLP.



env = SnakeEnv(seed=1)

print(env.snake)
env.step(0)
print(env.snake)
env.step(1)
print(env.snake)
env.step(2)
print(env.snake)
env.step(2)
print(env.snake)

for _ in range(10):
    env.step(0)
print(env.done)

env = SnakeEnv(seed=1)
env.food = (4, 4)             # force the food so we know the answer
print(env.observe())
# expected: [0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
print(len(env.observe()))