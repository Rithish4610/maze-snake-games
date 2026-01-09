import random
import gradio as gr

ROWS, COLS = 10, 20

# ---------------------
# Maze
# ---------------------
def create_maze():
    maze = [['.' for _ in range(COLS)] for _ in range(ROWS)]
    for i in range(ROWS):
        maze[i][0] = maze[i][COLS-1] = '#'
    for j in range(COLS):
        maze[0][j] = maze[ROWS-1][j] = '#'
    return maze

maze = create_maze()

# ---------------------
# Game State
# ---------------------
snake = []
direction = "RIGHT"
game_over = False
score = 0
move_count = 0
food_animation_phase = 0
food = ()
moving_obstacles = []

NUM_OBSTACLES = 10

# ---------------------
# Functions
# ---------------------
def init_game():
    global snake, direction, game_over, score, move_count, food_animation_phase, food, moving_obstacles
    snake = [(5,5),(5,4),(5,3)]
    direction = "RIGHT"
    game_over = False
    score = 0
    move_count = 0
    food_animation_phase = 0
    food = place_food()
    moving_obstacles = []
    # Place static human obstacles randomly
    for _ in range(NUM_OBSTACLES):
        while True:
            r = random.randint(1, ROWS-2)
            c = random.randint(1, COLS-2)
            if (r,c) not in snake and (r,c) != food and (r,c) not in moving_obstacles:
                moving_obstacles.append((r,c))
                break

def place_food():
    while True:
        r = random.randint(1, ROWS-2)
        c = random.randint(1, COLS-2)
        if (r,c) not in snake:
            return (r,c)

def render():
    global food_animation_phase
    html = """
    <style>
    @keyframes blink {50% {opacity:0.3;}}
    </style>
    <div style='display:grid;grid-template-columns:repeat(20,25px);gap:2px;'>"""
    
    for r in range(ROWS):
        for c in range(COLS):
            color = "#222"
            glow = False
            content = ""  # for emoji

            # Walls
            if maze[r][c] == "#":
                color = "#555"

            # Snake
            if (r,c) in snake:
                glow = True
                if (r,c) == snake[0]:
                    content = "🐍"
                else:
                    content = "🐉"

            # Static human obstacles
            if (r,c) in moving_obstacles:
                glow = True
                content = "🧍" if food_animation_phase % 2 == 0 else "🏃"

            # Food → rat animation
            if (r,c) == food:
                glow = True
                content = "🐀" if food_animation_phase % 2 == 0 else "🐁"

            shadow = f"box-shadow:0 0 6px {color};" if glow else ""
            html += f"<div style='width:25px;height:25px;background:{color};border-radius:6px;{shadow};text-align:center;font-size:20px;'>{content}</div>"
    
    html += "</div>"
    html += f"<h4>Score: {score}</h4>"
    return html

def move(dir):
    global snake, direction, game_over, food, score, move_count, food_animation_phase
    if game_over:
        return "<h2 style='color:red; animation: blink 1s infinite;'>💀 GAME OVER</h2>" + render()

    direction = dir
    move_count += 1
    food_animation_phase += 1
    head_r, head_c = snake[0]

    moves = {"UP":(head_r-1,head_c),
             "DOWN":(head_r+1,head_c),
             "LEFT":(head_r,head_c-1),
             "RIGHT":(head_r,head_c+1)}
    new = moves[direction]

    # Check collisions with walls, snake, or static humans
    if maze[new[0]][new[1]]=="#" or new in snake or new in moving_obstacles:
        game_over = True
        return "<h2 style='color:red; animation: blink 1s infinite;'>💀 GAME OVER</h2>" + render()

    snake.insert(0,new)

    if new == food:
        score += 1
        food = place_food()
    else:
        snake.pop()

    # Food moves every 5 moves
    if move_count % 5 == 0:
        food = place_food()

    return render()

# ---------------------
# Gradio UI
# ---------------------
init_game()  # start game

with gr.Blocks() as app:
    gr.Markdown("## 🐍 Maze Snake Game (Snake + Static Humans + Rat Food + Reset)")

    board = gr.HTML(render())

    with gr.Row():
        up = gr.Button("⬆️")
    with gr.Row():
        left = gr.Button("⬅️")
        down = gr.Button("⬇️")
        right = gr.Button("➡️")
    reset_btn = gr.Button("🔄 Reset Game")

    up.click(lambda: move("UP"), outputs=board)
    down.click(lambda: move("DOWN"), outputs=board)
    left.click(lambda: move("LEFT"), outputs=board)
    right.click(lambda: move("RIGHT"), outputs=board)

    # Reset button action
    reset_btn.click(lambda: (init_game(), render())[1], outputs=board)

app.launch()
