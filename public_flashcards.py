import pygame
import random
import sys
import os
import json

# === KONFIGURACE ===
DATA_FILE = "data_ukazka/kyberpojmy.json"
LOCAL_DIR = "local_data"
PROGRESS_FILE = os.path.join(LOCAL_DIR, "progress.json")
STARRED_FILE = os.path.join(LOCAL_DIR, "starred.json")

# Klávesy pro odpovědi 1, 2, 3, 4
KEY_BINDINGS = {
    "answers": [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4],
    "confirm": pygame.K_SPACE
}

# Inicializace lokální složky pro uložení osobního postupu
os.makedirs(LOCAL_DIR, exist_ok=True)

def load_flashcards(filename):
    """Načte data z JSON souboru."""
    if not os.path.exists(filename):
        print(f"Soubor {filename} nebyl nalezen!")
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Chyba při načítání JSON: {e}")
        return []

def get_available_chapters(cards_data):
    """Zjistí, jaké kapitoly se v datech reálně nacházejí."""
    chapters = set()
    for card in cards_data:
        chapters.add(card.get("kapitola", 1))
    return sorted(list(chapters))

def load_starred_terms():
    if os.path.exists(STARRED_FILE):
        with open(STARRED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def toggle_starred_card(term):
    starred = load_starred_terms()
    if term in starred:
        starred.remove(term)
    else:
        starred.add(term)
    with open(STARRED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(starred), f)

def is_starred(term):
    return term in load_starred_terms()

def draw_text(surface, text, pos, font, color=(255, 255, 255), center=False, max_width=1700):
    """Vykreslí text s robustním zalamováním podle šířky."""
    if not text: return
    words = text.split(" ")
    lines, current_line = [], ""

    for word in words:
        test_line = (current_line + " " + word).strip()
        width, _ = font.size(test_line)
        if width <= max_width:
            current_line = test_line
        else:
            if current_line: lines.append(current_line)
            current_line = word
    if current_line: lines.append(current_line)

    total_height = len(lines) * font.get_linesize()
    base_y = pos[1] - total_height // 2 if center else pos[1]

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect()
        if center: text_rect.centerx = pos[0]
        else: text_rect.x = pos[0]
        text_rect.y = base_y + i * font.get_linesize()
        surface.blit(text_surface, text_rect)

def select_chapters_pygame(screen, font, small_font, bg_color, info_color, def_color, available_chapters):
    selected = {ch: False for ch in available_chapters}
    selecting = True
    clock = pygame.time.Clock()
    
    while selecting:
        screen.fill(bg_color)
        draw_text(screen, "🧠 Flashcards – Výběr kapitol", (960, 60), font, (255, 255, 0), center=True)
        draw_text(screen, "S - ★ Oblíbené kartičky (starred)", (960, 110), small_font, (255, 255, 0), center=True)
        draw_text(screen, "Klávesy 1-9 přepínají kapitoly, Enter potvrzuje výběr", (960, 150), small_font, info_color, center=True)
        
        for i, ch in enumerate(available_chapters):
            y_pos = 250 + i * 40
            status = "✅" if selected[ch] else "❌"
            color = def_color if selected[ch] else info_color
            draw_text(screen, f"{ch}. {status}  Kapitola {ch}", (960, y_pos), font, color, center=True)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                keys_map = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4, pygame.K_5: 5,
                            pygame.K_6: 6, pygame.K_7: 7, pygame.K_8: 8, pygame.K_9: 9}
                if event.key in keys_map:
                    ch_num = keys_map[event.key]
                    if ch_num in selected:
                        selected[ch_num] = not selected[ch_num]
                elif event.key == pygame.K_s:
                    return ["starred"]
                elif event.key == pygame.K_RETURN:
                    chosen = [ch for ch, s in selected.items() if s]
                    return chosen if chosen else available_chapters[:1]
                elif event.key == pygame.K_ESCAPE:
                    return []
        clock.tick(30)

def generate_learning_question(cards):
    correct_index = random.randint(0, len(cards) - 1)
    correct_term = cards[correct_index]["term"]
    correct_def = cards[correct_index]["definition"]
    
    indices = list(range(len(cards)))
    indices.remove(correct_index)
    random.shuffle(indices)
    
    wrong_answers = [cards[i]["definition"] for i in indices[:3]]
    options = wrong_answers
    insert_pos = random.randint(0, 3) if len(options) == 3 else 0
    options.insert(insert_pos, correct_def)
    
    return correct_term, options, insert_pos

def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1000), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    BG = (30, 30, 40)
    TERM_COLOR = (230, 230, 255)
    DEF_COLOR = (180, 255, 180)
    INFO_COLOR = (150, 150, 150)
    RESULT_COLOR = (255, 255, 0)
    WRONG_COLOR = (255, 100, 100)

    title_font = pygame.font.SysFont("arial", 40, bold=True)
    text_font = pygame.font.SysFont("arial", 28)
    small_font = pygame.font.SysFont("arial", 22)

    # Načtení dat a kapitol
    all_cards_data = load_flashcards(DATA_FILE)
    available_chapters = get_available_chapters(all_cards_data)
    
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as pf:
            progress = json.load(pf)
    else:
        progress = {"correct": 0, "total": 0, "known": {}, "wrong": []}

    mode = "menu"
    active_cards = []
    flash_index = 0
    flash_show_definition = False
    
    learning_question = None
    learning_options = []
    learning_correct_pos = 0
    learning_answered = False
    learning_selected = None

    running = True
    while running:
        screen.fill(BG)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if mode == "menu":
                    if event.key == pygame.K_1:
                        chosen_ch = select_chapters_pygame(screen, text_font, small_font, BG, INFO_COLOR, DEF_COLOR, available_chapters)
                        if chosen_ch == ["starred"]:
                            starred = load_starred_terms()
                            active_cards = [c for c in all_cards_data if c["term"] in starred]
                        else:
                            active_cards = [c for c in all_cards_data if c.get("kapitola") in chosen_ch]
                        
                        if active_cards:
                            mode = "flashcards"
                            flash_index = 0
                            flash_show_definition = False
                            random.shuffle(active_cards)
                    elif event.key == pygame.K_2:
                        if active_cards:
                            mode = "learning"
                            learning_question, learning_options, learning_correct_pos = generate_learning_question(active_cards)
                            learning_answered = False
                            learning_selected = None
                    elif event.key == pygame.K_ESCAPE:
                        running = False

                elif mode == "flashcards":
                    if event.key == pygame.K_SPACE:
                        flash_show_definition = not flash_show_definition
                    elif event.key in [pygame.K_RIGHT, pygame.K_DOWN]:
                        flash_index = (flash_index + 1) % len(active_cards)
                        flash_show_definition = False
                    elif event.key in [pygame.K_LEFT, pygame.K_UP]:
                        flash_index = (flash_index - 1) % len(active_cards)
                        flash_show_definition = False
                    elif event.key == pygame.K_s:
                        toggle_starred_card(active_cards[flash_index]["term"])
                    elif event.key == pygame.K_ESCAPE:
                        mode = "menu"

                elif mode == "learning":
                    if event.key == pygame.K_s:
                        toggle_starred_card(learning_question)
                    elif not learning_answered:
                        if event.key in KEY_BINDINGS["answers"]:
                            key_map = {KEY_BINDINGS["answers"][i]: i for i in range(4)}
                            selected = key_map[event.key]
                            if selected < len(learning_options):
                                learning_selected = selected
                                learning_answered = True
                                is_correct = (selected == learning_correct_pos)
                                progress["total"] += 1
                                if is_correct: progress["correct"] += 1
                                
                                with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                                    json.dump(progress, pf)
                        elif event.key == pygame.K_ESCAPE:
                            mode = "menu"
                    else:
                        if event.key == KEY_BINDINGS["confirm"]:
                            learning_question, learning_options, learning_correct_pos = generate_learning_question(active_cards)
                            learning_answered = False
                            learning_selected = None
                        elif event.key == pygame.K_ESCAPE:
                            mode = "menu"

        # --- Vykreslování ---
        if mode == "menu":
            draw_text(screen, "🧠 Flashcards", (960, 100), title_font, RESULT_COLOR, center=True)
            draw_text(screen, "1 - Vybrat kapitoly a spustit Flashcards", (960, 200), text_font, INFO_COLOR, center=True)
            draw_text(screen, "2 - Spustit Learning mode (z vybraných kapitol)", (960, 250), text_font, INFO_COLOR, center=True)
            draw_text(screen, "ESC - Konec", (960, 300), text_font, INFO_COLOR, center=True)
            
            acc = int((progress.get("correct", 0) / max(1, progress.get("total", 1))) * 100)
            draw_text(screen, f"Úspěšnost: {acc} %", (960, 400), small_font, INFO_COLOR, center=True)

        elif mode == "flashcards" and active_cards:
            card = active_cards[flash_index]
            star = "★ " if is_starred(card["term"]) else ""
            draw_text(screen, f"{star}{card['term']}", (960, 300), text_font, TERM_COLOR, center=True)
            if flash_show_definition:
                draw_text(screen, card["definition"], (960, 400), text_font, DEF_COLOR, center=True, max_width=1200)
            else:
                draw_text(screen, "[Mezerník] pro zobrazení", (960, 400), small_font, INFO_COLOR, center=True)

        elif mode == "learning" and active_cards:
            star = "★ " if is_starred(learning_question) else ""
            draw_text(screen, f"{star}{learning_question}", (960, 150), text_font, TERM_COLOR, center=True)
            
            for i, option in enumerate(learning_options):
                color = INFO_COLOR
                if learning_answered:
                    if i == learning_correct_pos: color = DEF_COLOR
                    elif i == learning_selected: color = WRONG_COLOR
                
                draw_text(screen, f"{i+1}. {option}", (300, 300 + i * 60), text_font, color, center=False, max_width=1400)
                
            if learning_answered:
                draw_text(screen, "[Mezerník] pro další otázku", (960, 600), small_font, RESULT_COLOR, center=True)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()