import os
import re

# Zadejte soubor na otestování:
FILENAME = "Blue"
TARGET_FILE = f"Cybersec/THM_Cybersecurity101/THM_{FILENAME}.txt"

# Blue má spoustu # takže je to fucked

def format_inline_commands(text: str) -> str:
    # 1. Celé URL odkazy
    text = re.sub(r'(https?://[^\s`]+)', r'`\1`', text)
    
    # 2. IP adresy (včetně portů)
    text = re.sub(r'(?<!/)\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b', r'`\g<0>`', text)

    # 3. PowerShell Cmdlety (např. Get-ChildItem, Invoke-Command, Where-Object)
    text = re.sub(r'\b([A-Z][a-zA-Z]+-[A-Z][a-zA-Z0-9]+)\b', r'`\1`', text)

    # 4. Parametry / přepínače (např. -Path, -Property, -eq, -Descending)
    text = re.sub(r'(?<=\s)(-[a-zA-Z]+)\b', r'`\1`', text)

    return text


def prettify_text_to_markdown(content: str, filename: str) -> str:
    lines = content.splitlines()
    if not lines:
        return ""

    title = os.path.splitext(os.path.basename(filename))[0].replace('-', ' ').replace('_', ' ').replace('THM', 'TryHackMe:')
    md_lines = [f"# {title}\n"]

    in_code_block = False

    for line in lines:
        # Nahrazení nezlomitelných mezer (\xa0) běžnými mezerami
        normalized_line = line.replace('\xa0', ' ')
        stripped = normalized_line.strip()

        # Prázdný řádek
        if not stripped:
            if in_code_block:
                md_lines.append("```\n")
                in_code_block = False
            continue

        # 1. Odstranění hashtagů (#)
        clean_line = re.sub(r'#+', '', stripped).strip()
        if not clean_line:
            continue

        # 2. Detekce příkazové řádky / promptu
        # 100% bezpečný regex:
        is_cmd_line = bool(re.match(r'^(root@|kali@|user@|\$|>|PS\s+|(?:\b(nc|nmap|gobuster|ffuf|sqlmap|hydra|hashcat|john|cat|ls|cd|grep|curl|wget|mysql|sudo|su|echo|python|python3)\b))', clean_line))

        if is_cmd_line:
            if not in_code_block:
                in_code_block = True
                md_lines.append("```bash")
            md_lines.append(clean_line)
            continue
        else:
            if in_code_block:
                md_lines.append("```\n")
                in_code_block = False

        # 3. Detekce odrážek (včetně vnořených s mezerami)
        bullet_match = re.match(r'^(\s*)[•\-\*]\s*(.*)$', normalized_line)
        if bullet_match:
            leading_spaces = bullet_match.group(1)
            bullet_body = bullet_match.group(2).strip()

            # Pokud je odrážka prázdná (např. samotné "- "), přeskočíme
            if not bullet_body:
                continue

            # Spočítáme úroveň zanoření (každé 2-4 mezery = 1 úroveň zanoření)
            indent_level = len(leading_spaces) // 2
            indent = "  " * indent_level

            formatted_body = format_inline_commands(bullet_body)
            md_lines.append(f"{indent}* {formatted_body}")
            continue

        # 4. Detekce hluboce odsazeného textu (např. kód pod odrážkou)
        if normalized_line.startswith(('    ', '\t')) and not stripped.startswith(('*', '-', '•')):
            md_lines.append(f"  ```\n  {stripped}\n  ```")
            continue

        # 5. Pokud řádek nezačíná odrážkou a je krátký -> považujeme ho za H2 Nadpis
        if len(clean_line) < 60 and not clean_line.endswith(('.', ':', ';')):
            md_lines.append(f"\n## {clean_line}\n")
            continue

        # 6. Běžný text
        formatted_line = format_inline_commands(clean_line)
        md_lines.append(f"{formatted_line}\n")

    if in_code_block:
        md_lines.append("```\n")

    return "\n".join(md_lines)


def run_single_test():
    if not os.path.exists(TARGET_FILE):
        print(f"Chyba: Soubor '{TARGET_FILE}' nebyl nalezen.")
        return

    out_file = f"{os.path.splitext(TARGET_FILE)[0]}.md"

    with open(TARGET_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        raw_content = f.read()

    converted = prettify_text_to_markdown(raw_content, TARGET_FILE)

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(converted)

    print(f"Hotovo! Vytvořen otestovaný soubor: '{out_file}'")


if __name__ == '__main__':
    run_single_test()