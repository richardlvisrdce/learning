import pygame # ideally pygame -ce
import sys
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
BLUE = (100, 150, 255)


ROOM_BOUNDS = pygame.Rect(50, 50, 700, 500) # left, top, width, height

sprite_chosen = "TBOI/cat_version/cat_sprite"
cat_sprites = {}
for dir in ["front", "back", "left", "right"]:
    img = pygame.image.load(f"{sprite_chosen}/{dir}.png").convert_alpha()
    img = pygame.transform.scale(img, (int(img.get_width() * 0.2), int(img.get_height() * 0.2)))
    cat_sprites[dir] = img

class Player:
    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, cat_sprites["front"].get_width(), cat_sprites["front"].get_height())
        self.speed: int = 4
        self.health: int = 3
        self.shoot_cooldown: int = 0
        self.current_direction = "front"

    def move(self, keys) -> None:
        if keys[pygame.K_a]: 
            self.rect.x -= self.speed
            self.current_direction = "left"
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.current_direction = "right"
        if keys[pygame.K_w]: 
            self.rect.y -= self.speed
            self.current_direction = "back"
        if keys[pygame.K_s]: 
            self.rect.y += self.speed
            self.current_direction = "front"

        self.rect.clamp_ip(ROOM_BOUNDS)

    def update(self) -> None:
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, surface):
        active_sprite = cat_sprites[self.current_direction]
        surface.blit(active_sprite, self.rect.topleft)


# TODO
# to be changed - for now placeholder isaac tears - then maybe hairballs or ?
# tear_img = pygame.image.load(f"{sprite_chosen}_tears.png").convert()
ISAAC_TEARS = "TBOI/isaac_tears.png"
tear_img = pygame.image.load(ISAAC_TEARS).convert()
tear_size = 2
tear_img = pygame.transform.scale(tear_img,
                                (int(tear_img.get_width() * tear_size), 
                                int(tear_img.get_height() * tear_size)))
# here also black i think
tear_img.set_colorkey((0, 0, 0))

class Tear:
    def __init__(self, x: int, y: int, dx: int, dy: int):
        self.rect = pygame.Rect(x, y, tear_img.get_width(), tear_img.get_height())
        self.speed: int = 7
        self.dx = dx
        self.dy = dy
    
    def move(self) -> None:
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
    
    def draw(self, surface) -> None:
        surface.blit(tear_img, self.rect.topleft)


player = Player(400, 300)
tears = []

running: bool = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # Update stavu hráče
    player.move(keys)
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
            # Centrování výstřelu
            new_tear = Tear(player.rect.centerx - (tear_img.get_width() // 2), 
                            player.rect.centery - (tear_img.get_height() // 2), 
                            dx, dy)
            tears.append(new_tear)
            player.shoot_cooldown = 15

    # Pohyb a mazání slz
    for tear in tears[:]:
        tear.move()
        if not ROOM_BOUNDS.colliderect(tear.rect):
            tears.remove(tear)

    # Vykreslování
    screen.fill((30, 20, 20))
    pygame.draw.rect(screen, (60, 40, 40), ROOM_BOUNDS, 4) # Zdi místnosti
    
    player.draw(screen)
    for tear in tears:
        tear.draw(screen)
        
    pygame.display.flip()

pygame.quit()
sys.exit()