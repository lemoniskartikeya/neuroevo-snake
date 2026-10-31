import os
import random
import time

from snake_env import SnakeEnv


def draw(env):
    # Prints the current game state as text.

    grid = [["." for _ in range(env.size)] for _ in range(env.size)]
    # Build a size x size table. It is a list of rows, and each row is a
    # list of cells. Every cell starts as "." (empty square).

    if env.food:
        # food is None when the snake has filled the board, so check first.
        fx, fy = env.food
        grid[fy][fx] = "*"
        # IMPORTANT: grid is indexed [row][column], which is [y][x].
        # Writing grid[fx][fy] would put the food in the wrong place.

    for i, (x, y) in enumerate(env.snake):
        # enumerate gives each snake square together with its position i.
        # i == 0 is the head, because the snake list is head first.
        grid[y][x] = "H" if i == 0 else "o"
        # Head is drawn as H, body squares as o.

    os.system("cls" if os.name == "nt" else "clear")
    # Wipe the terminal so each frame replaces the last one.
    # "cls" is the Windows command, "clear" is for Mac and Linux.
    # os.name is "nt" on Windows.

    print("\n".join(" ".join(row) for row in grid))
    # " ".join(row): put a space between cells so the squares look square.
    # "\n".join(...): put each row on its own line.

    print("score:", env.score, " steps:", env.steps)
    # Show progress under the board.


def main():
    env = SnakeEnv(seed=1)
    # A fixed seed gives the same food positions every run,
    # which makes bugs easier to reproduce.

    while not env.done:
        # Keep playing until the game ends (crash or idle limit).

        draw(env)
        # Show the current board.

        env.step(random.randint(0, 3))
        # Pick a random action: 0 up, 1 down, 2 left, 3 right.
        # A random snake dies quickly. That is expected.
        # Later, replace this with: net.act(env.observe())

        time.sleep(0.15)
        # Pause 0.15 seconds so you can watch. Smaller is faster.

    draw(env)
    # Draw the final board so you can see how the snake died.

    print("game over")


if __name__ == "__main__":
    # Runs main() only when you run this file directly,
    # not when another file imports it.
    main()