import pygame
import random
import sys
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tesla Cart Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ROAD_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)

clock = pygame.time.Clock()
FPS = 60

cart_width, cart_height = 80, 50
lane_width = WIDTH // 5
cart_x = 2 * lane_width + (lane_width - cart_width) // 2
cart_y = HEIGHT - cart_height - 50
cart_speed = 5

obstacle_width, obstacle_height = 60, 120
obstacle_speed = 5
obstacles = []

line_height = 20
line_gap = 10
line_positions = [i for i in range(0, HEIGHT, line_height + line_gap)]

score = 0
high_score = 0
font = pygame.font.Font(None, 36)

high_score_file = "high_score.txt"
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as file:
        high_score = int(file.read())

try:
    tesla_cart_image = pygame.image.load("teslacybertruck.png")
    tesla_cart_image = pygame.transform.scale(tesla_cart_image, (cart_width, cart_height))
except pygame.error as e:
    print(f"Error loading image: {e}")
    sys.exit()

try:
    autopilot_sound = pygame.mixer.Sound("1.mp3")
except pygame.error as e:
    print(f"Error loading sound: {e}")
    autopilot_sound = None

try:
    obstacle_images = [
        pygame.image.load("ob1.png"),
        pygame.image.load("ob2.png"),
        pygame.image.load("ob3.png"),
        pygame.image.load("ob4.png"),
        pygame.image.load("ob5.png")
    ]
    obstacle_images = [pygame.transform.scale(img, (obstacle_width, obstacle_height)) for img in obstacle_images]
except pygame.error as e:
    print(f"Error loading obstacle images: {e}")
    sys.exit()

autodrive = False
player_name = ""

def spawn_obstacle():
    while True:
        lane = random.randint(0, 4)
        x = lane * lane_width + (lane_width - obstacle_width) // 2
        y = -obstacle_height

        obstacle_image = random.choice(obstacle_images)

        new_obstacle = pygame.Rect(x, y, obstacle_width, obstacle_height)
        overlap = False
        for obstacle, _ in obstacles:
            if new_obstacle.colliderect(obstacle):
                overlap = True
                break
        
        if not overlap:
            return new_obstacle, obstacle_image

def draw_lanes():
    screen.fill(ROAD_GRAY)
    for lane in range(5):
        pygame.draw.rect(screen, ROAD_GRAY, (lane * lane_width, 0, lane_width, HEIGHT))

    for i in range(1, 5):
        for position in line_positions:
            pygame.draw.line(screen, WHITE, (i * lane_width, position), (i * lane_width, position + line_height), 2)

def update_lines():
    for i in range(len(line_positions)):
        line_positions[i] += obstacle_speed
        if line_positions[i] > HEIGHT:
            line_positions[i] -= HEIGHT + line_height + line_gap

def autodrive_move():
    global cart_x
    current_lane = cart_x // lane_width
    safe_lanes = []
    for lane in range(5):
        if not any(obs.x // lane_width == lane and cart_y - 150 < obs.y < cart_y + 50 for obs, _ in obstacles):
            safe_lanes.append(lane)

    if current_lane not in safe_lanes:
        if safe_lanes:
            target_lane = min(safe_lanes, key=lambda lane: abs(lane - current_lane))
            cart_x = target_lane * lane_width + (lane_width - cart_width) // 2
            return target_lane
    return current_lane

def draw_autopilot_path(target_lane):
    path_x = target_lane * lane_width + lane_width // 2
    pygame.draw.line(screen, BLUE, (cart_x + cart_width // 2, cart_y), (path_x, cart_y - 100), 4)

def draw_tesla_cart(x, y):
    screen.blit(tesla_cart_image, (x, y))

def draw_start_screen():
    global player_name
    screen.fill(BLACK)
    title_font = pygame.font.Font(None, 72)
    subtitle_font = pygame.font.Font(None, 36)

    title_text = title_font.render("TESLA CART", True, YELLOW)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

    name_prompt = subtitle_font.render("Enter your name:", True, WHITE)
    screen.blit(name_prompt, (WIDTH // 2 - name_prompt.get_width() // 2, HEIGHT // 2 - 30))

    name_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 40)
    pygame.draw.rect(screen, WHITE, name_box, 2)

    name_text = subtitle_font.render(player_name, True, WHITE)
    screen.blit(name_text, (name_box.x + 5, name_box.y + 5))

    start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 40)
    pygame.draw.rect(screen, BLUE, start_button)
    start_button_text = subtitle_font.render("Start Game", True, WHITE)
    screen.blit(start_button_text, (start_button.x + (start_button.width - start_button_text.get_width()) // 2, start_button.y + (start_button.height - start_button_text.get_height()) // 2))

    pygame.display.flip()

    return name_box, start_button

running = True
game_started = False

while not game_started:
    name_box, start_button = draw_start_screen()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            elif event.key == pygame.K_RETURN and player_name != "":
                game_started = True
            elif event.key != pygame.K_RETURN:
                player_name += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if start_button.collidepoint(mouse_x, mouse_y) and player_name != "":
                game_started = True

while running:
    draw_lanes()
    update_lines()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                autodrive = not autodrive
                if autodrive and autopilot_sound:
                    autopilot_sound.play()
                elif not autodrive and autopilot_sound:
                    autopilot_sound.play()

    if not autodrive:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and cart_x > lane_width:
            cart_x -= cart_speed
        if keys[pygame.K_RIGHT] and cart_x < WIDTH - lane_width - cart_width:
            cart_x += cart_speed
    else:
        target_lane = autodrive_move()
        draw_autopilot_path(target_lane)

    if random.randint(1, 100) < 5:
        obstacle, obstacle_image = spawn_obstacle()
        obstacles.append((obstacle, obstacle_image))

    for obstacle, obstacle_image in obstacles:
        obstacle.y += obstacle_speed
        screen.blit(obstacle_image, obstacle)
        if obstacle.colliderect(pygame.Rect(cart_x, cart_y, cart_width, cart_height)):
            print("Game Over!")
            running = False
        if obstacle.y > HEIGHT:
            obstacles.remove((obstacle, obstacle_image))

    draw_tesla_cart(cart_x, cart_y)

    score += 1
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))

    pygame.display.flip()
    clock.tick(FPS)

game_over_text = font.render(f"{player_name} - Game Over! Final Score: {score}", True, WHITE)
screen.fill(BLACK)
screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
pygame.display.flip()

if score > high_score:
    with open(high_score_file, "w") as file:
        file.write(str(score))

pygame.time.wait(3000)
pygame.quit()
sys.exit()
