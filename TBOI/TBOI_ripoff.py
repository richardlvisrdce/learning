import pygame # ideally pygame -ce
import sys
import math

BLUE = (100, 150, 255)
pygame.init()
screen = pygame.display.set_mode((1600, 1200), pygame.RESIZABLE)
clock = pygame.time.Clock()

# ROOM_BOUNDS = pygame.Rect(50, 50, 700, 500) # left, top, width, height
ROOM_BOUNDS = pygame.Rect(100, 100, 1400, 1000) # left, top, width, height

sprite_chosen = "TBOI/isaac"

sprite_img = pygame.image.load(f"{sprite_chosen}.png").convert()
# potentially later used to update width and height of sprite image - 
# could also be used when some effects make you bigger (=> just make img bigger?)
sprite_size = 3 # i think this has to be int or sprite_img.scale() will have to put it to int else problems?
sprite_img = pygame.transform.scale(sprite_img,
                                    (int(sprite_img.get_width() * sprite_size), 
                                    int(sprite_img.get_height() * sprite_size)))

# this is used to set color to ignore when blitting, for different characters it should be diff colors
# but for isaac i think black (0, 0, 0) is ok: 
sprite_img.set_colorkey((0, 0, 0))

tear_img = pygame.image.load(f"{sprite_chosen}_tears.png").convert()
tear_size = 2
tear_img = pygame.transform.scale(tear_img,
                                (int(tear_img.get_width() * tear_size), 
                                int(tear_img.get_height() * tear_size)))
# here also black i think
tear_img.set_colorkey((0, 0, 0))
    

# to be replaced by actual sprite
class Player:
    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, sprite_img.get_width(), sprite_img.get_height())
        self.speed: int = 8
        self.health: int = 3
        self.shoot_cooldown: int = 0

    def move(self, keys) -> None:
        # upper left corner has coords [0, 0] so Y-axis changes mirror to that in cartesian
        if keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_d]: self.rect.x += self.speed
        if keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_s]: self.rect.y += self.speed

        # keep player inside room walls (simple boundaries)
        self.rect.clamp_ip(ROOM_BOUNDS)

    def update(self) -> None:
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, surface):
        surface.blit(sprite_img, self.rect.topleft)


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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # Update stavu hráče
    player.move(keys)
    player.update()
    
    # Střelba na šipky
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
    clock.tick(60)

pygame.quit()
sys.exit()