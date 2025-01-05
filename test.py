import nltk
nltk.download('punkt')

from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Funkce pro určení druhu věty
def urceni_druhu_vety(veta):
    if veta.endswith("?"):
        return "Tázací věta"
    elif veta.endswith("!"):
        return "Rozkazovací věta"
    elif "kéž" in veta or "kéž by" in veta:
        return "Přací věta"
    else:
        return "Oznamovací věta"

# Funkce pro spočítání slovních druhů
def spocitat_slovni_druhy(slova):
    sloveso_tagy = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
    pocet_sloves = sum(1 for word, tag in slova if tag in sloveso_tagy)
    pocet_podstatnych_jmen = sum(1 for word, tag in slova if tag.startswith("NN"))
    pocet_pridavnych_jmen = sum(1 for word, tag in slova if tag.startswith("JJ"))
    pocet_prislovci = sum(1 for word, tag in slova if tag.startswith("RB"))
    pocet_zajmen = sum(1 for word, tag in slova if tag.startswith("PR"))
    pocet_spojek = sum(1 for word, tag in slova if tag.startswith("CC"))
    return {
        "Počet sloves": pocet_sloves,
        "Počet podstatných jmen": pocet_podstatnych_jmen,
        "Počet přídavných jmen": pocet_pridavnych_jmen,
        "Počet příslovcí": pocet_prislovci,
        "Počet zájmen": pocet_zajmen,
        "Počet spojek": pocet_spojek
    }

# Hlavní funkce programu
def analyzovat_vetu(veta):
    druh_vety = urceni_druhu_vety(veta)
    tokeny = word_tokenize(veta)
    oznacena_slova = pos_tag(tokeny)
    slovni_druhy_pocet = spocitat_slovni_druhy(oznacena_slova)
    
    print(f"Druh věty: {druh_vety}")
    print("Počty jednotlivých slovních druhů:")
    for slovni_druh, pocet in slovni_druhy_pocet.items():
        print(f"{slovni_druh}: {pocet}")

# Příklad použití
veta = input("Zadejte větu: ")
analyzovat_vetu(veta)
