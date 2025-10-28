import sys
import csv
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin


def seber_uzemi(url: str) -> List[Dict[str, str]]:
    """
    Inputs:
        url: str
            URL vstupní stránky (ps3) se seznamem územních celků/krajů.

    Outputs:
        List[Dict[str, str]]
            Seznam slovníků s klíči:
              - 'nazev': text z 2. sloupce tabulek
              - 'url'  : absolutní odkaz z 4. sloupce tabulek

    Notes:
        Přeskočí 1. a 2. řádek v každé tabulce (hlavičky) a čte řádky od 3. dál.
    """
    r = requests.get(url)
    if r.status_code != 200:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    vysledky: List[Dict[str, str]] = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")[2:]
        for tr in rows:
            tds = tr.find_all("td")
            nazev = tds[1].get_text(strip=True)
            a = tds[3].find("a", href=True)
            if a:
                cele_url = urljoin(url, a["href"])
                vysledky.append({"nazev": nazev, "url": cele_url})

    return vysledky

 
def seber_obce(url: str) -> List[Dict[str, str]]:
    """
    Inputs:
        url: str
            URL územního celku (ps32) se seznamem obcí.

    Outputs:
        List[Dict[str, str]]
            Seznam slovníků s klíči:
            - 'kod_obce': text z 1. sloupce
              - 'nazev'   : text z 2. sloupce
              - 'url'     : absolutní odkaz ze 3. sloupce (detail obce)

    Notes:
       V každé tabulce se přeskočí první 2 řádky (hlavičky) a čte se od 3. řádku.
   """
    r = requests.get(url)
    if r.status_code != 200:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    vysledky: List[Dict[str, str]] = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")[2:]
        for tr in rows:
            tds = tr.find_all("td")
            kod_obce = tds[0].get_text(strip=True)
            nazev = tds[1].get_text(strip=True)
            a = tds[0].find("a", href=True)
            if a:
                cele_url = urljoin(url, a["href"])
                vysledky.append({"kod_obce": kod_obce, "nazev": nazev, "url": cele_url})

    return vysledky

def seber_detail(url: str) -> Dict[str, str]:
    """
    Inputs:
        url: str
            URL detailu obce (stránka s agregáty a tabulkami stran).

    Outputs:
        Dict[str, str]
            Slovník s agregovanými položkami a hlasy pro strany:
              - 'volici_v_seznamu' : hodnota ze 4. sloupce 3. řádku 1. tabulky
              - 'vydane_obalky'    : hodnota z 5. sloupce 3. řádku 1. tabulky
              - 'platne_hlasy'     : hodnota z 8. sloupce 3. řádku 1. tabulky
              - '<název strany>'   : hodnota z 3. sloupce řádku v tabulkách stran

    Notes:
        - Z prvních dvou tabulek stran bere řádky od 3. dál (po hlavičkách).
        - U druhé tabulky stran přeskočí poslední prázdný řádek (obsahuje „-“).
        - Nedělitelné mezery jsou odstraněny (\\xa0).
    """
    r = requests.get(url)
    if r.status_code != 200:
        return {}

    soup = BeautifulSoup(r.text, "html.parser")
    vysledky: Dict[str, str] = {}

    tables = soup.find_all("table")

    prvni_table = tables[0]
    row = prvni_table.find_all("tr")[2]
    tds = row.find_all("td")
    vysledky["volici_v_seznamu"] = tds[3].get_text(strip=True).replace("\xa0", "")
    vysledky["vydane_obalky"] = tds[4].get_text(strip=True).replace("\xa0", "")
    vysledky["platne_hlasy"] = tds[7].get_text(strip=True).replace("\xa0", "")
    
    for table in tables[1:3]:
        rows = table.find_all("tr")[2:]
        for tr in rows:
            tds = tr.find_all("td")
            # pokud první buňka prázdná → přeskoč celý řádek
            if not tds[0].get_text(strip=True).replace("-",""): #prázdný poslední řádek není ve skutečnosti prázdný a obsahuje "-"
                continue

            # sem se dostaneš jen pokud první buňka něco obsahuje
            klic = tds[1].get_text(strip=True)
            hodnota = tds[2].get_text(strip=True).replace("\xa0", "")
            vysledky[klic] = hodnota

    return vysledky


def uloz_do_csv(zaznamy: List[Dict[str, str]], jmeno_souboru: str) -> None:
    """
    Inputs:
        zaznamy: List[Dict[str, str]]
            Seznam záznamů; každý záznam je slovník se stejnými klíči.
        jmeno_souboru: str
            Název/ cesta k výstupnímu CSV souboru.

    Outputs:
        None
            Funkce nic nevrací; zapíše CSV soubor na disk.

    Notes:
        - Hlavička CSV je převzata z klíčů prvního záznamu.
        - Kódování UTF-8, oddělovač ';' (vhodné pro Excel v češtině).
    """
    if not zaznamy:
        # nic k uložení
        return

    hlavicka = list(zaznamy[0].keys())

    with open(jmeno_souboru, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=hlavicka, delimiter=";")
        writer.writeheader()
        writer.writerows(zaznamy)


def zkontroluj_argumenty():
    """
    Inputs:
        žádné (čte z sys.argv)

    Outputs:
        tuple[str, str]
            Dvojice (url, soubor), kde:
              - url: platná URL územního celku (musí být mezi odkazy z ps3)
              - soubor: název CSV souboru končící na '.csv'

    Notes:
        - Ověří počet argumentů (musí být 2).
        - Ověří příponu souboru (.csv).
        - Dotáže se na hlavní stránku (ps3), stáhne seznam územních celků
          a validuje, že zadaná URL je v tomto seznamu.
        - Při chybě vypíše hlášku a ukončí skript (sys.exit()).
    """
    if len(sys.argv) != 3:
        print("❌ Chyba: musíš zadat přesně 2 argumenty – URL a název .csv souboru.")
        sys.exit()

    url = sys.argv[1]
    soubor = sys.argv[2]

    # kontrola přípony
    if not soubor.lower().endswith(".csv"):
        print(f"❌ Chyba: '{soubor}' není platný CSV soubor (musí končit na .csv).")
        sys.exit()

    # načtení hlavní stránky a seznamu platných URL
    hlavni_url = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
    obce = seber_uzemi(hlavni_url)
    platne_url = [o["url"] for o in obce]

    if url not in platne_url:
        print(f"❌ Chyba: '{url}' není platná URL územního celku z hlavní stránky ČSÚ.")
        sys.exit()

    print("✅ Argumenty v pořádku.")
    return url, soubor


def main() -> None:
    """
    Hlavní řídicí funkce skriptu:
      1. Zkontroluje vstupní argumenty (URL, název souboru)
      2. Stáhne data z dané URL (seber_obce)
      3. Pro každou obec stáhne detail (seber_detail_obce)
      4. Spojí vše do listu slovníků a uloží do CSV (uloz_do_csv)
    """
    # 1 kontrola argumentů
    url, nazev_souboru = zkontroluj_argumenty()

    # 2 získání obcí z daného územního celku
    obce = seber_obce(url)
    if not obce:
        print("❌ Chyba: Nepodařilo se načíst seznam obcí.")
        sys.exit()

    # 3 načtení detailů všech obcí
    vysledky = []
    for obec in obce:
        vysledky.append({"kod_obce": obec["kod_obce"], "nazev": obec["nazev"], **seber_detail(obec["url"])})

    # 4 uložení výsledků do CSV
    uloz_do_csv(vysledky, nazev_souboru)
    print(f"✅ Data byla úspěšně uložena do '{nazev_souboru}'.")


# --- spuštění skriptu ---
if __name__ == "__main__":
    main()