import pygame
import sys

pygame.init()
# Nastavíme menší okno pro testování
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Test ořezu zelené barvy")
clock = pygame.time.Clock()

def remove_background_glow(image: pygame.Surface, mode: str = "magenta") -> pygame.Surface:
    """
    Vyčistí vnější šum podle zvoleného režimu ('green' nebo 'magenta') 
    a připraví obrázek pro set_colorkey.
    """
    pixel_array = pygame.PixelArray(image)
    
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            raw_color = pixel_array[x, y]
            color_obj = image.unmap_rgb(raw_color)
            r, g, b = color_obj.r, color_obj.g, color_obj.b
            
            if mode == "magenta":
                # FIALOVÉ POZADÍ: Červená a modrá jsou silné, zelená je slabá
                # Vymaže čistou fialovou i její tmavší/světlejší odstíny v šumu
                if (r > g + 40 and b > g + 40) or (r > 200 and b > 200 and g < 100):
                    pixel_array[x, y] = (0, 0, 0)
                    
            elif mode == "green":
                # ZELENÉ POZADÍ (pro tvé myši a brouka)
                if (g > r + 30 and g > b + 30) or ((90 <= r <= 110) and (220 <= g <= 255) and (30 <= b <= 65)):
                    pixel_array[x, y] = (0, 0, 0)
                    
    del pixel_array
    return image

# --- NAČTENÍ A ÚPRAVA TESTOVACÍHO OBRÁZKU ---
# Zde si doplň cestu k jednomu z tvých nepřátel, např. "TBOI/cat_version/enemy/beetle.png"
IMAGE_PATH = "TBOI/cat_version/bosses/veterinarian/vet.png"

try:
    # .convert() je nutný, aby PixelArray správně fungoval s RGB formátem
    test_img = pygame.image.load(IMAGE_PATH).convert()
    test_img = pygame.transform.scale(test_img, (300, 300)) # Zvětšíme, ať to dobře vidíš
    
    # Aplikujeme tvůj filtr na zelené pixely
    test_img = remove_background_glow(test_img)
    
    # Nastavíme nově vzniklou černou barvu jako průhlednou
    test_img.set_colorkey((0, 0, 0))
    
except pygame.error as e:
    print(f"Nepodařilo se načíst obrázek '{IMAGE_PATH}'. Zkontroluj cestu! Chyba: {e}")
    pygame.quit()
    sys.exit()

# --- HLAVNÍ TESTOVACÍ LOOP ---
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Vybarvíme pozadí schválně tmavě červenou, 
    # aby šel případný zelený nebo černý obrys okamžitě vidět
    screen.fill((80, 20, 20))

    # Vykreslíme upravený obrázek doprostřed obrazovky
    screen.blit(test_img, (400 - test_img.get_width() // 2, 300 - test_img.get_height() // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()