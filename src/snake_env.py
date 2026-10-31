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
    
    def step(self,action):
        if action == OPPOSITE[self.heading]:
            action = self.heading

        self.heading = action
        dx, dy = DIRS[action]

        hx, hy = self.snake[0]

        new = (hx+dx, hy+dy)

        self.steps +=1
        self.idle +=1

        eating = new == self.food
        body = self.snake if eating else self.snake[:-1]


        if self._blocked(new):
            self.done = True
            return

        self.snake.insert(0, new)

        if eating:
            self.score += 1
            self.idle = 0
            self._place_food
        else:
            self.snake.pop()

        if self.idle >= self.max_idle:
            self.done = True

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
