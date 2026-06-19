import pygame
import random
import sys
import os
import json

# setting up:
# odkud má program tahat data
DATA_FILE = "data_ukazka/otazky.json"
STATE_FILE = "quizlet_state.txt"

def load_data_from_json(filename):
    """Načte data z JSON souboru a převede je do požadované struktury pro hru."""
    data = {}
    if not os.path.exists(filename):
        print(f"Soubor {filename} nebyl nalezen!")
        return data
        
    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw_list = json.load(f)
            
        for item in raw_list:
            ch = item.get("kapitola")
            if ch not in data:
                data[ch] = {'OK': [], 'NOK': []}
            data[ch][item["typ"]].append(item["tvrzeni"])
            
        return data
    except Exception as e:
        print(f"Chyba při načítání JSON: {e}")
        return {}

def calculate_score(selections, truths):
    """Logika bodování pro jednu otázku."""
    sel_count = sum(selections)
    correct_sel_count = sum(1 for s, t in zip(selections, truths) if s and t)
    
    if sel_count == 2:
        if correct_sel_count == 2: return 4
        elif correct_sel_count == 1: return 0
        else: return -1
    elif sel_count == 1:
        if correct_sel_count == 1: return 1
        else: return -1
    else:
        return 0

# ==============================================================================
# PYGAME ROZHRANÍ - NEON STYLE
# ==============================================================================
BG = (10, 5, 20)           
TEXT_COLOR = (240, 240, 255)
CYAN = (0, 255, 255)       
PURPLE = (180, 50, 255)    
GREEN = (50, 255, 100)     
RED = (255, 50, 80)        
GRAY = (100, 100, 130)     

def draw_text_neon(surface, text, pos, font, main_color, glow_color, center=False, max_width=1700):
    if not text:
        return 0
        
    words = text.split(" ")
    lines = []
    current_line = ""

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
        glow_surf = font.render(line, True, glow_color)
        glow_surf.set_alpha(100)
        
        main_surf = font.render(line, True, main_color)
        
        rect = main_surf.get_rect()
        if center: rect.centerx = pos[0]
        else: rect.x = pos[0]
        rect.y = base_y + i * font.get_linesize()
        
        for offset in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            glow_rect = rect.copy()
            glow_rect.x += offset[0]
            glow_rect.y += offset[1]
            surface.blit(glow_surf, glow_rect)
            
        surface.blit(main_surf, rect)
        
    return total_height

def select_chapters_pygame(screen, font, small_font, available_chapters):
    selected = [False] * 12
    selecting = True
    clock = pygame.time.Clock()
    
    while selecting:
        screen.fill(BG)
        draw_text_neon(screen, "VÝBĚR KAPITOL", (960, 80), font, CYAN, PURPLE, center=True)
        draw_text_neon(screen, "Čísla 1-9 (pro 10 stiskni 0, pro 11 stiskni Q, pro 12 stiskni W)", (960, 130), small_font, TEXT_COLOR, PURPLE, center=True)
        draw_text_neon(screen, "ENTER = Potvrdit | ESC = Zpět", (960, 170), small_font, GRAY, BG, center=True)
        
        for i in range(12):
            ch_num = i + 1
            if ch_num not in available_chapters: continue
            
            col = i % 2
            row = i // 2
            x_pos = 660 + col * 600
            y_pos = 250 + row * 60
            
            status = "[ X ]" if selected[i] else "[   ]"
            color = CYAN if selected[i] else GRAY
            glow = PURPLE if selected[i] else BG
            draw_text_neon(screen, f"Kapitola {ch_num}:  {status}", (x_pos, y_pos), font, color, glow, center=True)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                keys_map = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4,
                            pygame.K_6: 5, pygame.K_7: 6, pygame.K_8: 7, pygame.K_9: 8, pygame.K_0: 9,
                            pygame.K_q: 10, pygame.K_w: 11}
                if event.key in keys_map:
                    idx = keys_map[event.key]
                    selected[idx] = not selected[idx]
                elif event.key == pygame.K_RETURN:
                    chosen = [i+1 for i, s in enumerate(selected) if s]
                    return chosen if chosen else [1]
                elif event.key == pygame.K_ESCAPE:
                    return []
        clock.tick(30)

KAPITOLY_POOLY = {}

def save_pool_state():
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            for ch, pools in KAPITOLY_POOLY.items():
                ok_str = "|".join(pools['OK'])
                nok_str = "|".join(pools['NOK'])
                f.write(f"{ch};OK;{ok_str}\n")
                f.write(f"{ch};NOK;{nok_str}\n")
    except Exception as e:
        pass

def load_pool_state():
    global KAPITOLY_POOLY
    if not os.path.exists(STATE_FILE): return False
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(";", 2)
                if len(parts) < 3: continue
                
                ch = int(parts[0])
                p_type = parts[1]
                statements = parts[2].split("|") if parts[2] else []
                
                if ch not in KAPITOLY_POOLY:
                    KAPITOLY_POOLY[ch] = {'OK': [], 'NOK': []}
                KAPITOLY_POOLY[ch][p_type] = statements
        return True
    except:
        return False

def generate_5c_questions(data, chapters):
    global KAPITOLY_POOLY
    questions = []
    
    if not KAPITOLY_POOLY: load_pool_state()
    
    for ch in chapters:
        if ch not in data or len(data[ch]['OK']) < 2 or len(data[ch]['NOK']) < 3:
            questions.append({'chapter': ch, 'statements': [("NEDOSTATEK DAT", False)]*5, 'selected': [False]*5})
            continue
            
        if ch not in KAPITOLY_POOLY or len(KAPITOLY_POOLY[ch]['OK']) < 2 or len(KAPITOLY_POOLY[ch]['NOK']) < 3:
            KAPITOLY_POOLY[ch] = {
                'OK': list(data[ch]['OK']),
                'NOK': list(data[ch]['NOK'])
            }
            random.shuffle(KAPITOLY_POOLY[ch]['OK'])
            random.shuffle(KAPITOLY_POOLY[ch]['NOK'])
            
        ok_choices = [KAPITOLY_POOLY[ch]['OK'].pop() for _ in range(2)]
        nok_choices = [KAPITOLY_POOLY[ch]['NOK'].pop() for _ in range(3)]
        
        combined = [(q, True) for q in ok_choices] + [(q, False) for q in nok_choices]
        random.shuffle(combined)
        
        questions.append({'chapter': ch, 'statements': combined, 'selected': [False]*5})
        
    save_pool_state()
    return questions

def main():
    pygame.init()
    pygame.display.set_caption("KNOWLEDGE TEST TERMINAL")
    screen = pygame.display.set_mode((1920, 1000), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    DB = load_data_from_json(DATA_FILE)
    available_chapters = list(DB.keys())

    available_fonts = ["consolas", "arial", "calibri", "verdana", "trebuchet ms"]
    current_font_idx = 0

    def get_fonts(font_name):
        return (
            pygame.font.SysFont(font_name, 50, bold=True),
            pygame.font.SysFont(font_name, 24),
            pygame.font.SysFont(font_name, 18)
        )

    title_font, text_font, small_font = get_fonts(available_fonts[current_font_idx])

    mode = "menu"
    trenink_cards = []
    trenink_current = None
    questions_list = []
    current_q_index = 0
    focused_option = 0
    final_scores = {}
    total_score = 0

    running = True
    while running:
        screen.fill(BG)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if mode == "menu":
                    if event.key == pygame.K_1:
                        chosen = select_chapters_pygame(screen, text_font, small_font, available_chapters)
                        if chosen:
                            trenink_cards = []
                            for c in chosen:
                                if c in DB:
                                    trenink_cards.extend([(t, True) for t in DB[c]['OK']])
                                    trenink_cards.extend([(t, False) for t in DB[c]['NOK']])
                            random.shuffle(trenink_cards)
                            if trenink_cards:
                                trenink_current = trenink_cards.pop()
                                mode = "trenink_1c"
                                focused_option = 0
                                trenink_answered = False
                                
                    elif event.key == pygame.K_2:
                        chosen = select_chapters_pygame(screen, text_font, small_font, available_chapters)
                        if chosen:
                            questions_list = generate_5c_questions(DB, chosen)
                            current_q_index = 0
                            focused_option = 0
                            mode = "trenink_5c"
                            
                    elif event.key == pygame.K_3:
                        questions_list = generate_5c_questions(DB, range(1, 13))
                        current_q_index = 0
                        focused_option = 0
                        mode = "zapocet"
                    
                    elif event.key == pygame.K_4:
                        mode = "settings"
                        
                    elif event.key == pygame.K_ESCAPE:
                        running = False

                elif mode == "settings":
                    if event.key in [pygame.K_ESCAPE, pygame.K_RETURN]: mode = "menu"
                    elif event.key == pygame.K_RIGHT:
                        current_font_idx = (current_font_idx + 1) % len(available_fonts)
                        title_font, text_font, small_font = get_fonts(available_fonts[current_font_idx])
                    elif event.key == pygame.K_LEFT:
                        current_font_idx = (current_font_idx - 1) % len(available_fonts)
                        title_font, text_font, small_font = get_fonts(available_fonts[current_font_idx])

                elif mode == "trenink_1c":
                    if event.key == pygame.K_ESCAPE: mode = "menu"
                    elif not trenink_answered:
                        if event.key in [pygame.K_UP, pygame.K_DOWN]:
                            focused_option = 1 - focused_option
                        elif event.key == pygame.K_SPACE:
                            guess = (focused_option == 0)
                            correct = trenink_current[1]
                            is_right = (guess == correct)
                            trenink_answered = True
                        elif event.key == pygame.K_RIGHT:
                            if trenink_cards: trenink_current = trenink_cards.pop()
                            else: mode = "menu"
                    else:
                        if event.key in [pygame.K_SPACE, pygame.K_RIGHT]:
                            if trenink_cards:
                                trenink_current = trenink_cards.pop()
                                trenink_answered = False
                            else:
                                mode = "menu"

                elif mode in ["trenink_5c", "zapocet"]:
                    if event.key == pygame.K_ESCAPE: mode = "menu"
                    elif event.key == pygame.K_DOWN:
                        focused_option = min(4, focused_option + 1)
                    elif event.key == pygame.K_UP:
                        focused_option = max(0, focused_option - 1)
                    elif event.key == pygame.K_SPACE:
                        q = questions_list[current_q_index]
                        q['selected'][focused_option] = not q['selected'][focused_option]
                    elif event.key == pygame.K_RIGHT:
                        current_q_index = min(len(questions_list) - 1, current_q_index + 1)
                        focused_option = 0
                    elif event.key == pygame.K_LEFT:
                        current_q_index = max(0, current_q_index - 1)
                        focused_option = 0
                    elif event.key == pygame.K_RETURN and mode in ["zapocet", "trenink_5c"]:
                        final_scores = {}
                        total_score = 0
                        for q in questions_list:
                            truths = [stmt[1] for stmt in q['statements']]
                            pts = calculate_score(q['selected'], truths)
                            final_scores[q['chapter']] = pts
                            total_score += pts
                        mode = "zapocet_table"

                elif mode == "zapocet_table":
                    if event.key == pygame.K_ESCAPE: mode = "menu"
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        current_q_index = 0
                        mode = "zapocet_review"

                elif mode == "zapocet_review":
                    if event.key == pygame.K_ESCAPE: mode = "menu"
                    elif event.key == pygame.K_RIGHT:
                        current_q_index = min(len(questions_list) - 1, current_q_index + 1)
                    elif event.key == pygame.K_LEFT:
                        current_q_index = max(0, current_q_index - 1)

        # ---------------- VYKRESLOVÁNÍ ----------------
        if mode == "menu":
            draw_text_neon(screen, "TERMINAL: KNOWLEDGE TEST", (960, 150), title_font, CYAN, PURPLE, center=True)
            draw_text_neon(screen, "1_ TRÉNINK (Pravda/Lež)", (960, 320), text_font, TEXT_COLOR, BG, center=True)
            draw_text_neon(screen, "2_ TRÉNINK KAPITOL (2 z 5)", (960, 380), text_font, TEXT_COLOR, BG, center=True)
            draw_text_neon(screen, "3_ OSTRÝ TEST (12 kapitol, +4/0/-1)", (960, 440), text_font, CYAN, PURPLE, center=True)
            draw_text_neon(screen, "4_ NASTAVENÍ FONTŮ", (960, 500), text_font, TEXT_COLOR, BG, center=True)
            draw_text_neon(screen, "ESC_ UKONČIT SYSTÉM", (960, 560), text_font, GRAY, BG, center=True)

        elif mode == "settings":
            draw_text_neon(screen, "NASTAVENÍ SYSTÉMU", (960, 150), title_font, CYAN, PURPLE, center=True)
            draw_text_neon(screen, "VÝBĚR FONTU", (960, 320), text_font, GRAY, BG, center=True)
            draw_text_neon(screen, f"◄   {available_fonts[current_font_idx].upper()}   ►", (960, 380), title_font, TEXT_COLOR, PURPLE, center=True)
            draw_text_neon(screen, "Šipky ←/→ mění font | ESC pro návrat", (960, 650), small_font, GRAY, BG, center=True)

        elif mode == "trenink_1c":
            draw_text_neon(screen, "TRÉNINK TVRZENÍ", (960, 60), title_font, CYAN, PURPLE, center=True)
            
            if trenink_current:
                draw_text_neon(screen, trenink_current[0], (960, 300), text_font, TEXT_COLOR, PURPLE, center=True, max_width=1400)
            
            if not trenink_answered:
                c_pravda = CYAN if focused_option == 0 else GRAY
                c_lez = CYAN if focused_option == 1 else GRAY
                draw_text_neon(screen, "► PRAVDA" if focused_option == 0 else "  PRAVDA", (850, 500), title_font, c_pravda, PURPLE)
                draw_text_neon(screen, "► LEŽ" if focused_option == 1 else "  LEŽ", (850, 560), title_font, c_lez, PURPLE)
            else:
                correct = trenink_current[1]
                if is_right: draw_text_neon(screen, "SPRÁVNĚ", (960, 500), title_font, GREEN, GREEN, center=True)
                else: draw_text_neon(screen, "ŠPATNĚ", (960, 500), title_font, RED, RED, center=True)
                vysv = "Tvrzení je PRAVDA (OK)" if correct else "Tvrzení je LEŽ (NOK)"
                draw_text_neon(screen, vysv, (960, 560), text_font, TEXT_COLOR, BG, center=True)

        elif mode in ["trenink_5c", "zapocet", "zapocet_review"]:
            q = questions_list[current_q_index]
            mod_nazev = "TRÉNINK KAPITOL" if mode == "trenink_5c" else "OSTRÝ TEST"
            if mode == "zapocet_review": mod_nazev = "PŘEHLED VÝSLEDKŮ"
            
            draw_text_neon(screen, f"{mod_nazev} | Otázka {current_q_index+1}/{len(questions_list)} (Kap. {q['chapter']})", (100, 40), title_font, CYAN, PURPLE)
            
            nav_text = "Šipky ↑/↓ pohyb | Mezerník zaškrtává | Šipky ←/→ přepínají otázky | ENTER odevzdá"
            if mode == "zapocet_review": nav_text = "Šipky ←/→ přepínají otázky | ESC do menu"
            draw_text_neon(screen, nav_text, (100, 100), small_font, GRAY, BG)

            y_offset = 200
            for i, (text, is_correct) in enumerate(q['statements']):
                is_selected = q['selected'][i]
                is_focused = (i == focused_option) and (mode != "zapocet_review")
                
                cursor = "► " if is_focused else "  "
                checkbox = "[X]" if is_selected else "[ ]"
                box_color = TEXT_COLOR
                glow = PURPLE if is_focused else BG
                
                if mode == "zapocet_review":
                    cursor = "  "
                    if is_selected == is_correct:
                        box_color, glow = GREEN, BG
                    else:
                        box_color, glow = RED, BG
                    text += " (PRAVDA)" if is_correct else " (LEŽ)"
                elif is_selected:
                    box_color, glow = CYAN, BG

                full_text = f"{cursor}{checkbox} {text}"
                h = draw_text_neon(screen, full_text, (100, y_offset), text_font, box_color, glow, max_width=1600)
                y_offset += h + 30

        elif mode == "zapocet_table":
            draw_text_neon(screen, "VÝSLEDKY TESTU", (960, 80), title_font, CYAN, PURPLE, center=True)
            draw_text_neon(screen, "ENTER pro detailní review chyb | ESC do menu", (960, 140), small_font, GRAY, BG, center=True)
            
            start_y = 250
            for i in range(12):
                ch_num = i + 1
                pts = final_scores.get(ch_num, 0)
                
                col = i % 2
                row = i // 2
                x_pos = 660 + col * 600
                y_pos = start_y + row * 50
                
                color = GREEN if pts == 4 else (CYAN if pts >= 0 else RED)
                draw_text_neon(screen, f"Kapitola {ch_num:>2}: {pts:>2} b.", (x_pos, y_pos), text_font, color, BG, center=True)

            verdict_color = GREEN if total_score >= 32 else RED
            verdict_text = "SPLNĚNO" if total_score >= 32 else "NESPLNĚNO"
            draw_text_neon(screen, f"CELKOVÉ SKÓRE: {total_score} / 48", (960, 650), title_font, TEXT_COLOR, PURPLE, center=True)
            draw_text_neon(screen, f"VERDIKT: {verdict_text}", (960, 720), title_font, verdict_color, verdict_color, center=True)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()