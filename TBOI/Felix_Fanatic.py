import pygame # ideally pygame -ce
import sys
import math
import random

pygame.init()
screen = pygame.display.set_mode((1600, 1200), pygame.RESIZABLE)
virtual_screen = pygame.Surface((1600, 1200)) # this is where everything will be drawn, then scaled to the actual screen size
clock = pygame.time.Clock()
BLUE = (100, 150, 255)

ROOM_BOUNDS = pygame.Rect(100, 100, 1400, 1000) # left, top, width, height
TILE_SIZE = 80

# test room. then should generate pseudo-randomly 15 rows, 20 columns
# 0 for empty tile, 1 for bounds - room will have outer layer full of these, except places where door is - that will have an empty tile, 2 for obstacle, 3 for sharp obstacle
ROOM_MAP: list[list[int]] = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 1],
    [1, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 1],
    [1, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# 15 rows, 20 columns - Doors are the 0s in the middle of walls
START_ROOM_MAP: list[list[int]] = [
    [1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1], # North Door (cols 9, 10)
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,2,2,0,0,0,0,0,0,0,0,0,2,2,0,0,0,1],
    [1,0,0,2,2,0,0,0,0,0,0,0,0,0,2,2,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], # West & East Doors (row 7)
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,2,2,0,0,0,0,0,0,0,0,0,2,2,0,0,0,1],
    [1,0,0,2,2,0,0,0,0,0,0,0,0,0,2,2,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1]  # South Door (cols 9, 10)
]

# TILES_MEANING = {"empty": 0, "bounds": 1, "obstacle": 2, "sharp_obstacle": 3}
class Room:
    # room has to be formally made out of tiles - eg. 20x15 (width x height) for normal rooms and 20x20 for boss ? What about special rooms?
    # will have obstacles in it somewhere, possible entry costs,
    def __init__(self, room_data: list[list[int]]):
        self.room_data = room_data
        self.walls: list[pygame.Rect] = []
        self.obstacles: list[pygame.Rect] = []
        self.sharp_obstacles: list[pygame.Rect] = []
        # 
        for row_index, row in enumerate(self.room_data):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                
                if tile != 0: # If it's not empty floor
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    if tile == 1:
                        self.walls.append(rect)
                    elif tile == 2:
                        self.obstacles.append(rect)
                    elif tile == 3:
                        self.sharp_obstacles.append(rect)
    def draw(self, surface):
        # placeholder colors before # TODO textures
        for wall in self.walls:
            pygame.draw.rect(surface, (50, 40, 40), wall)
        for obs in self.obstacles:
            pygame.draw.rect(surface, (100, 100, 100), obs) # Gray rocks
        for sharp in self.sharp_obstacles:
            pygame.draw.rect(surface, (200, 50, 50), sharp) # Red spikes



class Floor_Manager:
    ### BRUTALLY VIBECODED :(
    # TODO - manages the floors, rooms, room transitions, etc. 
    # will have to generate random rooms and #TODO keep track of which ones have been visited
    def __init__(self, num_rooms: int = 10):
        self.num_rooms = num_rooms
        # 10x10 grid of rooms. None means empty space, string means room type
        self.grid: list[list[str | None]] = [[None for _ in range(10)] for _ in range(10)]
        self.room_instances: list[list[Room | None]] = [[None for _ in range(10)] for _ in range(10)]
        # Start in the exact middle of the floor grid
        self.start_x = 5
        self.start_y = 5
        self.current_x = self.start_x
        self.current_y = self.start_y
        
        self.generate_floor()

    def generate_floor(self):
        # 1. Place the starting room
        self.grid[self.current_y][self.current_x] = "start"
        
        placed_rooms = 1
        active_positions = [(self.current_x, self.current_y)]
        
        # 2. Drunkard's Walk / Branching algorithm to generate normal rooms
        while placed_rooms < self.num_rooms:
            # Pick a random already placed room to branch out from
            cx, cy = random.choice(active_positions)
            
            # Pick a random direction to expand
            dx, dy = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
            nx, ny = cx + dx, cy + dy
            
            # Check grid bounds and if the slot is empty
            if 0 <= nx < 10 and 0 <= ny < 10 and self.grid[ny][nx] is None:
                self.grid[ny][nx] = "normal"
                active_positions.append((nx, ny))
                placed_rooms += 1
                
        # 3. Find dead ends (rooms with only 1 neighbor) to place Special Rooms
        dead_ends = []
        for y in range(10):
            for x in range(10):
                if self.grid[y][x] == "normal":
                    neighbors = 0
                    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 10 and 0 <= ny < 10 and self.grid[ny][nx] is not None:
                            neighbors += 1
                    if neighbors == 1:
                        dead_ends.append((x, y))

        # 4. Force place Boss and Treasure rooms into dead ends
        if len(dead_ends) >= 2:
            bx, by = dead_ends.pop(0)
            self.grid[by][bx] = "boss"
            
            tx, ty = dead_ends.pop(0)
            self.grid[ty][tx] = "treasure"
        else:
            # Backup plan if geometry layout didn't create enough dead ends
            pass
            
        # Just a quick debug print to console to see the generated matrix on load!
        print("--- NEW FLOOR GENERATED ---")
        for row in self.grid:
            print([r[:2] if r else " ." for r in row])



sprite_chosen = "TBOI/cat_version/cat_sprite"
cat_sprites = {}
for dir in ["front", "back", "left", "right"]:
    img = pygame.image.load(f"{sprite_chosen}/{dir}.png").convert_alpha()
    img = pygame.transform.scale(img, (int(img.get_width() * 0.2), int(img.get_height() * 0.2)))
    cat_sprites[dir] = img

class Player:
    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, cat_sprites["front"].get_width(), cat_sprites["front"].get_height())
        self.speed: int = 10
        self.health: int = 3
        self.shoot_cooldown: int = 1
        self.current_direction = "front"

    # def move(self, keys) -> None:
    #     if keys[pygame.K_a]: 
    #         self.rect.x -= self.speed
    #         self.current_direction = "left"
    #     if keys[pygame.K_d]:
    #         self.rect.x += self.speed
    #         self.current_direction = "right"
    #     if keys[pygame.K_w]: 
    #         self.rect.y -= self.speed
    #         self.current_direction = "back"
    #     if keys[pygame.K_s]: 
    #         self.rect.y += self.speed
    #         self.current_direction = "front"

    #     self.rect.clamp_ip(ROOM_BOUNDS)
    def move(self, keys, current_room: Room, active_enemies: list) -> None:
        dx, dy = 0, 0
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        self.rect.x += dx
        
        for wall in current_room.walls + current_room.obstacles:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right
        
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        self.rect.y += dy
        for wall in current_room.walls + current_room.obstacles:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom
        self.rect.clamp_ip(pygame.Rect(0, 0, 1600, 1200))
        
        if len(active_enemies) > 0:
            # Kočka nemůže na okraj obrazovky, dokud jsou myši naživu
            # Zmenšíme jí hřiště o TILE_SIZE (80 pixelů) z každé strany
            self.rect.clamp_ip(pygame.Rect(TILE_SIZE, TILE_SIZE, 1600 - 2*TILE_SIZE, 1200 - 2*TILE_SIZE))
            return None # Nemůže odejít

        if self.rect.top <= 0: return "north"
        if self.rect.bottom >= 1200: return "south"
        if self.rect.left <= 0: return "west"
        if self.rect.right >= 1600: return "east"
            
        return None

    def update(self) -> None:
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, surface):
        active_sprite = cat_sprites[self.current_direction]
        surface.blit(active_sprite, self.rect.topleft)


# to be changed later
CAT_TEARS = "TBOI/cat_version/cat_sprite/cat_tears_v1.png"
tear_img = pygame.image.load(CAT_TEARS).convert()
tear_size = 0.05
tear_img = pygame.transform.scale(tear_img,
                                (int(tear_img.get_width() * tear_size), 
                                int(tear_img.get_height() * tear_size)))
# here also black i think
tear_img.set_colorkey((0, 0, 0))

class Tear:
    def __init__(self, x: int, y: int, dx: int, dy: int):
        self.rect = pygame.Rect(x, y, tear_img.get_width(), tear_img.get_height())
        self.speed: int = 13
        self.dx = dx
        self.dy = dy
    
    def move(self) -> None:
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
    
    def draw(self, surface) -> None:
        surface.blit(tear_img, self.rect.topleft)


player = Player(400, 300)
tears = []




enemy_types = ["fly", "beetle", "mechanical_mouse", "mouse"]
enemy_sprites = {}

for e_type in enemy_types:
    # Load each enemy and upscale it slightly (e.g., to 64x64 or according to scale)
    img = pygame.image.load(f"TBOI/cat_version/enemy/{e_type}.png").convert()
    img = pygame.transform.scale(img, (80, 80)) # Scale them to fit exactly 1 tile size
    bg_color = img.get_at((0, 0)) # TODO doenstwork
    img.set_colorkey(bg_color) # This removes the bright green screen completely!
    enemy_sprites[e_type] = img


OBSTACLES = ["rock", "spike", "mousetrap"] # some of these can be destroyed, some can have effects on contact, some can be moved by player, some move on their own


    # TODO, TBD this could be like separate levels completely or like separate paths in the same level ?
# normal - just a room with obstacles, maybe some pickups, enemies
# party - music, bar to spend money at for powerups, maybe a slot machine. Should be super dope and have some interactible npcs and some party-goers
# boss
# shop - buy stuff
# lsd - this happens for all rooms after you pick up the cat_lsd powerup, changes visuals and music, maybe some weird effects like screen shaking or something + melting walls and floors.
# treasure - some loot some item
# arcade - some mini games, maybe a shooting gallery or something, can win pickups or items or something + fun music + insanely catchy and colorful slots which have their own full screen (2 types for player max, 3 slots always filled by non-interactible animals - eg. dolphin, cat)
ROOMS = ["normal", "party", "boss", "shop", "lsd", "treasure", "arcade"]


class Obstacle:
    # just an obstacle. Can be destroyed with bombs or some can be moved, all are 1x1
    def __init__(self):
        pass

class ObstacleSharp:
    # can have dmg/some effect upon contact, cant be destroyed
        # TODO mousetrap - tweaks movement, spikes - do dmg, 
    def __init__(self):
        pass


class PowerUp:
    # things that change what you see and do. press K_e to interact (eat/drink them - dont know about animating that but we'll see)
        # uno reverse reverses movement controls for like 3 rooms / 2 minutes - prolly easier
        # redbul makes you shoot and move faster, changes music to be a little faster. Works for x minutes. Music could be GO2-Spitfire
        # kfc makes you bigger and tiny bit slower mbe
        # cat_lsd changes whole environment - easiest would be overlay bg (ideally moving/spinning) + other
        # skittles make you shoot rainbow colors #TODO they have white bg so have to convert twice
        # beer makes you a bit drowsy - controls are a bit delayed
        # cigarette is just aesthetic and makes you cough every now and then, with a bit of screen shake

    # TODO what about combinations? Need caps on stats.

    def __init__(self):
        pass



# bombs and shi, idk about textures. need explosion ranged like 2 tiles
class Pickups:
    def __init__(self):
        pass


class Item:
    # perma change something. Crazy stuff also. Can change tears, HP or stats
    def __init__(self):
        pass


class Enemy:
    # sprite img, tear img, size, light RNG AI for attacks?
    # collision dmg, tear dmg will be normalised to half/full heart
    # need special attacks for each one, some will only have 1 attack, bosses will have like 3
    # need to move on their own so defo some AI
    def __init__(self, x: int, y: int, enemy_type: str):
        self.type = enemy_type
        # 60x60 hitbox inside an 80x80 tile makes it feel tight and fair
        self.rect = pygame.Rect(x, y, 60, 60)
        self.speed: float = 0.0
        # Stats based on type
        if self.type == "fly":
            self.speed: float = 3.5  # Fast but fragile
            self.health: int = 1
        elif self.type == "mouse":
            self.speed: float = 2.0  # Normal speed, normal health
            self.health: int = 2
        elif self.type == "mechanical_mouse":
            self.speed: float = 4.5  # Super fast clockwork toy!
            self.health: int = 1
        elif self.type == "beetle":
            self.speed: float = 1.2  # Slow tank armored bug
            self.health: int = 4

    def move_towards_player(self, player_rect, current_room: Room):
        # Calculate distance
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance == 0: return

        # Normalize vector
        dx /= distance
        dy /= distance

        # Move X with room collision check
        self.rect.x += int(dx * self.speed)
        for wall in current_room.walls + current_room.obstacles:
            if self.rect.colliderect(wall):
                if dx > 0:  self.rect.right = wall.left
                elif dx < 0: self.rect.left = wall.right

        # Move Y with room collision check
        self.rect.y += int(dy * self.speed)
        for wall in current_room.walls + current_room.obstacles:
            if self.rect.colliderect(wall):
                if dy > 0:   self.rect.bottom = wall.top
                elif dy < 0: self.rect.top = wall.bottom

    def draw(self, surface):
        # Draw the correct sprite centered on the hitbox
        sprite = enemy_sprites[self.type]
        # Offset to draw 80x80 sprite nicely over 60x60 rect
        render_pos = (self.rect.x - 10, self.rect.y - 10)
        surface.blit(sprite, render_pos)


class Boss:
    # need to move+shoot on their own so defo some AI. dmg - 1 heart
    # need special attacks for each one, some will only have 1 attack, bosses will have like 3
    def __init__(self):
        pass



def load_room_by_type(room_type: str, floor: Floor_Manager, x: int, y: int) -> list[list[int]]:
    # JUST VIBES. better check it later
    # 0. Zjistíme, jestli máme sousedy v mřížce (a nejdeme mimo 10x10)
    has_north = y > 0 and floor.grid[y-1][x] is not None
    has_south = y < 9 and floor.grid[y+1][x] is not None
    has_west = x > 0 and floor.grid[y][x-1] is not None
    has_east = x < 9 and floor.grid[y][x+1] is not None

    # 1. Base clean room layout
    new_map = []
    for r in range(15):
        row = []
        for c in range(20):
            if r == 0 or r == 14 or c == 0 or c == 19:
                is_door = False
                # Dveře se vytvoří, pouze pokud je tím směrem místnost
                if r == 0 and c in [8, 9, 10, 11] and has_north: is_door = True
                if r == 14 and c in [8, 9, 10, 11] and has_south: is_door = True
                if r in [6, 7, 8] and c == 0 and has_west: is_door = True
                if r in [6, 7, 8] and c == 19 and has_east: is_door = True

                if is_door:
                    row.append(0) # Open path
                else:
                    row.append(1) # Solid wall
            else:
                row.append(0) # Empty floor
        new_map.append(row)

    # 2. Zbytek funkce (překážky podle typu místnosti) zůstává ÚPLNĚ STEJNÝ
    if room_type == "start":
        pass
    elif room_type == "treasure":
        new_map[6][9], new_map[6][10] = 2, 2
        new_map[8][9], new_map[8][10] = 2, 2
        new_map[7][8], new_map[7][11] = 2, 2
    elif room_type == "boss":
        new_map[2][2], new_map[2][17] = 3, 3
        new_map[12][2], new_map[12][17] = 3, 3
    elif room_type == "normal":
        for r in range(1, 14):
            for c in range(1, 19):
                if r in [1, 2, 6, 7, 8, 12, 13] and c in [1, 2, 8, 9, 10, 11, 17, 18]:
                    continue
                rand = random.random()
                if rand < 0.05:     new_map[r][c] = 2
                elif rand < 0.07:   new_map[r][c] = 3
                
    return new_map


#### TODO - couldnt rip menu music from medved misa ve vesmiru so which?

# TODO - how do i put gif + menu text?
NYAN_GIF = "TBOI/cat_version/nyan/nyan-cat-original.png"
MENU_MUSIC = ""
TITLE_IMG = ""
def draw_main_menu(screen, nyan_gif: str, menu_music: str, NAME_FONT) -> None:
    # TODO - nyan cat gif as background, Name of game, press any key to start, menu music
    pass
# draw_main_menu(screen, NYAN_GIF, MENU_MUSIC)

enemies: list[Enemy] = []
floor = Floor_Manager(num_rooms=12) # Generates 12 rooms on a 10x10 matrix

# Load the initial layout for the 'start' room from our new function
initial_layout = load_room_by_type("start", floor, floor.start_x, floor.start_y)
current_room = Room(initial_layout)
floor.room_instances[floor.start_y][floor.start_x] = current_room # Cache the start room!
running: bool = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # Update stavu hráče
    door_triggered = player.move(keys, current_room, enemies)
    player.update()
    if door_triggered is not None:
        tears.clear() # Clear active hairballs
        
        # 1. Update positions in the FloorManager grid matrix
        if door_triggered == "north":
            floor.current_y -= 1
            player.rect.centery = 1200 - TILE_SIZE - 40 # Teleport south
        elif door_triggered == "south":
            floor.current_y += 1
            player.rect.centery = TILE_SIZE + 40        # Teleport north
        elif door_triggered == "west":
            floor.current_x -= 1
            player.rect.centerx = 1600 - TILE_SIZE - 40 # Teleport east
        elif door_triggered == "east":
            floor.current_x += 1
            player.rect.centerx = TILE_SIZE + 40        # Teleport west

        # 2. Get the room type from the floor grid map
        room_type = floor.grid[floor.current_y][floor.current_x]
        if room_type is None:
            room_type = "normal"
            floor.grid[floor.current_y][floor.current_x] = "normal"

        if floor.room_instances[floor.current_y][floor.current_x] is not None:
            # Pull the existing room layout from memory!
            current_room = floor.room_instances[floor.current_y][floor.current_x]
            print(f"Returned to an already VISITED [{room_type}] room at [{floor.current_x}, {floor.current_y}]")
        else:
            # Generate a brand new layout, then cache it in room_instances
            new_layout = load_room_by_type(room_type, floor, floor.current_x, floor.current_y)
            current_room = Room(new_layout)
            floor.room_instances[floor.current_y][floor.current_x] = current_room
            print(f"Generated a NEW [{room_type}] room at [{floor.current_x}, {floor.current_y}]")
            # Clear hairballs and enemies from previous room
            tears.clear()
            enemies.clear()

            # TODO is this in correct place?
            # Spawn enemies only if it's a 'normal' room and we haven't cleared it yet
            # (For now we spawn them every time you enter a fresh normal room)
            if room_type == "normal":
                for _ in range(random.randint(2, 5)): # 2 to 5 random enemies
                    rx = random.randint(200, 1400)
                    ry = random.randint(200, 1000)
                    
                    # Pick a random type from your generated green screen image
                    random_type = random.choice(enemy_types)
                    enemies.append(Enemy(rx, ry, random_type))
    
    # Střelba na šipky
        # výstřel zároveň otočí sprita do smeru ve kterém střílí, 
        # nesmi to ale clashovat s pohybem -> proto nejdriv strelba a pak pokud neni strelba tak smer dle pohybu
    if keys[pygame.K_LEFT]:
        dx = -1
        player.current_direction = "left"
    elif keys[pygame.K_RIGHT]:
        dx = 1
        player.current_direction = "right"
    elif keys[pygame.K_UP]:
        dy = -1
        player.current_direction = "back"
    elif keys[pygame.K_DOWN]:
        dy = 1
        player.current_direction = "front"
    else:
    # Pokud hráč NESTŘÍLÍ, otočíme ho podle toho, kam se hýbe (WASD)
        if keys[pygame.K_a]:   player.current_direction = "left"
        elif keys[pygame.K_d]: player.current_direction = "right"
        elif keys[pygame.K_w]: player.current_direction = "back"
        elif keys[pygame.K_s]: player.current_direction = "front"
    if player.shoot_cooldown == 0:
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:  dx = -1
        if keys[pygame.K_RIGHT]: dx = 1
        if keys[pygame.K_UP]:    dy = -1
        if keys[pygame.K_DOWN]:  dy = 1
        if dx != 0 or dy != 0:
            # Centrování výstřelu - TBD
            new_tear = Tear(player.rect.centerx - (tear_img.get_width() // 2), 
                            player.rect.centery - (tear_img.get_height() // 2), 
                            dx, dy)
            tears.append(new_tear)
            player.shoot_cooldown = 15


    # # Pass the room to the player movement
    # player.move(keys, current_room)
    # player.update()
    
    # Pohyb a mazání slz
    for tear in tears[:]:
        tear.move()
        hit_obstacle = False
        for wall in current_room.walls + current_room.obstacles:
            if tear.rect.colliderect(wall):
                hit_obstacle = True
                break
                
        # Smazání slzy, pokud narazila do zdi, NEBO pro jistotu vylétla z obrazovky #TODO tohle je hodne hardcoded - sus
        if hit_obstacle or tear.rect.left < 0 or tear.rect.right > 1600 or tear.rect.top < 0 or tear.rect.bottom > 1200:
            tears.remove(tear)
    # Update enemies and hairball collisions
    for enemy in enemies[:]:
        enemy.move_towards_player(player.rect, current_room)

        # Hairball collision check
        for tear in tears[:]:
            if tear.rect.colliderect(enemy.rect):
                enemy.health -= 1
                if tear in tears: tears.remove(tear) # Destroy hairball
                
                if enemy.health <= 0:
                    if enemy in enemies: enemies.remove(enemy) # RIP enemy
                    break

    virtual_screen.fill((30, 20, 20)) # Dark floor
    
    # Draw the room tiles first!
    current_room.draw(virtual_screen)
    
    # Then draw player and tears
    player.draw(virtual_screen)
    for tear in tears:
        tear.draw(virtual_screen)
    for enemy in enemies:
        enemy.draw(virtual_screen)

    # scale the virtual (logic) screen to the actual screen size and blit it    
    scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
    screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()