# neuroevo-snake

Snake agents that learn to play through **neuroevolution**. Each snake is controlled by a small neural network built from scratch in NumPy. There is no backpropagation and no ML framework: a population of random networks plays the game, the best ones survive, and their offspring get slightly mutated weights. Over generations, the snakes get better.

The best snake can be watched live in the browser, streamed over a FastAPI WebSocket, and the whole project runs in a single Docker container.

<!-- TODO: add demo.gif here (generation 1 vs generation 80, side by side) -->
![demo](results/demo.gif)

## Why this project

Most neural network projects train with gradient descent. This one asks a different question: can a plain MLP learn a task using only selection pressure, with no gradients at all? Evolution is a good fit when there is no labeled data and the only feedback is a score at the end of a game.

## How it works

### The game
A headless 12 x 12 Snake (`src/snake_env.py`). Actions are up, down, left and right. A U-turn into the snake's own neck is ignored. If the snake goes 100 moves without eating, the game ends, which stops snakes from circling forever.

### The network
A plain feed-forward MLP (`src/mlp.py`), written in NumPy.

| Layer  | Size | Activation |
|--------|------|------------|
| Input  | 12   | none       |
| Hidden | 16   | tanh       |
| Hidden | 16   | tanh       |
| Output | 4    | argmax     |

All weights and biases are stored in one flat vector (the "genome"), which makes crossover and mutation simple array operations.

### The 12 inputs
| Inputs | Count | Meaning |
|--------|-------|---------|
| Danger | 4 | 1 if the square next to the head (up, down, left, right) is a wall or the snake's body |
| Heading | 4 | One-hot encoding of the current direction |
| Food direction | 4 | 1 if the food is above, below, left of, or right of the head |

### The evolution loop
`src/evolve.py` runs the following each generation:

1. **Evaluate.** Every network plays several games on the same random seeds, so scores compare skill and not luck.
2. **Rank** the population by fitness.
3. **Keep the elite.** The top 10% pass to the next generation unchanged.
4. **Select parents** with tournament selection (pick 3 at random, the best one wins).
5. **Crossover.** Each weight in the child comes from one of the two parents at random.
6. **Mutate.** A small fraction of weights get Gaussian noise added.

### Fitness
```
fitness = (food eaten * 100) + (steps survived * 0.1)
```
Eating dominates the score. The small survival bonus helps early generations that cannot eat yet.

<!-- TODO: update these defaults if you change them in evolve.py -->
**Default settings:** population 200, 60 generations, 3 games per evaluation, mutation rate 0.1, mutation scale 0.3.

## Results

<!-- TODO: fill in after your real runs. Do not leave made-up numbers here. -->

| Metric | Generation 1 | Final generation |
|--------|--------------|------------------|
| Best score (food eaten) | TODO | TODO |
| Average score | TODO | TODO |

![fitness curve](results/fitness.png)

## Project structure

```
neuroevo-snake/
├── README.md
├── requirements.txt
├── Dockerfile
├── src/
│   ├── snake_env.py      # game logic
│   ├── mlp.py            # NumPy neural network
│   ├── evolve.py         # evolution loop
│   └── replay.py         # watch the best snake in the terminal
├── app/
│   ├── main.py           # FastAPI app with WebSocket stream
│   └── static/           # live dashboard (HTML and JS)
├── models/
│   └── best.npy          # saved best weights
├── results/
│   ├── history.json      # fitness per generation
│   └── demo.gif
└── tests/
    └── test_snake_env.py
```

## Getting started

### Run locally

```bash
git clone https://github.com/lemoniskartikeya/neuroevo-snake.git
cd neuroevo-snake
pip install -r requirements.txt
```

Train a population (saves `models/best.npy` and `results/history.json`):
```bash
python src/evolve.py 60
```

Watch the best snake play in the terminal:
```bash
python src/replay.py
```

Start the web dashboard:
```bash
uvicorn app.main:app --reload
```
Then open http://localhost:8000.

### Run with Docker

```bash
docker build -t neuroevo-snake .
docker run -p 8000:8000 neuroevo-snake
```
Then open http://localhost:8000.

## API

<!-- TODO: update to match your final endpoints -->

| Endpoint | Type | Description |
|----------|------|-------------|
| `/health` | GET | Service status |
| `/ws/play` | WebSocket | Streams the best snake's game state, one message per move |

## Tests

```bash
pytest tests/
```
The tests cover wall collisions, growth on eating, ignoring U-turns, and seed repeatability (the same seed always produces the same food positions).

## Limitations

- Fitness is noisy, because each generation is scored on fresh random games. The best score can drop between generations even when the population is improving.
- The network sees only 12 local features, so it cannot plan around its own long body. Snakes tend to plateau once they get long.
- Evolution is sample-inefficient compared with gradient-based reinforcement learning. The goal here is to show that it works at all, not that it is the best method.

## Ideas for extension

- Add distance-to-wall and body-ahead inputs
- Try a larger network or a different fitness function
- Compare against a hand-coded Snake AI baseline
- Let users tune mutation rate and population size from the dashboard

## License

MIT
