import json

# 1. Otevřeme soubor v režimu čtení ("r" = read) s UTF-8 kódováním, aby fungovala čeština
with open("dummy_data.json", "r", encoding="utf-8") as soubor:
    
    # 2. Knihovna json převede text ze souboru rovnou na Python seznam (list)
    data = json.load(soubor)

# 3. Teď už pracujeme s klasickým Pythonem
print(f"Úspěšně jsem načetl {len(data)} otázek!\n")

# Projdeme všechny položky
for polozka in data:
    kapitola = polozka["kapitola"]
    typ = polozka["typ"]
    text = polozka["tvrzeni"]
    
    print(f"Kapitola {kapitola} | Typ: {typ}")
    print(f"Tvrzení: {text}")
    print("-" * 30)