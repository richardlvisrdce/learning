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
    def move(self, keys, current_room: Room) -> None:
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
    def __init__(self):
        pass


class Boss:
    # need to move+shoot on their own so defo some AI. dmg - 1 heart
    # need special attacks for each one, some will only have 1 attack, bosses will have like 3
    def __init__(self):
        pass


def load_room_by_type(room_type: str) -> list[list[int]]:
    # BRUTALLY VIBECODED #TODO check if ok
    # 1. Base clean room layout with doors on all 4 sides
    new_map = []
    for r in range(15):
        row = []
        for c in range(20):
            if r == 0 or r == 14 or c == 0 or c == 19:
                # Open doors in the middle of walls
                if (r == 0 and c in [9, 10]) or (r == 14 and c in [9, 10]) or (r == 7 and c in [0, 19]):
                    row.append(0)
                else:
                    row.append(1) # Solid wall
            else:
                row.append(0) # Empty floor
        new_map.append(row)

    # 2. Add specific obstacles based on what kind of room this is
    if room_type == "start":
        # Start room stays completely empty and safe
        pass
        
    elif room_type == "treasure":
        # Treasure room: Rocks forming a protective square in the center for the item
        new_map[6][9], new_map[6][10] = 2, 2
        new_map[8][9], new_map[8][10] = 2, 2
        new_map[7][8], new_map[7][11] = 2, 2
        
    elif room_type == "boss":
        # Boss room: Empty center for the fight, spikes in corners
        new_map[2][2], new_map[2][17] = 3, 3
        new_map[12][2], new_map[12][17] = 3, 3
        
    elif room_type == "normal":
        # Regular enemy room: Random distribution of rocks (5%) and spikes (2%)
        for r in range(1, 14):
            for c in range(1, 19):
                # Don't spawn directly in front of doors or in the dead center
                if r in [1, 2, 7, 12, 13] and c in [1, 2, 9, 10, 17, 18]:
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

floor = Floor_Manager(num_rooms=12) # Generates 12 rooms on a 10x10 matrix

# Load the initial layout for the 'start' room from our new function
initial_layout = load_room_by_type("start")
current_room = Room(initial_layout)

current_room = Room(ROOM_MAP)
running: bool = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # Update stavu hráče
    player.move(keys, current_room)
    player.update()
    
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

    virtual_screen.fill((30, 20, 20)) # Dark floor
    
    # Draw the room tiles first!
    current_room.draw(virtual_screen)
    
    # Then draw player and tears
    player.draw(virtual_screen)
    for tear in tears:
        tear.draw(virtual_screen)

    # scale the virtual (logic) screen to the actual screen size and blit it    
    scaled_surface = pygame.transform.scale(virtual_screen, screen.get_size())
    screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()