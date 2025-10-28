# Vysledky_voleb_2017

Popis projektu

Tento projekt slouží k automatickému stažení výsledků voleb z oficiálních stránek Českého statistického úřadu  
([volby.cz](https://www.volby.cz)) a jejich uložení do přehledného CSV souboru.  
Program postupně načítá všechny obce z vybraného územního celku a pro každou z nich uloží základní volební údaje  
a hlasy jednotlivých stran.

Instalace knihoven

1. Naklonuj nebo zkopíruj tento projekt do počítače.
2. Otevři složku projektu v terminálu (PowerShell, CMD nebo VS Code).
3. Doporučuje se vytvořit **virtuální prostředí**:
   ```bash
   python -m venv volby_env
   a aktivovat ho:
   volby_env\Scripts\activate
4. Nainstaluj potřebné knihovny:
   pip install -r requirements.txt

Spuštění projektu

Skript se spouští z příkazové řádky pomocí dvou argumentů:
python main.py "<URL_územního_celku>" "<název_výstupního_souboru.csv>"
První argument je adresa územního celku (např. okresu) z webu ČSÚ
Druhý argument je název CSV souboru, do kterého se data uloží
V PowerShellu musí být URL uzavřena v uvozovkách "...",
protože obsahuje znak &, který by jinak způsobil chybu.

Příklad spuštění

python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" "vysledky_prostejov.csv"

Agrument 1: "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"
Argument 2: "vysledky_prostejov.csv"

Průběh

✅ Argumenty v pořádku.
✅ Data byla úspěšně uložena do 'vysledky_prostejov.csv'.

Částečný výstup

kod_obce;nazev;volici_v_seznamu;vydane_obalky;platne_hlasy;Občanská demokratická strana;...
506761;Alojzov;205;145;144;29;...
589268;Bedihošť;834;527;524;51;...
