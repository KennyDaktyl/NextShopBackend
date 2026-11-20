"""Dane i treści dla komendy create_gate_remotes (kategoria „Piloty do bram”).

Wszystkie 13 pilotów to ZAMIENNIKI (marka „Zamiennik”), a pole compatible_brand
wskazuje producenta oryginału. Fakty techniczne dotyczą systemu, do którego
zamiennik jest przeznaczony (częstotliwość, typ kodu) i pochodzą ze źródeł
w SOURCES. Procedur programowania nie podajemy: instrukcje producentów opisują
piloty oryginalne, a nie zamienniki – w FAQ jest bezpieczna odpowiedź ogólna.

{price} w tekstach jest podstawiane aktualną ceną produktu przy każdym
uruchomieniu komendy (cena 69 zł jest tymczasowa).
"""

SERVICE_URL = "/uslugi/mobilne-kodowanie-pilotow-do-bram"
PHONE = "506 029 980"
ADDRESS = "ul. Wspólna 2 w Rybnej"
HOURS = "pn–pt 8–17"
DEFAULT_PRICE = "69.00"
DEFAULT_QTY = 1
GOOGLE_PRODUCT_CATEGORY = "6741"  # Dom i ogród > Sprzęt AGD > Piloty i klawiatury do bram garażowych

SAFE_ANSWER = (
    "Procedura zależy od modelu odbiornika. Najprościej sprawdzić ją w instrukcji "
    f"napędu albo zadzwonić: {PHONE}, pomogę ustalić model i zaprogramuję pilota."
)

LINK_CLASS = "text-blue-600 underline"


def link(anchor, href=SERVICE_URL):
    return f'<a class="{LINK_CLASS}" href="{href}">{anchor}</a>'


# --- Producenci ------------------------------------------------------------------
# slug -> dane; "aliases" to nazwy istniejących rekordów Brand do dopasowania.
BRANDS = {
    "zamiennik": {
        "name": "Zamiennik",
        "aliases": ["Zamiennik"],
        "description": "Produkty nieoryginalne, przeznaczone do współpracy z urządzeniami innych producentów.",
        "website": "",
    },
    "nice": {
        "name": "Nice",
        "aliases": ["Nice"],
        "description": "Włoski producent automatyki do bram wjazdowych, bram garażowych, szlabanów i rolet.",
        "website": "https://www.niceforyou.com",
    },
    "came": {
        "name": "CAME",
        "aliases": ["CAME", "Came"],
        "description": "Włoski producent automatyki do bram przesuwnych, skrzydłowych i garażowych oraz szlabanów.",
        "website": "https://www.came.com",
    },
    "faac": {
        "name": "FAAC",
        "aliases": ["FAAC", "Faac"],
        "description": "Włoski producent napędów do bram wjazdowych i garażowych oraz szlabanów.",
        "website": "https://www.faac.com",
    },
    "bft": {
        "name": "BFT",
        "aliases": ["BFT", "Bft"],
        "description": "Włoski producent automatyki do bram, drzwi garażowych i szlabanów.",
        "website": "https://www.bft-automation.com",
    },
    "beninca": {
        "name": "Beninca",
        "aliases": ["Beninca", "Benincà"],
        "description": "Włoski producent napędów do bram przesuwnych, skrzydłowych i garażowych.",
        "website": "https://www.beninca.com",
    },
    "somfy": {
        "name": "Somfy",
        "aliases": ["Somfy", "SOMFY"],
        "description": "Francuski producent napędów do bram, rolet, markiz i żaluzji.",
        "website": "https://www.somfy.pl",
    },
    "hormann": {
        "name": "Hörmann",
        "aliases": ["Hörmann", "Hormann"],
        "description": "Niemiecki producent bram garażowych, drzwi i napędów do bram.",
        "website": "https://www.hormann.pl",
    },
}

# --- Kategoria -------------------------------------------------------------------
CATEGORY = {
    "name": "Piloty do bram",
    "slug": "piloty-do-bram",
    "parent_slug": "produkty",
    "order": 3,
    "item_label": "Piloty do bram",
    "h1_tag": "Piloty do bram garażowych i wjazdowych",
    "meta_title": "Piloty do bram – zamienniki Nice, CAME, FAAC | Rybna",
    "meta_description": (
        "Zamienniki pilotów do bram od {price} zł: Nice, CAME, FAAC, BFT, Beninca, "
        "Somfy, Hörmann. Wysyłka, odbiór lub kodowanie w Rybnej i z dojazdem."
    ),
    "description": (
        "Zamienniki pilotów do bram wjazdowych i garażowych, przeznaczone do napędów "
        "Nice, CAME, FAAC, BFT, Beninca, Somfy i Hörmann. Pilot od {price} zł, "
        "z wysyłką albo do odbioru w Rybnej."
    ),
    "seo_text": (
        '<h2 class="mt-6 mb-2 text-xl font-semibold">Jak dobrać pilot do bramy</h2>'
        "<p>Zanim zamówisz pilota, ustal, do jakiego systemu ma pasować. Najszybciej "
        "zrobisz to na trzy sposoby. Po pierwsze, obejrzyj obecny pilot – producent "
        "zwykle umieszcza logo i nazwę modelu na obudowie albo na tylnej ściance pod "
        "klapką baterii. Po drugie, znajdź naklejkę znamionową na napędzie bramy lub na "
        "obudowie centrali sterującej – jest na niej marka i model napędu. Po trzecie, "
        "sprawdź częstotliwość: większość systemów pracuje na 433,92 MHz albo na 868 MHz "
        "i pilot z innego pasma nie zadziała, nawet jeśli wygląda podobnie.</p>"
        "<p>Pilot musi pasować do odbiornika, a nie tylko do marki napędu. Ten sam "
        "producent stosuje różne systemy radiowe, z kodem stałym albo zmiennym, więc "
        "dwa piloty jednej marki nie zawsze są zamienne. Wszystkie piloty w tej "
        "kategorii to zamienniki, czyli piloty nieoryginalne, opisane jako przeznaczone "
        "do konkretnych systemów.</p>"
        "<p>Nowy pilot trzeba zapisać w pamięci odbiornika. Możesz to zrobić "
        f"samodzielnie według instrukcji napędu albo przyjechać do punktu przy {ADDRESS} "
        f"({HOURS}). Jeśli nie masz czasu albo nie wiesz, gdzie jest sterownik, zamów "
        f"{link('pilot do bramy z dojazdem i programowaniem')}. Gdy masz wątpliwości, "
        f"czy pilot będzie pasował, zadzwoń: {PHONE} – pomogę ustalić model, zanim "
        "złożysz zamówienie.</p>"
    ),
}

# --- Źródła faktów (raport dla właściciela, nie publikowane) ---------------------
SOURCES = {
    "faac_xt4": [
        "https://www.manualslib.com/manual/2118061/Faac-Xt-868-Slh-Lr.html (deklaracja FAAC: 868,35 MHz)",
        "https://manuals.plus/m/0ccc1b44192aae7b508b6aa8ebd52429c1bbd98a15caedb52729aeb1cae4d5a3 (instrukcja XT2/XT4 868 SLH LR)",
    ],
    "hormann_bisecur": [
        "https://www.vartai.eu/uploads/userfiles/pdf/Pulteliai/Hormann/HORMANN%20hse%204%20bs/hoermann-hse4-bisecur-DE.pdf (instrukcja Hörmann TR20A229)",
        "https://garagentore-weber.de/hoermann-hse-4-bs/",
    ],
    "beninca_togo": [
        "https://www.beninca.com/en/product/transmitters/to-go2va.html",
        "https://benincauk.co.uk/p/to-go-va/ (2VA zastępuje wycofany 2WV; odbiorniki ONE2WB, ONE2WI)",
    ],
    "came_top432na": [
        "https://ivolta.pl/top-432na-pilot-dwukanalowy/2547/produkt/",
        "https://twojabrama.pl/promocje/3206-promocja-came-pilot-dwukanalowy-top-432na-top-432-sa.html",
        "https://all4gates.eu/handsender-came-top-432na.html",
    ],
    "nice_flor": [
        "https://napeddobramy.pl/pilot-4-kanalowy-nice-flo4r-s",
        "https://sklep-elektronik.pl/automatyka-dla-domu/pilot-do-bram-nice-flor-s-4-kanalowy-43392mhz-oryginal-flo4r-s.html",
    ],
    "nice_smilo": [
        "https://www.liberotech.it/ww/433-92-mhz-4ch-rolling-code-radio-controlled-nice-smilo-sm4.html",
        "https://www.zenderservice.be/en/products/nice-smilo-sm4-afstandsbediening",
    ],
    "bft_mitto": [
        "https://automatyka.shop/product-pol-31-PILOT-DO-BRAM-BFT-MITTO-B2-RCB-2-KANALOWY.html",
        "https://sklep-elektronik.pl/automatyka-dla-domu/pilot-do-bram-bft-mitto-b2-rcb-b-rcb02-2-kanalowy.html",
    ],
}

GENERAL = "odpowiedź ogólna (zamiennik, brak instrukcji producenta zamiennika)"

# --- Piloty ----------------------------------------------------------------------
# Klucze:
#   service_id     – pozycja usługowa, z której kopiujemy plik zdjęcia (nowy plik)
#   compatible     – slug marki oryginału (BRANDS)
#   label          – „{Producent} {Model}” używane w frazach i FAQ
#   meta_label     – wersja do meta title
#   specs          – lista (parametr, wartość); tylko potwierdzone dane
#   battery        – typ baterii zamiennika; None = niepotwierdzony (FAQ o baterii pominięte)
#   sources        – klucz SOURCES albo None
REMOTES = [
    {
        "service_id": 656,
        "compatible": "bft",
        "label": "BFT Mitto",
        "meta_label": "BFT Mitto zamiennik",
        "name": "Pilot do bramy BFT Mitto – zamiennik 433,92 MHz",
        "slug": "pilot-bft-mitto-zamiennik",
        "sku": "PB-BFT-MITTO-007",
        "color": "czarny",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do systemu", "BFT Mitto"),
            ("Częstotliwość", "433,92 MHz"),
            ("Typ kodu", "zmienny (rolling code)"),
            ("Liczba przycisków", "2"),
            ("Kolor", "czarny"),
        ],
        "battery": None,
        "sources": "bft_mitto",
        "short": "Zamiennik pilota BFT Mitto: 2 przyciski, 433,92 MHz, kod zmienny. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot BFT Mitto (zamiennik) 433,92 MHz, kod zmienny, za {price} zł. Sprawdź zgodność z napędem BFT i jak dodać pilota. Wysyłka lub kodowanie w Rybnej.",
        "intro": (
            "Pilot BFT Mitto w wersji zamiennika to dwuprzyciskowy nadajnik do bram "
            "wjazdowych i garażowych z automatyką BFT. Oryginalne piloty z rodziny Mitto "
            "pracują na częstotliwości 433,92 MHz z kodem zmiennym i do takich instalacji "
            "przeznaczony jest ten egzemplarz. To pilot nieoryginalny, tańszy od nadajnika "
            "producenta. Przyda się jako dodatkowy pilot dla domownika, zapasowy egzemplarz "
            "do drugiego samochodu albo następca pilota, który zgubił się lub uległ zniszczeniu."
        ),
        "compat": (
            "Zamiennik jest przeznaczony do instalacji, w których działają oryginalne piloty "
            "BFT Mitto – w starszej wersji Mitto 2 i w nowszej Mitto B2, które według "
            "sprzedawców są ze sobą zgodne. Odbiornik radiowy może być wbudowany w centralę "
            "sterującą napędu albo zamontowany osobno. Sam napis BFT na napędzie nie "
            "przesądza o zgodności, bo liczy się odbiornik. Jeśli nie wiesz, jaki masz, "
            "wyślij mi zdjęcie naklejki z napędu lub obecnego pilota – sprawdzę to przed zakupem."
        ),
        "recognize": (
            "Oryginalny BFT Mitto ma płaską, prostokątną obudowę z zaokrąglonymi rogami, "
            "dwa przyciski obok siebie w górnej części i logo BFT w dolnej. Model i "
            "częstotliwość znajdziesz zwykle na tylnej ściance pilota lub pod klapką baterii. "
            "Drugą wskazówką jest naklejka znamionowa na napędzie albo na skrzynce centrali – "
            "jeśli jest na niej BFT i oznaczenie 433 MHz, to dobry trop."
        ),
        "prog_intro": (
            "Zamiennik BFT Mitto, podobnie jak oryginał, trzeba zapisać w pamięci odbiornika "
            "Twojej bramy."
        ),
        "replace_answer": (
            "Tak, jeśli obecny pilot to BFT Mitto (Mitto 2 lub Mitto B2) i brama działa "
            "w systemie 433,92 MHz z kodem zmiennym. Zamiennik nie zastąpi pilotów innych "
            "marek ani systemów. W razie wątpliwości wyślij zdjęcie starego pilota lub "
            f"zadzwoń: {PHONE}."
        ),
    },
    {
        "service_id": 659,
        "compatible": "beninca",
        "label": "Beninca To.Go",
        "meta_label": "Beninca To.Go zamiennik",
        "name": "Pilot do bramy Beninca To.Go – zamiennik",
        "slug": "pilot-beninca-togo-zamiennik",
        "sku": "PB-BENINCA-TOGO-005",
        "color": "czarny z szarymi przyciskami",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do systemu", "Beninca To.Go"),
            ("Liczba przycisków", "2"),
            ("Kolor", "czarny, szare przyciski"),
        ],
        "battery": None,
        "sources": "beninca_togo",
        "short": "Zamiennik pilota Beninca To.Go z dwoma szarymi przyciskami. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot Beninca To.Go (zamiennik) z 2 przyciskami za {price} zł. Sprawdź, którą wersję To.Go masz i jak dodać pilota do bramy. Wysyłka lub kodowanie w Rybnej.",
        "intro": (
            "Pilot Beninca To.Go w wersji zamiennika ma czarną obudowę z dwoma szarymi "
            "przyciskami i napisem TO.GO w dolnej części. Jest przeznaczony do bram "
            "wjazdowych i garażowych z napędami Beninca, w których pracują piloty z serii "
            "To.Go. To pilot nieoryginalny, tańszy od nadajnika producenta. Zanim go "
            "zamówisz, ustal, którą wersję To.Go masz w domu – w tej serii są modele "
            "o różnym kodowaniu, a od tego zależy, czy odbiornik przyjmie nowego pilota."
        ),
        "compat": (
            "Beninca produkowała piloty To.Go w kilku wersjach. Obecny model TO.GO 2VA "
            "zastąpił wycofany TO.GO 2WV, a oba różnią się sposobem kodowania. Dlatego "
            "zgodność tego zamiennika zależy od odbiornika zamontowanego w Twojej "
            "instalacji, a nie od samej marki napędu. Jeśli masz stary pilot, porównaj "
            "oznaczenie na jego tylnej ściance. Gdy nie masz pewności, wyślij mi zdjęcie "
            "pilota albo naklejki z napędu – pomogę ustalić wersję przed zakupem."
        ),
        "recognize": (
            "Piloty Beninca To.Go mają wydłużoną, prostokątną obudowę z napisem TO.GO lub "
            "logo Beninca. Oznaczenie modelu, np. 2VA albo 2WV, znajduje się zwykle na "
            "tylnej ściance lub na płytce po zdjęciu klapki baterii. Pomocna jest też "
            "naklejka na napędzie albo na obudowie centrali, gdzie producent podaje model "
            "urządzenia. Kolor przycisków bywa różny w zależności od wersji, więc nie "
            "warto opierać się tylko na wyglądzie."
        ),
        "prog_intro": (
            "Zamiennik Beninca To.Go zapisuje się w pamięci odbiornika, a sposób zależy "
            "od wersji systemu w Twojej bramie."
        ),
        "replace_answer": (
            "Zastąpi go, jeśli Twój odbiornik obsługuje ten typ pilota To.Go. Seria To.Go "
            "ma wersje o różnym kodowaniu (np. 2VA i wycofany 2WV), dlatego najpierw "
            "sprawdź oznaczenie na starym pilocie albo napędzie. Możesz też wysłać zdjęcie "
            f"lub zadzwonić: {PHONE}."
        ),
    },
    {
        "service_id": 660,
        "compatible": "beninca",
        "label": "Beninca To.Go 2VA",
        "meta_label": "Beninca To.Go 2VA zamiennik",
        "name": "Pilot do bramy Beninca To.Go 2VA – zamiennik 433,92 MHz",
        "slug": "pilot-beninca-togo-2va-zamiennik",
        "sku": "PB-BENINCA-TOGO-2VA",
        "color": "czarny z zielonymi przyciskami",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do systemu", "Beninca To.Go 2VA"),
            ("Częstotliwość", "433,92 MHz"),
            ("Typ kodu", "zmienny (w oryginale ARC lub HCS)"),
            ("Liczba przycisków", "2"),
            ("Kolor", "czarny, zielone przyciski"),
        ],
        "battery": None,
        "sources": "beninca_togo",
        "short": "Zamiennik pilota Beninca To.Go 2VA: 2 przyciski, 433,92 MHz, kod zmienny. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot Beninca To.Go 2VA (zamiennik) 433,92 MHz za {price} zł. Sprawdź zgodność z odbiornikiem i jak dodać pilota. Wysyłka lub kodowanie w Rybnej.",
        "intro": (
            "Pilot Beninca To.Go 2VA w wersji zamiennika to nadajnik z dwoma zielonymi "
            "przyciskami, przeznaczony do bram wjazdowych i garażowych z automatyką "
            "Beninca. Oryginalny TO.GO 2VA pracuje na częstotliwości 433,92 MHz z kodem "
            "zmiennym – według producenta może nadawać w kodowaniu ARC albo HCS. To pilot "
            "nieoryginalny, tańszy od nadajnika Beninca, przydatny jako kolejny pilot "
            "w rodzinie albo zastępstwo za zgubiony egzemplarz."
        ),
        "compat": (
            "Zamiennik jest przeznaczony do instalacji, w których pracują oryginalne piloty "
            "TO.GO 2VA. Beninca podaje, że ten model zastąpił wycofany TO.GO 2WV, a wśród "
            "odbiorników współpracujących z oryginałem wymienia m.in. zewnętrzny ONE2WB "
            "i wtykowy ONE2WI. Odbiornik może też być wbudowany w centralę napędu. "
            "Kod stały nie jest w tym modelu obsługiwany, więc nie zastąpi on starszych "
            "pilotów na kod stały. Przy wątpliwościach wyślij zdjęcie odbiornika lub pilota."
        ),
        "recognize": (
            "Oryginalny TO.GO 2VA ma czarną obudowę z logo Beninca i dwa przyciski. Nazwa "
            "modelu jest zwykle nadrukowana na tylnej ściance lub widoczna po zdjęciu "
            "klapki baterii. Na naklejce znamionowej napędu albo odbiornika sprawdzisz "
            "producenta i częstotliwość – powinno to być 433,92 MHz. Jeśli na Twoim pilocie "
            "jest oznaczenie 2WV, to starsza wersja i warto to zaznaczyć przy zamówieniu."
        ),
        "prog_intro": (
            "Zamiennik Beninca To.Go 2VA trzeba zapisać w pamięci odbiornika Twojej bramy."
        ),
        "replace_answer": (
            "Tak, jeśli obecny pilot to TO.GO 2VA albo inny pilot na 433,92 MHz z kodem "
            "zmiennym obsługiwany przez Twój odbiornik Beninca. Nie zastąpi pilota na kod "
            "stały ani pilotów innych marek. Gdy nie masz pewności, wyślij zdjęcie starego "
            f"pilota albo zadzwoń: {PHONE}."
        ),
    },
    {
        "service_id": 653,
        "compatible": "came",
        "label": "CAME SPACE",
        "meta_label": "CAME zamiennik SPACE",
        "name": "Pilot do bramy CAME – zamiennik SPACE",
        "slug": "pilot-came-space-zamiennik",
        "sku": "PB-CAME-025",
        "color": "czarny",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Oznaczenie na obudowie", "SPACE"),
            ("Przeznaczony do", "napędów CAME"),
            ("Liczba przycisków", "2"),
            ("Kolor", "czarny"),
        ],
        "battery": None,
        "sources": None,
        "copy_photos": True,
        "short": "Zamiennik pilota do napędów CAME z napisem SPACE, 2 przyciski. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot do bram CAME, zamiennik SPACE z 2 przyciskami, za {price} zł. Sprawdź zgodność z napędem i jak dodać pilota. Wysyłka lub kodowanie w Rybnej.",
        "intro": (
            "Pilot CAME SPACE to zamiennik z dwoma przyciskami w owalnej, czarnej obudowie "
            "z napisem SPACE w dolnej części. Jest przeznaczony do bram wjazdowych "
            "i garażowych z napędami CAME. To pilot nieoryginalny – nie ma na nim logo "
            "CAME – i kosztuje mniej niż nadajnik producenta. Zanim go zamówisz, sprawdź, jaki pilot masz obecnie, bo CAME stosuje "
            "w swoich pilotach różne systemy radiowe."
        ),
        "compat": (
            "CAME produkuje piloty pracujące w różnych systemach – na przykład popularny "
            "TOP-432NA działa na 433,92 MHz z kodem stałym, a inne serie korzystają "
            "z innych rozwiązań. Zgodność tego zamiennika zależy więc od odbiornika "
            "w Twoim napędzie. Najprościej porównać go z obecnym pilotem albo podać mi "
            "model napędu z naklejki znamionowej. Jeśli przyślesz zdjęcie, sprawdzę, "
            "czy ten pilot będzie pasował, zanim złożysz zamówienie."
        ),
        "recognize": (
            "Oryginalne piloty CAME mają logo producenta na przodzie obudowy, a nazwę "
            "modelu – np. TOP-432NA – na tylnej ściance lub pod klapką baterii. Ten "
            "zamiennik rozpoznasz po owalnym kształcie, dwóch okrągłych przyciskach "
            "i napisie SPACE. Model napędu odczytasz z naklejki na jego obudowie albo na "
            "skrzynce centrali sterującej. Tam często jest też podana częstotliwość radia."
        ),
        "prog_intro": (
            "Zamiennik CAME SPACE trzeba zapisać w pamięci odbiornika Twojej bramy."
        ),
        "replace_answer": (
            "To zależy od systemu, w którym działa Twój obecny pilot. CAME stosuje różne "
            "systemy radiowe, a model, do którego ten zamiennik jest przeznaczony, muszę "
            "potwierdzić. Wyślij mi zdjęcie starego pilota lub naklejki z napędu albo "
            f"zadzwoń: {PHONE} – sprawdzę przed zakupem."
        ),
    },
    {
        "service_id": 658,
        "compatible": "came",
        "label": "CAME TOP-432NA",
        "meta_label": "CAME TOP-432NA zamiennik",
        "name": "Pilot do bramy CAME TOP-432NA – zamiennik 433,92 MHz",
        "slug": "pilot-came-top-432na-zamiennik",
        "sku": "PB-CAME-TOP432NA",
        "color": "szary",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do systemu", "CAME TOP-432NA"),
            ("Częstotliwość", "433,92 MHz"),
            ("Typ kodu", "stały"),
            ("Liczba przycisków", "2"),
            ("Kolor", "szary"),
        ],
        "battery": None,
        "sources": "came_top432na",
        "short": "Zamiennik pilota CAME TOP-432NA: 2 przyciski, 433,92 MHz, kod stały. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot CAME TOP-432NA (zamiennik) 433,92 MHz, kod stały, za {price} zł. Sprawdź zgodność z odbiornikiem CAME i jak dodać pilota. Wysyłka lub odbiór w Rybnej.",
        "intro": (
            "Pilot CAME TOP-432NA w wersji zamiennika to szary, dwuprzyciskowy nadajnik "
            "z otworem na kółko do kluczy. Jest przeznaczony do bram wjazdowych, "
            "garażowych i szlabanów z automatyką CAME, w których pracują piloty serii TOP "
            "na częstotliwości 433,92 MHz. Oryginalny TOP-432NA nadaje kod stały. Ten "
            "egzemplarz to pilot nieoryginalny, tańszy od nadajnika producenta – dobry "
            "jako dodatkowy pilot albo następca zgubionego."
        ),
        "compat": (
            "Oryginalne piloty TOP-432NA współpracują według sprzedawców z odbiornikami "
            "serii TOP firmy CAME, m.in. RE432, RBE4N i RBE41, oraz z kartami radiowymi "
            "AF43S montowanymi w centralach. Zamiennik jest przeznaczony do takich samych "
            "instalacji. Ponieważ to kod stały, odbiornik musi pracować w tym trybie – "
            "piloty CAME z kodem zmiennym to inny system. Jeśli nie wiesz, co masz w "
            "skrzynce sterownika, przyślij zdjęcie, a pomogę to ustalić."
        ),
        "recognize": (
            "Oryginalny TOP-432NA ma jasnoszarą obudowę, dwa przyciski w górnej części "
            "i logo CAME na dole, przy otworze na kółko. Oznaczenie TOP-432NA oraz "
            "częstotliwość 433,92 MHz znajdziesz zwykle na tylnej ściance albo pod "
            "klapką baterii. Sprawdź też naklejkę na centrali sterującej – jeśli jest na "
            "niej karta radiowa AF43S lub odbiornik serii TOP, to dobry znak."
        ),
        "prog_intro": (
            "Zamiennik CAME TOP-432NA, podobnie jak oryginał, musi zostać zapisany "
            "w odbiorniku pracującym z kodem stałym."
        ),
        "replace_answer": (
            "Tak, jeśli Twój obecny pilot to CAME TOP-432NA albo inny pilot serii TOP na "
            "433,92 MHz z kodem stałym. Nie zastąpi pilotów CAME z kodem zmiennym ani "
            "pilotów innych marek. W razie wątpliwości wyślij zdjęcie starego pilota "
            f"lub zadzwoń: {PHONE}."
        ),
    },
    {
        "service_id": 654,
        "compatible": "faac",
        "label": "FAAC Fix",
        "meta_label": "FAAC Fix zamiennik",
        "name": "Pilot do bramy FAAC – zamiennik Fix",
        "slug": "pilot-faac-fix-zamiennik",
        "sku": "PB-FAAC-FIX",
        "color": "czarny",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do", "napędów FAAC"),
            ("Liczba przycisków", "2 (duży i mały)"),
            ("Kolor", "czarny"),
        ],
        "battery": None,
        "sources": None,
        "short": "Zamiennik pilota do napędów FAAC w czarnej obudowie z dwoma przyciskami. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot do bram FAAC, zamiennik Fix z 2 przyciskami, za {price} zł. Sprawdź zgodność z napędem FAAC i jak dodać pilota. Wysyłka lub kodowanie w Rybnej.",
        "intro": (
            "Pilot FAAC Fix to zamiennik w zwartej, czarnej obudowie z fakturą, z jednym "
            "dużym i jednym małym przyciskiem oraz diodą w rogu. Jest przeznaczony do bram "
            "wjazdowych i garażowych z napędami FAAC. To pilot nieoryginalny, bez logo "
            "producenta, tańszy od nadajnika FAAC. Ponieważ FAAC stosuje piloty na różnych "
            "częstotliwościach i z różnym kodowaniem, przed zamówieniem ustal, w jakim "
            "systemie działa Twoja brama."
        ),
        "compat": (
            "W ofercie FAAC są piloty pracujące na 433 MHz i na 868 MHz, z kodem stałym "
            "albo zmiennym SLH. Pilot z innego pasma lub z innym kodowaniem nie zostanie "
            "przyjęty przez odbiornik, dlatego zgodność tego zamiennika trzeba potwierdzić "
            "dla konkretnej instalacji. Najprościej porównać go z obecnym pilotem albo "
            "odczytać model odbiornika z naklejki w skrzynce sterownika. Przyślij mi "
            "zdjęcie – sprawdzę, czy ten pilot będzie pasował."
        ),
        "recognize": (
            "Oryginalne piloty FAAC mają logo producenta na obudowie, a nazwę modelu "
            "i częstotliwość – na tylnej ściance lub na płytce pod klapką baterii. "
            "Oznaczenia w rodzaju 433 albo 868 i skrót SLH wskazują pasmo i typ kodu. "
            "Ten zamiennik poznasz po jednym dużym i jednym małym przycisku w czarnej, "
            "chropowatej obudowie. Model napędu znajdziesz na naklejce znamionowej."
        ),
        "prog_intro": "Zamiennik FAAC Fix trzeba zapisać w pamięci odbiornika Twojej bramy.",
        "replace_answer": (
            "To zależy od systemu Twojej bramy. FAAC ma piloty na 433 i 868 MHz, z kodem "
            "stałym i zmiennym, a system, do którego ten zamiennik jest przeznaczony, "
            "muszę potwierdzić. Wyślij zdjęcie starego pilota lub naklejki z napędu albo "
            f"zadzwoń: {PHONE}."
        ),
    },
    {
        "service_id": 657,
        "compatible": "faac",
        "label": "FAAC XT4 868 SLH LR",
        "meta_label": "FAAC XT4 868 SLH zamiennik",
        "name": "Pilot do bramy FAAC XT4 868 SLH LR – zamiennik",
        "slug": "pilot-faac-xt4-868-slh-lr-zamiennik",
        "sku": "PB-FAAC-XT4-868",
        "color": "czarny",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do systemu", "FAAC XT4 868 SLH LR"),
            ("Częstotliwość", "868,35 MHz"),
            ("Typ kodu", "zmienny SLH"),
            ("Liczba kanałów", "4"),
            ("Kolor", "czarny"),
        ],
        "battery": None,
        "sources": "faac_xt4",
        "short": "Zamiennik pilota FAAC XT4 868 SLH LR: 4 kanały, 868,35 MHz, kod SLH. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot FAAC XT4 868 SLH LR (zamiennik) za {price} zł. Sprawdź zgodność z odbiornikiem FAAC 868 i jak dodać pilota. Wysyłka lub kodowanie w Rybnej.",
        "intro": (
            "Pilot FAAC XT4 868 SLH LR w wersji zamiennika to czarny, czterokanałowy "
            "nadajnik do bram wjazdowych i garażowych z automatyką FAAC. Oryginalny XT4 "
            "868 SLH LR pracuje według deklaracji producenta na częstotliwości 868,35 MHz "
            "i nadaje kod zmienny SLH, a skrót LR oznacza wersję o zwiększonym zasięgu. "
            "Ten egzemplarz to pilot nieoryginalny, tańszy od nadajnika FAAC, "
            "przeznaczony do instalacji pracujących w tym systemie."
        ),
        "compat": (
            "Oryginalne piloty XT4 868 SLH LR współpracują z odbiornikami FAAC "
            "obsługującymi kod SLH w paśmie 868 MHz – sprzedawcy wymieniają m.in. "
            "odbiorniki RP 868, XR2 868 C i XF 868. Zamiennik jest przeznaczony do takich "
            "samych instalacji. Nie zadziała w bramie, której odbiornik pracuje na 433 MHz, "
            "bo to inne pasmo. Jeśli nie wiesz, jaki odbiornik masz w skrzynce "
            "sterownika, przyślij zdjęcie jego naklejki – pomogę to ustalić."
        ),
        "recognize": (
            "Oryginalny XT4 868 SLH LR ma płaską, prostokątną obudowę z czterema "
            "przyciskami rozmieszczonymi na okręgu i logo FAAC. Na tylnej ściance lub pod "
            "klapką baterii jest nazwa modelu i częstotliwość 868. Oznaczenie SLH mówi, "
            "że to kod zmienny. Na odbiorniku albo na karcie radiowej w centrali szukaj "
            "napisu 868 – jeśli widzisz 433, potrzebny jest inny pilot."
        ),
        "prog_intro": (
            "Zamiennik FAAC XT4 868 SLH LR trzeba zapisać w odbiorniku FAAC pracującym "
            "na 868 MHz z kodem SLH."
        ),
        "replace_answer": (
            "Tak, jeśli Twój obecny pilot to FAAC XT2 lub XT4 868 SLH (także w wersji LR), "
            "a odbiornik pracuje na 868 MHz z kodem SLH. Nie zastąpi pilotów FAAC na "
            "433 MHz ani z kodem stałym. W razie wątpliwości wyślij zdjęcie starego pilota "
            f"lub zadzwoń: {PHONE}."
        ),
    },
    {
        "service_id": 655,
        "compatible": "nice",
        "label": "Nice Flor-S",
        "meta_label": "Nice Flor-S zamiennik",
        "name": "Pilot do bramy Nice Flor-S – zamiennik 433,92 MHz",
        "slug": "pilot-nice-flor-s-zamiennik",
        "sku": "PB-NICE-FLOR-005",
        "color": "czarny z niebieskimi przyciskami",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do systemu", "Nice Flor (Flor-S)"),
            ("Częstotliwość", "433,92 MHz"),
            ("Typ kodu", "zmienny Flor"),
            ("Liczba przycisków", "4"),
            ("Kolor", "czarny, niebieskie przyciski"),
        ],
        "battery": None,
        "sources": "nice_flor",
        "short": "Zamiennik pilota Nice Flor-S: 4 przyciski, 433,92 MHz, kod zmienny Flor. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot Nice Flor-S (zamiennik) 433,92 MHz za {price} zł. Sprawdź, czy masz system Flor, a nie Smilo, i jak dodać pilota. Wysyłka lub kodowanie w Rybnej.",
        "intro": (
            "Pilot Nice Flor-S w wersji zamiennika to czarny nadajnik z czterema "
            "niebieskimi przyciskami i półprzezroczystą końcówką, przeznaczony do bram "
            "wjazdowych i garażowych z automatyką Nice pracującą w systemie Flor. "
            "Oryginalne piloty Flor-S nadają na częstotliwości 433,92 MHz kod zmienny Flor. "
            "Ten egzemplarz to pilot nieoryginalny, tańszy od nadajnika Nice – sprawdzi się "
            "jako dodatkowy pilot albo następca zgubionego."
        ),
        "compat": (
            "Oryginalne piloty Flor-S współpracują według sprzedawców z odbiornikami Nice "
            "systemu Flor, m.in. FLOX2R i FLOXI2R, a także z odbiornikami SMXI, OX2 czy "
            "OXIBD. Zamiennik jest przeznaczony do takich instalacji. Uwaga: system Flor "
            "to nie to samo co Nice Smilo – piloty obu systemów nie są zamienne. Jeśli "
            "Twój obecny pilot jest okrągły, z otworem na palec, to prawdopodobnie Smilo "
            "i potrzebujesz innego zamiennika."
        ),
        "recognize": (
            "Oryginalny Nice Flor-S ma wydłużoną obudowę z przyciskami ułożonymi w kwadrat "
            "i logo Nice. Nazwa modelu, np. FLO2R-S lub FLO4R-S, znajduje się zwykle na "
            "tylnej ściance lub pod klapką baterii. Na odbiorniku albo centrali szukaj "
            "oznaczeń zaczynających się od FLOX lub OX. Częstotliwość 433,92 MHz bywa "
            "podana na tabliczce znamionowej odbiornika."
        ),
        "prog_intro": (
            "Zamiennik Nice Flor-S trzeba zapisać w pamięci odbiornika systemu Flor."
        ),
        "replace_answer": (
            "Tak, jeśli Twój obecny pilot to Nice Flor-S (FLO2R-S, FLO4R-S) albo inny pilot "
            "systemu Flor na 433,92 MHz. Nie zastąpi pilota Nice Smilo ani pilotów innych "
            "marek. W razie wątpliwości wyślij zdjęcie starego pilota lub zadzwoń: "
            f"{PHONE}."
        ),
    },
    {
        "service_id": 652,
        "compatible": "nice",
        "label": "Nice Smilo",
        "meta_label": "Nice Smilo zamiennik",
        "name": "Pilot do bramy Nice Smilo – zamiennik 433,92 MHz",
        "slug": "pilot-nice-smilo-zamiennik",
        "sku": "PB-NICE-SMILO-002",
        "color": "czarny",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do systemu", "Nice Smilo"),
            ("Częstotliwość", "433,92 MHz"),
            ("Typ kodu", "zmienny"),
            ("Liczba przycisków", "4"),
            ("Kolor", "czarny"),
        ],
        "battery": None,
        "sources": "nice_smilo",
        "short": "Zamiennik pilota Nice Smilo: okrągła obudowa, 4 przyciski, 433,92 MHz. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot Nice Smilo (zamiennik) 433,92 MHz z 4 przyciskami za {price} zł. Sprawdź zgodność z odbiornikiem i jak dodać pilota. Wysyłka lub odbiór w Rybnej.",
        "intro": (
            "Pilot Nice Smilo w wersji zamiennika ma charakterystyczną, okrągłą obudowę "
            "z czterema przyciskami i dużym otworem na palec lub kółko do kluczy. Jest "
            "przeznaczony do bram wjazdowych i garażowych z automatyką Nice pracującą "
            "w systemie Smilo, który działa na częstotliwości 433,92 MHz z kodem zmiennym. "
            "To pilot nieoryginalny, tańszy od nadajnika Nice, przydatny jako kolejny "
            "pilot w domu albo zastępstwo za zgubiony."
        ),
        "compat": (
            "System Nice Smilo obejmuje piloty dwu- i czterokanałowe (SM2, SM4) oraz "
            "odbiorniki tej serii, np. uniwersalny SMX2 i wtykowy SMXIS. Zamiennik jest "
            "przeznaczony do instalacji, w których działają oryginalne piloty Smilo. "
            "Pamiętaj, że Smilo i Nice Flor to różne systemy – pilot jednego nie zadziała "
            "z odbiornikiem drugiego, choć oba pochodzą od Nice. Jeśli nie wiesz, który "
            "masz, wyślij zdjęcie starego pilota."
        ),
        "recognize": (
            "Pilot Smilo łatwo rozpoznać po okrągłym kształcie z wycięciem na palec – "
            "to wygląd niespotykany w innych seriach Nice. Na tylnej ściance oryginału "
            "znajdziesz oznaczenie SM2 lub SM4 i logo Nice. Na odbiorniku albo w centrali "
            "szukaj oznaczeń zaczynających się od SMX. Częstotliwość 433,92 MHz bywa "
            "nadrukowana na tabliczce znamionowej odbiornika."
        ),
        "prog_intro": (
            "Zamiennik Nice Smilo trzeba zapisać w pamięci odbiornika systemu Smilo."
        ),
        "replace_answer": (
            "Tak, jeśli Twój obecny pilot to Nice Smilo (SM2 lub SM4), a odbiornik pracuje "
            "w systemie Smilo na 433,92 MHz. Nie zastąpi pilota Nice Flor ani pilotów "
            f"innych marek. W razie wątpliwości wyślij zdjęcie lub zadzwoń: {PHONE}."
        ),
    },
    {
        "service_id": 661,
        "compatible": "somfy",
        "label": "Somfy",
        "meta_label": "Somfy zamiennik",
        "name": "Pilot do bramy Somfy – zamiennik",
        "slug": "pilot-somfy-zamiennik",
        "sku": "PB-SOMFY-001",
        "color": "czarny",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do", "napędów Somfy"),
            ("Liczba przycisków", "2"),
            ("Kolor", "czarny"),
        ],
        "battery": None,
        "sources": None,
        "short": "Zamiennik pilota do napędów Somfy, czarny, z dwoma przyciskami. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot do bram Somfy (zamiennik) z 2 przyciskami za {price} zł. Sprawdź, czy masz system RTS czy io, i jak dodać pilota. Wysyłka lub kodowanie w Rybnej.",
        "intro": (
            "Pilot Somfy w wersji zamiennika to czarny nadajnik z dwoma przyciskami "
            "w okrągłym zagłębieniu i otworem na kółko do kluczy. Jest przeznaczony do "
            "bram wjazdowych i garażowych z napędami Somfy. To pilot nieoryginalny, bez "
            "logo producenta, tańszy od nadajnika Somfy. Zanim go zamówisz, ustal, w jakim "
            "systemie radiowym pracuje Twój napęd – od tego zależy, czy pilot zostanie "
            "przyjęty przez odbiornik."
        ),
        "compat": (
            "Somfy stosuje w automatyce dwa różne systemy radiowe: RTS oraz "
            "io-homecontrol. Piloty jednego systemu nie współpracują z odbiornikami "
            "drugiego, więc sama marka napędu nie wystarczy. System, do którego "
            "przeznaczony jest ten zamiennik, potwierdzę na podstawie Twojego obecnego "
            "pilota albo naklejki z napędu. Wyślij mi zdjęcie, a sprawdzę zgodność przed "
            "zakupem – to oszczędzi Ci zwrotu."
        ),
        "recognize": (
            "Oryginalne piloty Somfy mają logo producenta na obudowie, a na tylnej ściance "
            "nazwę modelu i oznaczenie systemu – RTS albo io. To samo oznaczenie zwykle "
            "widnieje na naklejce znamionowej napędu lub odbiornika. Jeśli na Twoim "
            "starym pilocie lub napędzie jest napis io, a nie RTS, koniecznie zaznacz to "
            "przy kontakcie ze mną. Sam kształt obudowy nie wystarczy do rozpoznania systemu."
        ),
        "prog_intro": "Zamiennik Somfy trzeba zapisać w pamięci odbiornika Twojej bramy.",
        "replace_answer": (
            "To zależy od systemu radiowego Twojego napędu – Somfy ma systemy RTS "
            "i io-homecontrol, które nie są zamienne. System tego zamiennika muszę "
            "potwierdzić. Wyślij zdjęcie starego pilota lub naklejki z napędu albo "
            f"zadzwoń: {PHONE}."
        ),
    },
    {
        "service_id": 663,
        "compatible": "hormann",
        "label": "Hörmann 2-kanałowy",
        "meta_label": "Hörmann 2-kanałowy zamiennik",
        "name": "Pilot do bramy Hörmann 2-kanałowy – zamiennik",
        "slug": "pilot-hormann-2-kanalowy-zamiennik",
        "sku": "PB-HORMANN-001",
        "color": "szary",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do", "napędów Hörmann"),
            ("Liczba przycisków", "2"),
            ("Kolor", "szary"),
        ],
        "battery": None,
        "sources": "hormann_bisecur",
        "short": "Zamiennik pilota do napędów Hörmann: szara obudowa, 2 przyciski. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot do bram Hörmann, zamiennik 2-kanałowy, za {price} zł. Sprawdź, czy masz system 868 MHz czy BiSecur, i jak dodać pilota. Wysyłka lub odbiór w Rybnej.",
        "intro": (
            "Pilot Hörmann 2-kanałowy w wersji zamiennika to wąski, szary nadajnik z dwoma "
            "przyciskami i kółkiem do kluczy. Jest przeznaczony do bram garażowych "
            "i wjazdowych z napędami Hörmann. To pilot nieoryginalny, bez logo producenta, "
            "tańszy od nadajnika Hörmann. Hörmann przez lata stosował kilka systemów "
            "radiowych, dlatego przed zamówieniem trzeba ustalić, który pracuje w Twojej "
            "bramie."
        ),
        "compat": (
            "Napędy Hörmann korzystają z różnych systemów: starszego 40 MHz, 868 MHz "
            "z kodem stałym oraz nowszego BiSecur na 868 MHz z szyfrowaniem. Nie są one "
            "wzajemnie zamienne – np. piloty BiSecur według instrukcji Hörmann nie działają "
            "z systemami 40 MHz. System, do którego przeznaczony jest ten zamiennik, "
            "potwierdzę na podstawie Twojego obecnego pilota albo naklejki z napędu. "
            "Przyślij zdjęcie, a sprawdzę zgodność przed zakupem."
        ),
        "recognize": (
            "Oryginalne piloty Hörmann mają logo na obudowie, a na tylnej ściance "
            "oznaczenie modelu, np. HSM2, HSE2 albo HSE 4 BS, i częstotliwość. Według "
            "Hörmann starszy system 868 MHz z kodem stałym poznasz m.in. po szarych "
            "pilotach z niebieskimi przyciskami. Piloty BiSecur mają w nazwie BS. "
            "Model napędu, np. ProMatic lub SupraMatic, odczytasz z naklejki na napędzie."
        ),
        "prog_intro": (
            "Zamiennik Hörmann 2-kanałowy trzeba zapisać w pamięci odbiornika lub napędu."
        ),
        "replace_answer": (
            "To zależy od systemu Twojej bramy – Hörmann ma systemy 40 MHz, 868 MHz "
            "z kodem stałym i BiSecur, które nie są wzajemnie zamienne. System tego "
            "zamiennika muszę potwierdzić. Wyślij zdjęcie starego pilota lub zadzwoń: "
            f"{PHONE}."
        ),
    },
    {
        "service_id": 664,
        "compatible": "hormann",
        "label": "Hörmann 4-kanałowy",
        "meta_label": "Hörmann 4-kanałowy zamiennik",
        "name": "Pilot do bramy Hörmann 4-kanałowy – zamiennik",
        "slug": "pilot-hormann-4-kanalowy-zamiennik",
        "sku": "PB-HORMANN-006",
        "color": "czarny z niebieskimi przyciskami",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do", "napędów Hörmann"),
            ("Liczba przycisków", "4"),
            ("Kolor", "czarny, niebieskie przyciski"),
        ],
        "battery": None,
        "sources": "hormann_bisecur",
        "short": "Zamiennik pilota do napędów Hörmann: 4 niebieskie przyciski w układzie krzyża. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot do bram Hörmann, zamiennik 4-kanałowy, za {price} zł. Sprawdź system swojej bramy i jak dodać pilota. Wysyłka, odbiór lub kodowanie w Rybnej.",
        "intro": (
            "Pilot Hörmann 4-kanałowy w wersji zamiennika ma czarną obudowę i cztery "
            "niebieskie przyciski ułożone w krzyż. Cztery kanały pozwalają sterować np. "
            "bramą wjazdową, garażową i dodatkowymi urządzeniami z jednego pilota, jeśli "
            "instalacja to obsługuje. Jest przeznaczony do napędów Hörmann. To pilot "
            "nieoryginalny, bez logo producenta, tańszy od nadajnika Hörmann. Przed "
            "zamówieniem ustal, w jakim systemie pracuje Twoja brama."
        ),
        "compat": (
            "Hörmann stosował kilka systemów radiowych: 40 MHz, 868 MHz z kodem stałym "
            "i BiSecur na 868 MHz. Systemy te nie są zamienne, a nowoczesne napędy "
            "z odbiornikiem BiSecur przyjmują piloty BiSecur. System, do którego "
            "przeznaczony jest ten zamiennik, potwierdzę na podstawie Twojego obecnego "
            "pilota albo naklejki z napędu. Wyślij zdjęcie – sprawdzę zgodność, zanim "
            "zamówisz."
        ),
        "recognize": (
            "Oryginalne czterokanałowe piloty Hörmann, np. HSM4 lub HSE 4 BS, mają logo "
            "producenta i oznaczenie modelu na tylnej ściance. Według Hörmann starszy "
            "system 868 MHz z kodem stałym rozpoznasz m.in. po pilotach z niebieskimi "
            "przyciskami, a piloty BiSecur mają w nazwie BS. Model napędu odczytasz "
            "z naklejki znamionowej na napędzie garażowym lub na centrali."
        ),
        "prog_intro": (
            "Zamiennik Hörmann 4-kanałowy trzeba zapisać w pamięci odbiornika lub napędu, "
            "osobno dla każdego przycisku, którego chcesz używać."
        ),
        "replace_answer": (
            "To zależy od systemu Twojej bramy – Hörmann ma systemy 40 MHz, 868 MHz "
            "z kodem stałym i BiSecur, które nie są wzajemnie zamienne. System tego "
            "zamiennika muszę potwierdzić. Wyślij zdjęcie starego pilota lub zadzwoń: "
            f"{PHONE}."
        ),
    },
    {
        "service_id": 662,
        "compatible": "hormann",
        "label": "Hörmann HSE 4 BiSecur",
        "meta_label": "Hörmann HSE 4 BiSecur zamiennik",
        "name": "Pilot do bramy Hörmann HSE 4 BiSecur – zamiennik 868 MHz",
        "slug": "pilot-hormann-hse-4-bisecur-zamiennik",
        "sku": "PB-HORMANN-HSE4-BS",
        "color": "czarny",
        "specs": [
            ("Rodzaj", "zamiennik (pilot nieoryginalny)"),
            ("Przeznaczony do systemu", "Hörmann BiSecur"),
            ("Częstotliwość", "868 MHz"),
            ("Typ kodu", "BiSecur (szyfrowany)"),
            ("Liczba przycisków", "4"),
            ("Kolor", "czarny"),
        ],
        "battery": None,
        "sources": "hormann_bisecur",
        "short": "Zamiennik pilota Hörmann HSE 4 BiSecur: 4 przyciski, 868 MHz, system BiSecur. Cena {price} zł, wysyłka lub odbiór w Rybnej.",
        "meta_description": "Pilot Hörmann HSE 4 BiSecur (zamiennik) 868 MHz za {price} zł. Sprawdź zgodność z napędem BiSecur i jak dodać pilota. Wysyłka lub kodowanie w Rybnej.",
        "intro": (
            "Pilot Hörmann HSE 4 BiSecur w wersji zamiennika to czarny, czteroprzyciskowy "
            "nadajnik do bram garażowych i wjazdowych z napędami Hörmann pracującymi "
            "w systemie BiSecur. Oryginalny HSE 4 BS działa na częstotliwości 868 MHz "
            "i według producenta korzysta z szyfrowania 128-bitowego. Ten egzemplarz to "
            "pilot nieoryginalny, tańszy od nadajnika Hörmann, przeznaczony do instalacji "
            "z odbiornikiem BiSecur."
        ),
        "compat": (
            "Oryginalne piloty BiSecur współpracują według Hörmann z napędami "
            "wyposażonymi w odbiornik BiSecur 868 MHz, m.in. z serii ProMatic, SupraMatic, "
            "RotaMatic, VersaMatic i LineaMatic. Instrukcja producenta zaznacza, że "
            "piloty te nie działają z systemami 40 MHz ani 433 MHz. Zamiennik jest "
            "przeznaczony do napędów z odbiornikiem BiSecur. Jeśli Twój napęd jest starszy, "
            "przyślij zdjęcie naklejki – sprawdzę, czy ten pilot będzie pasował."
        ),
        "recognize": (
            "Oryginalny HSE 4 BS ma wydłużoną, czarną obudowę z czterema przyciskami "
            "wokół środka i logo Hörmann. Skrót BS w nazwie oznacza BiSecur. Na naklejce "
            "znamionowej napędu sprawdź model i informację o odbiorniku – nowsze napędy "
            "Hörmann z BiSecur mają to oznaczenie na tabliczce lub w instrukcji. Starsze "
            "piloty 868 MHz bez BiSecur to inny system."
        ),
        "prog_intro": (
            "Zamiennik Hörmann HSE 4 BiSecur trzeba zapisać w napędzie lub odbiorniku "
            "z systemem BiSecur."
        ),
        "replace_answer": (
            "Tak, jeśli Twój obecny pilot to Hörmann z systemem BiSecur (np. HSE 2 BS, "
            "HSE 4 BS), a napęd ma odbiornik BiSecur 868 MHz. Nie zastąpi pilotów 40 MHz "
            "ani 433 MHz. Przy starszym systemie 868 MHz bez BiSecur najpierw wyślij "
            f"zdjęcie pilota lub zadzwoń: {PHONE}."
        ),
    },
]


# --- Budowanie treści ------------------------------------------------------------
def build_seo_text(remote, brand_name):
    specs = "".join(
        f"<li><strong>{name}:</strong> {value}</li>" for name, value in remote["specs"]
    )
    label = remote["label"]
    return (
        f"<p>{remote['intro']}</p>"
        f'<h2 class="mt-6 mb-2 text-xl font-semibold">Z jakimi napędami współpracuje {label}</h2>'
        f"<p>{remote['compat']}</p>"
        '<h2 class="mt-6 mb-2 text-xl font-semibold">Parametry</h2>'
        f'<ul class="list-disc pl-6">{specs}</ul>'
        '<h2 class="mt-6 mb-2 text-xl font-semibold">Jak sprawdzić, czy to Twój pilot</h2>'
        f"<p>{remote['recognize']}</p>"
        '<h2 class="mt-6 mb-2 text-xl font-semibold">Programowanie pilota</h2>'
        f"<p>{remote['prog_intro']} Dokładną kolejność czynności opisuje instrukcja "
        "Twojego napędu lub odbiornika – możesz zrobić to samodzielnie, korzystając "
        "z odpowiedzi w pytaniach poniżej. Możesz też przyjechać do punktu przy "
        f"{ADDRESS} ({HOURS}) albo wybrać wygodniejszą opcję: "
        f"{link(f'zaprogramuję pilota {brand_name} u Ciebie na miejscu')}.</p>"
    )


def build_faqs(remote, price):
    label = remote["label"]
    faqs = [
        (
            f"Jak dodać pilot {label} do odbiornika bramy?",
            f"Pilot {label} trzeba zapisać w pamięci odbiornika Twojej bramy. {SAFE_ANSWER}",
        ),
        (
            f"Jak skopiować pilot {label} z pilota na pilota?",
            "Dla tego zamiennika nie mam potwierdzonej procedury dodawania z działającego "
            "pilota, dlatego jej nie podaję – błędna sekwencja przycisków może niczego "
            f"nie zapisać. Pewniejsze jest dodanie pilota przy odbiorniku. {SAFE_ANSWER}",
        ),
        (f"Czy pilot {label} zastąpi mój stary pilot?", remote["replace_answer"]),
    ]
    if remote.get("battery"):
        faqs.append(
            (
                f"Jaka bateria jest w pilocie {label} i jak ją wymienić?",
                f"Pilot zasila bateria {remote['battery']}. Wymienisz ją po otwarciu "
                "obudowy lub klapki baterii – zwróć uwagę na biegunowość. Jeśli wolisz, "
                f"wymienię ją od ręki w punkcie przy {ADDRESS}.",
            )
        )
    faqs += [
        (
            f"Co zrobić, gdy pilot {label} przestał działać albo go zgubiłem?",
            "Gdy pilot przestał działać, najpierw wymień baterię i sprawdź, czy brama "
            "reaguje na inne piloty. Zgubiony pilot warto usunąć z pamięci odbiornika, "
            "żeby nikt nie otworzył nim bramy – w wielu odbiornikach oznacza to "
            "wyczyszczenie całej pamięci i ponowne dodanie pozostałych pilotów. Mogę to "
            f"zrobić u Ciebie: {link('pilot do bramy z dojazdem i programowaniem')}.",
        ),
        (
            f"Czy cena {price} zł obejmuje zaprogramowanie pilota {label}?",
            f"Nie, {price} zł to cena samego pilota. Zaprogramujesz go samodzielnie "
            f"według instrukcji napędu, w punkcie przy {ADDRESS} ({HOURS}) albo "
            "w ramach usługi z dojazdem. Pilota wyślę w 1–3 dni robocze lub odbierzesz "
            "go osobiście w Rybnej.",
        ),
    ]
    return faqs
