"""Dane i treści dla komendy przebuduj_klucze_samochodowe (2026-11-20).

Zmiana profilu: najważniejsze są klucze samochodowe, immobilizery i piloty
samochodowe (+ nowa usługa: awaryjne otwieranie samochodów), pieczątki na końcu.

Ceny – wyłącznie z tabeli właściciela:
  * klucz z grotem + immobilizer (kopia/dorobienie): 300 zł
  * programowanie klucza/pilota przez OBD: od 300 zł + koszt pilota/klucza
    (np. od ok. 150 zł), razem zwykle od ok. 450 zł
  * awaryjne otwieranie: brak ceny – wycena telefoniczna
Brak stałych godzin otwarcia – wizyty po umówieniu.
"""

PHONE_HTML = '<a href="tel:+48506029980" class="font-semibold underline">506 029 980</a>'

CAR_KEYS = "/uslugi/klucze-samochodowe"
PROGRAMMING = f"{CAR_KEYS}/programowanie-kluczy-samochodowych"
COPYING = f"{CAR_KEYS}/kopiowanie-immobilizerow"
EMERGENCY = f"{CAR_KEYS}/awaryjne-otwieranie-samochodow"
MOBILE_KEYS = "/uslugi/mobilne-dorabianie-kluczy"
LOST_KEY_ARTICLE = "/blog/zgubiony-kluczyk-do-auta-dorobienie-klucza-bez-oryginalu-z-dojazdem-id-10"


def brand_path(slug):
    return f"{PROGRAMMING}/programowanie-kluczy-i-pilotow-samochodowych-{slug}"


def a(href, text):
    return f'<a href="{href}" class="underline">{text}</a>'


PRICE_SENTENCE = (
    "Klucz z grotem i immobilizerem kosztuje 300 zł. Programowanie nowego klucza "
    "lub pilota przez złącze OBD to od 300 zł plus koszt pilota lub klucza "
    "(np. od ok. 150 zł), czyli razem zwykle od ok. 450 zł."
)

VAG_LINKS = (
    f"{a(brand_path('audi'), 'Audi')}, {a(brand_path('volkswagen'), 'Volkswagen')} "
    f"i {a(brand_path('seat'), 'Seat')}"
)

APPOINTMENT_ANSWER = (
    "Nie mam stałych godzin otwarcia. Proszę o umówienie wizyty telefonicznie "
    "(506 029 980), przez WhatsApp lub e-mailem, ponieważ wykonuję zlecenia "
    "z dojazdem do klienta. Wizytę w punkcie w Rybnej (ul. Wspólna 2) również "
    "trzeba wcześniej umówić. Sklep internetowy działa 24 h."
)

# --- Obszar działania (Etap 5) – ta sama lista jest we froncie (serviceArea.ts) ----
AREA_KRAKOW = [
    "Stare Miasto", "Krowodrza", "Bronowice", "Azory", "Prądnik Biały",
    "Prądnik Czerwony", "Zwierzyniec", "Dębniki", "Ruczaj", "Łagiewniki",
    "Borek Fałęcki", "Podgórze", "Wola Duchacka", "Bieżanów", "Prokocim",
    "Czyżyny", "Mistrzejowice", "Bieńczyce", "Nowa Huta",
]
AREA_AROUND = [
    "Zabierzów", "Balice", "Rząska", "Liszki", "Mników", "Piekary", "Czernichów",
    "Krzeszowice", "Alwernia", "Jerzmanowice", "Wielka Wieś", "Zielonki",
    "Michałowice", "Skawina", "Wieliczka", "Niepołomice", "Mogilany",
    "Świątniki Górne", "Trzebinia",
]
AREA_RYBNA = [
    "Rybna", "Czułówek", "Kamień", "Przeginia Narodowa", "Przeginia Duchowna",
    "Wołowice", "Rusocice", "Sanka",
]

# --- Dokładne podmiany w istniejących treściach -----------------------------------
# (model, slug albo None = każdy obiekt z tym tekstem, pole, stary tekst, nowy tekst)
REPLACEMENTS = [
    # 17 stron marek: błędne ceny 180/150 zł
    (
        "category", None, "seo_text",
        "Orientacyjnie: dorobienie klucza z immobilizerem od 180 zł, kopiowanie immobilizera od 150 zł.",
        PRICE_SENTENCE,
    ),
    # kategoria programowania + artykuł 10
    (
        "category", "programowanie-kluczy-samochodowych", "seo_text",
        "Orientacyjnie: klucz z immobilizerem od 180 zł, kopiowanie immobilizera od 150 zł.",
        PRICE_SENTENCE,
    ),
    (
        "article", "zgubiony-kluczyk-do-auta-dorobienie-klucza-bez-oryginalu-z-dojazdem-id-10", "content",
        "Orientacyjnie: klucz z immobilizerem od 180 zł, kopiowanie immobilizera od 150 zł.",
        PRICE_SENTENCE,
    ),
    # programowanie: VAG po 2016 – nowe urządzenie
    (
        "category", "programowanie-kluczy-samochodowych", "seo_text",
        '<h3 class="text-lg font-semibold mb-2">Volkswagen, Skoda, Audi, Seat, BMW i Volvo</h3>\n'
        '  <p class="mb-4">W tych markach programowanie nowszych roczników (mniej więcej od 2015 roku) '
        "wymaga często specjalistycznej pracy przy module auta. Jeśli masz jeden działający klucz, "
        'zwykle mogę wykonać <a href="/uslugi/klucze-samochodowe/kopiowanie-immobilizerow" '
        'class="underline">kopię immobilizera</a> — także w nowszych modelach. Zadzwoń z numerem VIN, '
        "a powiem, co da się zrobić.</p>",
        '<h3 class="text-lg font-semibold mb-2">Audi, Volkswagen i Seat — także roczniki po 2016</h3>\n'
        '  <p class="mb-4">Mam nowe urządzenie do programowania kluczy i pilotów grupy VAG, więc '
        f"obsługuję także nowsze roczniki {VAG_LINKS}, które wcześniej wymagały wizyty w ASO. "
        "Możliwość wykonania potwierdzam przez telefon po modelu, roczniku i VIN.</p>\n"
        '  <h3 class="text-lg font-semibold mb-2">Skoda, BMW i Volvo</h3>\n'
        '  <p class="mb-4">W nowszych rocznikach tych marek, jeśli masz jeden działający klucz, zwykle '
        f"mogę wykonać {a(COPYING, 'kopię immobilizera')}. Zadzwoń z numerem VIN, a powiem, co da się "
        "zrobić.</p>",
    ),
    # kategoria kopiowania: cena i linki VAG
    (
        "category", "kopiowanie-immobilizerow", "seo_text",
        "Kopiowanie immobilizera od 150 zł.",
        "Klucz z grotem i kopią immobilizera kosztuje 300 zł.",
    ),
    (
        "category", "kopiowanie-immobilizerow", "seo_text",
        "Kopiowanie wykonuję też w autach grupy VAG (Volkswagen, Skoda, Audi, Seat), BMW i Volvo",
        "Kopiowanie wykonuję też w autach grupy VAG ("
        f"{a(brand_path('volkswagen'), 'Volkswagen')}, Skoda, {a(brand_path('audi'), 'Audi')}, "
        f"{a(brand_path('seat'), 'Seat')}), BMW i Volvo",
    ),
    # kategoria klucze-samochodowe: nowe marki + awaryjne otwieranie
    (
        "category", "klucze-samochodowe", "seo_text",
        'programowanie-kluczy-i-pilotow-samochodowych-chevrolet" class="underline">Chevrolet</a>.</li>',
        'programowanie-kluczy-i-pilotow-samochodowych-chevrolet" class="underline">Chevrolet</a>, '
        f"{VAG_LINKS} (VAG, także po 2016).</li>",
    ),
    (
        "category", "klucze-samochodowe", "seo_text",
        '    <li><a href="/uslugi/klucze-samochodowe/kopiowanie-immobilizerow" class="underline">',
        f'    <li><a href="{EMERGENCY}" class="underline"><strong>Awaryjne otwieranie samochodów</strong></a>'
        " — zatrzaśnięte kluczyki albo zgubiony klucz: otwieram auto bez uszkodzeń narzędziami Lishi "
        "i na miejscu dorabiam nowy klucz.</li>\n"
        '    <li><a href="/uslugi/klucze-samochodowe/kopiowanie-immobilizerow" class="underline">',
    ),
    (
        "category", "klucze-samochodowe", "description",
        "Dorabiam i programuję klucze samochodowe, kopiuję immobilizery, wymieniam obudowy i baterie w pilotach. "
        "W punkcie w Rybnej albo z dojazdem do klienta w Krakowie i okolicach.",
        "Dorabiam i programuję klucze samochodowe, kopiuję immobilizery, awaryjnie otwieram auta, wymieniam "
        "obudowy i baterie w pilotach. Z dojazdem do klienta w Krakowie i okolicach albo w punkcie w Rybnej "
        "po umówieniu.",
    ),
    # pozycje cennika na /uslugi/mobilne-dorabianie-kluczy
    (
        "product", "klucze-samochodowe-id-643", "description",
        "Z immobilizerem, dorobione i skonfigurowane na miejscu.",
        "Wymiana obudowy kluczyka/pilota (bez programowania).",
    ),
    (
        "product", "klucze-samochodowe-id-643", "meta_title",
        "Klucze samochodowe z dojazdem — od 180 zł | Kraków",
        "Wymiana obudowy kluczyka z dojazdem | Kraków",
    ),
    (
        "product", "klucze-samochodowe-id-643", "meta_description",
        "Dorabiamy i programujemy klucze samochodowe z immobilizerem, z dojazdem do klienta w Krakowie i okolicy. Cena od 180 zł.",
        "Wymiana obudowy kluczyka lub pilota samochodowego (bez programowania) z dojazdem do klienta w Krakowie i okolicy.",
    ),
    (
        "product", "immobilizery-i-piloty-id-644", "meta_description",
        "Dorabiamy i programujemy zdalniki oraz immobilizery samochodowe z dojazdem do klienta w Krakowie i okolicy. Cena od 150 zł.",
        "Programowanie pilotów i immobilizerów z dojazdem w Krakowie i okolicy: od 300 zł + koszt pilota przy programowaniu przez OBD.",
    ),
    (
        "product", "immobilizery-i-piloty-id-644", "description",
        "Dorobienie i programowanie pilotów do samochodu. Kopiowanie immobilizerów",
        "Dorobienie i programowanie pilotów do samochodu, kopiowanie immobilizerów. "
        "Przy programowaniu przez OBD doliczam koszt pilota.",
    ),
]

# Ceny pozycji usługowych ujednolicane do tabeli właściciela (slug -> cena brutto).
PRODUCT_PRICES = {
    "kopiowanie-immobilizerow-id-620": "300.00",
}

# Pola nadpisywane w całości (slug kategorii -> pola).
CATEGORY_FIELDS = {
    "mobilne-dorabianie-kluczy": {
        "h1_tag": "Dorabianie kluczy samochodowych i mieszkaniowych z dojazdem — Kraków i okolice",
        "meta_title": "Dorabianie kluczy samochodowych z dojazdem – Kraków",
        "meta_description": (
            "Dorabianie kluczy samochodowych z immobilizerem, programowanie pilotów i klucze "
            "mieszkaniowe z dojazdem do klienta w Krakowie i okolicy. Płacisz po sprawdzeniu."
        ),
        "description": (
            "Klucze samochodowe z immobilizerem, programowanie pilotów oraz klucze mieszkaniowe — "
            "przyjeżdżam pod wskazany adres w Krakowie i okolicy i wykonuję usługę na miejscu."
        ),
        "seo_text": (
            "Dorabiam klucze samochodowe, programuję immobilizery i piloty oraz dorabiam klucze "
            "mieszkaniowe z dojazdem do klienta w całym Krakowie i okolicznych miejscowościach — "
            "bez konieczności przyjazdu do punktu w Rybnej."
        ),
    },
}

# Kolejność „Kategorii promowanych” i menu (pole Category.order).
# Promowane: Klucze samochodowe → Usługi → Kodowanie pilotów do bram → Piloty do bram →
# Naprawy telefonów → Klucze (sklep) → Pieczątki. Pozostałe zmiany porządkują rodzeństwo,
# żeby pieczątki i klucze mieszkaniowe nie wyprzedzały kluczy samochodowych w menu.
CATEGORY_ORDER = {
    "klucze-samochodowe": 1,
    "uslugi": 2,
    "mobilne-kodowanie-pilotow-do-bram": 3,
    "piloty-do-bram": 4,
    "naprawy-telefonow": 5,
    "dorabianie-kluczy-mieszkaniowych": 6,
    "klucze": 6,
    "pieczatki": 7,
    "mobilne-wyrob-pieczatek": 8,
    # w drzewie kluczy samochodowych: awaryjne otwieranie zaraz po programowaniu
    "programowanie-kluczy-samochodowych": 1,
    "kopiowanie-immobilizerow": 2,
    "awaryjne-otwieranie-samochodow": 3,
    "wymiana-obudowy": 4,
    "wymiana-baterii-w-pilotach-samochodowych": 5,
}

# Banery (Hero): klucze przed pieczątkami. Front i tak przenosi baner pieczątek na dół strony.
HERO_ORDER_BY_LINK = {
    "https://serwiswrybnej.pl/produkty/klucze": 1,
    "https://serwiswrybnej.pl/produkty/pieczatki": 2,
}


# --- Nowe kategorie ------------------------------------------------------------------
def _area_short():
    return (
        "Kraków — wszystkie dzielnice, m.in. Krowodrza, Bronowice, Prądnik Biały, Podgórze, "
        "Dębniki, Ruczaj i Nowa Huta — oraz okolice: Zabierzów, Balice, Liszki, Czernichów, "
        "Krzeszowice, Skawina, Wieliczka, Zielonki, Michałowice i Niepołomice, a także okolice "
        "Rybnej."
    )


EMERGENCY_SEO = f"""<section class="w-full mx-auto">
  <h2 class="text-xl font-bold mb-4">Zatrzaśnięte kluczyki, zgubiony klucz, zacięty zamek?</h2>
  <p class="mb-4">Kluczyki zostały w środku, a drzwi się zablokowały? Zgubiłeś jedyny klucz do auta albo zamek przestał reagować na klucz? Takie sytuacje zdarzają się zwykle w najgorszym momencie — pod sklepem, na parkingu przy pracy albo przed wyjazdem. Przyjeżdżam z dojazdem pod wskazany adres w Krakowie i okolicach i otwieram samochód bez wybijania szyby i bez uszkadzania zamka. Nie potrzebujesz lawety ani wizyty w ASO.</p>
  <h3 class="text-lg font-semibold mb-2">Najczęstsze sytuacje, w których dzwonisz</h3>
  <ul class="list-disc list-inside mb-4">
    <li>kluczyki zostały na siedzeniu lub w bagażniku, a auto się zamknęło,</li>
    <li>jedyny klucz zginął na spacerze, w sklepie albo w drodze z pracy,</li>
    <li>pilot nie otwiera centralnego zamka, a kluczykiem mechanicznym nie da się otworzyć drzwi,</li>
    <li>kupiłeś używane auto bez zapasowego klucza i jedyny egzemplarz właśnie przepadł.</li>
  </ul>
  <h2 class="text-xl font-bold mb-4">Jak otwieram samochód: narzędzia Lishi</h2>
  <p class="mb-4">Pracuję narzędziami Lishi (2w1: otwieracz i dekoder). Narzędzie wchodzi do wkładki zamka jak klucz i pozwala otworzyć zamek bez niszczenia go. Jednocześnie odczytuje układ nacięć wkładki, czyli „dekoduje” zamek. Dzięki temu po otwarciu auta mogę od razu dociąć nowy grot klucza dokładnie pod Twój zamek, nawet gdy nie masz oryginału. Zamek i drzwi zostają nietknięte — nie wiercę, nie podważam drzwi i nie wybijam szyby. Narzędzie dobieram do konkretnego typu wkładki, dlatego pytam o markę, model i rocznik już przy pierwszym telefonie.</p>
  <p class="mb-4">Taka metoda jest wolniejsza niż „siłowe” otwarcie, ale bezpieczna dla auta: po mojej wizycie zamek działa tak samo jak wcześniej, a Ty nie płacisz za nową szybę, lakierowanie drzwi ani wymianę wkładki.</p>
  <h2 class="text-xl font-bold mb-4">Otwarcie auta i nowy klucz w jednej wizycie</h2>
  <p class="mb-4">Gdy klucz zginął, nie kończę na otwarciu drzwi. Dekoderem Lishi odczytuję nacięcia, docinam grot, a potem programuję immobilizer i pilota do auta. Klucz z grotem i immobilizerem kosztuje 300 zł, a programowanie przez złącze OBD — od 300 zł plus koszt pilota lub klucza (np. od ok. 150 zł). Wyjeżdżasz własnym autem, bez holowania do ASO. Więcej o tej sytuacji piszę w poradniku {a(LOST_KEY_ARTICLE, 'zgubiony kluczyk do auta — co zrobić')}.</p>
  <h2 class="text-xl font-bold mb-4">Jakie samochody otwieram</h2>
  <p class="mb-4">Otwieram większość popularnych marek, które obsługuję przy programowaniu kluczy: {a(brand_path('peugeot'), 'Peugeot')}, {a(brand_path('citroen'), 'Citroën')}, {a(brand_path('ford'), 'Ford')}, {a(brand_path('opel'), 'Opel')}, {a(brand_path('renault'), 'Renault')}, {a(brand_path('dacia'), 'Dacia')}, {a(brand_path('toyota'), 'Toyota')}, {a(brand_path('honda'), 'Honda')}, {a(brand_path('fiat'), 'Fiat')}, {a(brand_path('suzuki'), 'Suzuki')}, {a(brand_path('kia'), 'Kia')}, {a(brand_path('hyundai'), 'Hyundai')}, a także {VAG_LINKS}. Możliwość otwarcia konkretnego auta potwierdzam przez telefon po marce, modelu i roczniku — od tego zależy, jakim narzędziem pracuję.</p>
  <h2 class="text-xl font-bold mb-4">Bezpieczeństwo: tylko dla właściciela</h2>
  <p class="mb-4">Otwieram samochód wyłącznie osobie, która potwierdzi prawo do auta: dowodem rejestracyjnym (lub innym dokumentem pojazdu) i dowodem osobistym. Jeśli dokumenty są zamknięte w aucie, sprawdzam je zaraz po otwarciu, przed wydaniem auta lub dorobieniem klucza. Dzięki temu usługa jest bezpieczna także dla Ciebie — nikt postronny nie zleci mi otwarcia Twojego samochodu.</p>
  <h2 class="text-xl font-bold mb-4">Co zrobić, zanim przyjadę</h2>
  <p class="mb-4">Zadzwoń i podaj markę, model, rocznik oraz adres, pod którym stoi auto. Nie próbuj otwierać drzwi drutem, linijką ani podważać szyby — łatwo wtedy uszkodzić uszczelki, lakier, mechanizm zamka albo elektrykę w drzwiach, a naprawa kosztuje więcej niż samo otwarcie. Przygotuj dowód osobisty; jeśli dowód rejestracyjny masz przy sobie, też go weź. Jeśli w zamkniętym aucie zostało dziecko lub zwierzę, a na zewnątrz jest upał albo mróz, nie czekaj na mnie — dzwoń od razu na numer alarmowy 112.</p>
  <h2 class="text-xl font-bold mb-4">Ile to kosztuje i jak szybko dojadę</h2>
  <p class="mb-4">Cenę podaję przez telefon po marce, modelu, roczniku i miejscu, w którym stoi auto. Zadzwoń: {PHONE_HTML}. Przygotuj, jeśli możesz, numer rejestracyjny lub VIN — ułatwi to dobór narzędzia i skróci samą usługę na miejscu.</p>
  <h2 class="text-xl font-bold mb-4">Obszar działania</h2>
  <p class="mb-4">Dojeżdżam do klienta: {_area_short()} Pełną listę miejscowości znajdziesz na stronie {a(MOBILE_KEYS, 'dorabianie kluczy z dojazdem')}.</p>
</section>"""

EMERGENCY_FAQS = [
    (
        "Czy otwarcie auta uszkodzi zamek lub drzwi?",
        "Nie. Narzędzia Lishi otwierają zamek przez wkładkę, bez wybijania szyby i bez wiercenia. "
        "Zamek po otwarciu działa tak samo jak wcześniej.",
    ),
    (
        "Zgubiłem jedyny kluczyk. Czy po otwarciu zrobisz nowy?",
        "Tak. Dekoderem Lishi odczytuję nacięcia zamka, docinam grot i programuję immobilizer oraz "
        "pilota. Klucz z grotem i immobilizerem kosztuje 300 zł, a programowanie przez OBD od 300 zł "
        "plus koszt pilota lub klucza (np. od ok. 150 zł).",
    ),
    (
        "Jakich dokumentów potrzebujesz?",
        "Dowodu rejestracyjnego (lub innego dokumentu pojazdu) i dowodu osobistego. Jeśli dokumenty "
        "są zamknięte w aucie, sprawdzam je zaraz po otwarciu, przed wydaniem auta lub dorobieniem klucza.",
    ),
    ("Czy trzeba się umówić? W jakich godzinach działacie?", APPOINTMENT_ANSWER),
]


def _brand_price_block(brand):
    return (
        '  <h3 class="text-lg font-semibold mb-2">Cena i obszar dojazdu</h3>\n'
        f'  <p class="mb-4">{PRICE_SENTENCE} Dokładną cenę klucza {brand} podam przez telefon po modelu, '
        "roczniku i VIN. Dojeżdżam w całym Krakowie i okolicach — m.in. w Zabierzowie, Liszkach, "
        "Czernichowie, Krzeszowicach, Skawinie, Wieliczce, Zielonkach i Michałowicach. Zadzwoń: "
        f"{PHONE_HTML}.</p>\n"
    )


VAG_NEW_MACHINE = (
    "Mam nowe urządzenie do programowania kluczy i pilotów grupy VAG, więc obsługuję także nowsze "
    "roczniki {brand}, które wcześniej wymagały wizyty w ASO. Możliwość wykonania potwierdzam przez "
    "telefon po modelu, roczniku i VIN."
)

NEW_BRANDS = {
    "audi": {
        "name": "Programowanie Kluczy i Pilotów Samochodowych Audi",
        "item_label": "Programowanie Pilotów Audi",
        "order": 1,
        "meta_title": "Klucze i piloty Audi – programowanie z dojazdem, Kraków",
        "meta_description": (
            "Zapasowy kluczyk Audi albo nowy klucz po utracie wszystkich — programuję z dojazdem, "
            "także roczniki po 2016: A3, A4, A6, Q3, Q5. Kraków i okolice."
        ),
        "h1_tag": "Programowanie kluczy i pilotów Audi z dojazdem — Kraków",
        "description": (
            "Dorabiam i programuję kluczyki oraz piloty do Audi z dojazdem do klienta — A3, A4, A6, "
            "Q3, Q5 i inne modele, także z roczników po 2016. Kraków i okolice, płatność po sprawdzeniu."
        ),
        "seo_text": f"""<section class="w-full mx-auto">
  <h2 class="text-xl font-bold mb-4">Kluczyk do Audi bez wizyty w salonie</h2>
  <p class="mb-4">Właściciele Audi najczęściej dzwonią w dwóch sytuacjach: przy aucie z drugiej ręki został tylko jeden kluczyk albo jedyny klucz zginął lub przestał działać. Salon zwykle zamawia nowy klucz i każe przyprowadzić auto. Ja przyjeżdżam do Ciebie — pod dom, biuro albo na parking — i robię klucz na miejscu.</p>
  <h3 class="text-lg font-semibold mb-2">Zapasowy klucz Audi</h3>
  <p class="mb-4">Jeśli masz jeden działający kluczyk, najprostszą drogą jest {a(COPYING, 'kopia immobilizera')} i docięcie grotu. Klucz z grotem i immobilizerem kosztuje 300 zł. Drugi klucz warto mieć zanim pierwszy zawiedzie — przy utracie wszystkich kluczy usługa jest bardziej pracochłonna.</p>
  <h3 class="text-lg font-semibold mb-2">Zgubione wszystkie klucze</h3>
  <p class="mb-4">Gdy nie masz żadnego działającego klucza, nowy programuję do auta przez złącze OBD. Kosztuje to od 300 zł plus koszt pilota lub klucza (np. od ok. 150 zł). Jeśli auto jest zamknięte, najpierw je otwieram — zobacz {a(EMERGENCY, 'awaryjne otwieranie samochodów')}.</p>
  <h3 class="text-lg font-semibold mb-2">Nowsze Audi po 2016 roku</h3>
  <p class="mb-4">{VAG_NEW_MACHINE.format(brand='Audi')}</p>
  <h3 class="text-lg font-semibold mb-2">Modele Audi, z którymi spotykam się najczęściej</h3>
  <ul class="list-disc list-inside mb-4">
    <li>Audi A3 i A4 — popularne w wersjach kombi i sedan, często z drugiej ręki</li>
    <li>Audi A6 — auta służbowe i rodzinne</li>
    <li>Audi Q3 i Q5 — SUV-y, w których kluczyk bywa jedynym egzemplarzem po zakupie</li>
    <li>Audi A1 i A5 — rzadziej, ale również</li>
  </ul>
  <p class="mb-4">W Audi spotkasz zarówno klasyczne kluczyki składane, jak i nowsze kluczyki zbliżeniowe. To, czy wykonam klucz do Twojego egzemplarza, zależy od modelu i rocznika — dlatego zawsze potwierdzam to przed przyjazdem.</p>
  <h3 class="text-lg font-semibold mb-2">Pilot Audi przestał działać?</h3>
  <p class="mb-4">Nie zawsze trzeba od razu robić nowy klucz. Gdy zasięg pilota spada stopniowo, najczęściej wystarcza {a(CAR_KEYS + '/wymiana-baterii-w-pilotach-samochodowych', 'wymiana baterii')}. Jeśli pilot nie reaguje mimo nowej baterii, sprawdzam, czy da się go ponownie zaprogramować do auta, i dopiero wtedy proponuję nowy klucz. Przy wizycie przygotuj dowód rejestracyjny, dowód osobisty i wszystkie klucze, które masz do tego Audi — przy programowaniu warto, żeby każdy działający egzemplarz był na miejscu.</p>
{_brand_price_block('Audi')}</section>""",
        "faqs": [
            (
                "Czy zaprogramujesz klucz do Audi z rocznika po 2016?",
                "Tak, mam nowe urządzenie do programowania kluczy i pilotów grupy VAG. Możliwość "
                "potwierdzam przez telefon po modelu, roczniku i VIN.",
            ),
            (
                "Ile kosztuje zapasowy kluczyk do Audi?",
                "Klucz z grotem i immobilizerem kosztuje 300 zł. Gdy potrzebne jest programowanie przez "
                "OBD, usługa kosztuje od 300 zł plus koszt pilota lub klucza (np. od ok. 150 zł).",
            ),
            (
                "Zgubiłem jedyny klucz do Audi. Co teraz?",
                "Zadzwoń z numerem VIN. Jeśli auto jest zamknięte, otwieram je bez uszkodzeń, a potem "
                "programuję nowy klucz przez OBD na miejscu.",
            ),
        ],
    },
    "volkswagen": {
        "name": "Programowanie Kluczy i Pilotów Samochodowych Volkswagen",
        "item_label": "Programowanie Pilotów Volkswagen",
        "order": 16,
        "meta_title": "Klucze i piloty Volkswagen – programowanie z dojazdem Kraków",
        "meta_description": (
            "Kluczyk do Volkswagena z dojazdem: Golf, Passat, Polo, Tiguan, Touran, Caddy, także "
            "po 2016. Zapasowy klucz lub nowy po utracie wszystkich. Kraków i okolice."
        ),
        "h1_tag": "Programowanie kluczy i pilotów Volkswagen z dojazdem — Kraków",
        "description": (
            "Dorabiam i programuję kluczyki oraz piloty do Volkswagena z dojazdem do klienta — Golf, "
            "Passat, Polo, Tiguan, Touran, Caddy, także nowsze roczniki. Kraków i okolice."
        ),
        "seo_text": f"""<section class="w-full mx-auto">
  <h2 class="text-xl font-bold mb-4">Kluczyk do Volkswagena z dojazdem do klienta</h2>
  <p class="mb-4">Volkswagen to jedna z najczęściej spotykanych marek na polskich drogach — od rodzinnego Golfa i Passata po Caddy w firmie. W wielu z tych aut po latach zostaje jeden, wytarty kluczyk albo pilot z pękniętą obudową. Przyjeżdżam pod wskazany adres i dorabiam lub programuję klucz na miejscu, bez holowania auta.</p>
  <h3 class="text-lg font-semibold mb-2">Zapasowy kluczyk do VW</h3>
  <p class="mb-4">Masz jeden działający klucz? Wtedy wykonuję {a(COPYING, 'kopię immobilizera')} i docinam grot — klucz z grotem i immobilizerem kosztuje 300 zł. W Volkswagenach często spotkasz kluczyki składane („scyzoryki”); jeśli elektronika Twojego pilota działa, a pęknięta jest tylko obudowa, wystarczy {a(CAR_KEYS + '/wymiana-obudowy', 'wymiana obudowy')}.</p>
  <h3 class="text-lg font-semibold mb-2">Gdy nie masz żadnego klucza</h3>
  <p class="mb-4">Nowy klucz programuję wtedy przez złącze OBD: od 300 zł plus koszt pilota lub klucza (np. od ok. 150 zł), czyli razem zwykle od ok. 450 zł. Jeśli kluczyki zostały w zamkniętym aucie, zacznę od {a(EMERGENCY, 'awaryjnego otwarcia samochodu')}.</p>
  <h3 class="text-lg font-semibold mb-2">Volkswagen po 2016 roku</h3>
  <p class="mb-4">{VAG_NEW_MACHINE.format(brand='Volkswagena')} Dotyczy to także aut dostawczych, które są w firmach jedynym środkiem transportu — tu każdy dzień postoju kosztuje.</p>
  <h3 class="text-lg font-semibold mb-2">Najczęstsze modele Volkswagen</h3>
  <ul class="list-disc list-inside mb-4">
    <li>Volkswagen Golf i Polo</li>
    <li>Volkswagen Passat</li>
    <li>Volkswagen Tiguan i T-Roc</li>
    <li>Volkswagen Touran i Sharan</li>
    <li>Volkswagen Caddy i Transporter</li>
  </ul>
  <p class="mb-4">W starszych Golfach i Passatach najczęściej robię zapasowy kluczyk z kopią immobilizera, a w nowszych autach — zwłaszcza gdy klucz zginął — programowanie przez OBD. Zakres prac zależy od modelu i rocznika, dlatego przed przyjazdem proszę o numer VIN z dowodu rejestracyjnego — wtedy od razu powiem, co da się zrobić i ile to będzie kosztować.</p>
  <h3 class="text-lg font-semibold mb-2">Klucze do firmowych Volkswagenów</h3>
  <p class="mb-4">Dużo zleceń dotyczy aut firmowych — Caddy, Transportera czy Passata we flocie, gdzie jeden kluczyk krąży między kilkoma kierowcami. Dla firm mogę przygotować kilka zapasowych kluczy podczas jednej wizyty, na parkingu firmy, bez wyłączania auta z pracy na cały dzień. Wystarczy, że podasz numery VIN pojazdów, a przed przyjazdem potwierdzę, które auta obsłużę.</p>
{_brand_price_block('Volkswagen')}</section>""",
        "faqs": [
            (
                "Czy obsługujesz nowe Volkswageny, także po 2016 roku?",
                "Tak, mam nowe urządzenie do programowania kluczy i pilotów grupy VAG. Potwierdzam "
                "możliwość po modelu, roczniku i VIN.",
            ),
            (
                "Pilot do Golfa ma pękniętą obudowę. Czy trzeba robić nowy klucz?",
                "Nie zawsze. Jeśli elektronika działa, wystarczy wymiana obudowy kluczyka bez "
                "programowania.",
            ),
            (
                "Ile kosztuje nowy klucz do Volkswagena?",
                "Klucz z grotem i immobilizerem kosztuje 300 zł. Programowanie przez OBD to od 300 zł "
                "plus koszt pilota lub klucza (np. od ok. 150 zł), razem zwykle od ok. 450 zł.",
            ),
            ("Czy trzeba się umówić?", APPOINTMENT_ANSWER),
        ],
    },
    "seat": {
        "name": "Programowanie Kluczy i Pilotów Samochodowych Seat",
        "item_label": "Programowanie Pilotów Seat",
        "order": 15,
        "meta_title": "Klucze i piloty Seat – programowanie z dojazdem, Kraków",
        "meta_description": (
            "Kluczyk do Seata z dojazdem: Leon, Ibiza, Ateca, Arona, także roczniki po 2016. "
            "Kopia immobilizera lub programowanie przez OBD. Kraków i okolice."
        ),
        "h1_tag": "Programowanie kluczy i pilotów Seat z dojazdem — Kraków",
        "description": (
            "Dorabiam i programuję kluczyki oraz piloty do Seata z dojazdem do klienta — Leon, Ibiza, "
            "Ateca, Arona i inne modele, także po 2016. Kraków i okolice, płatność po sprawdzeniu."
        ),
        "seo_text": f"""<section class="w-full mx-auto">
  <h2 class="text-xl font-bold mb-4">Klucze do Seata na miejscu, u klienta</h2>
  <p class="mb-4">Seat to marka chętnie wybierana przez młodsze rodziny i kierowców jeżdżących dużo po mieście — Ibiza, Leon czy Arona często mają za sobą kilku właścicieli, a razem z autem przechodzi jeden kluczyk. Gdy potrzebujesz drugiego albo jedyny przestał działać, przyjeżdżam do Ciebie z urządzeniem do programowania i maszyną do kluczy.</p>
  <h3 class="text-lg font-semibold mb-2">Drugi kluczyk do Seata</h3>
  <p class="mb-4">Przy jednym działającym kluczu robię {a(COPYING, 'kopię immobilizera')} i docinam grot — klucz z grotem i immobilizerem kosztuje 300 zł. To najszybsza droga do zapasowego klucza i warto ją wybrać, zanim jedyny egzemplarz się zgubi. Nowy klucz sprawdzasz od razu przy aucie: otwieranie, zamykanie i rozruch silnika.</p>
  <h3 class="text-lg font-semibold mb-2">Utrata wszystkich kluczy</h3>
  <p class="mb-4">Bez działającego klucza programuję nowy przez złącze OBD: od 300 zł plus koszt pilota lub klucza (np. od ok. 150 zł). Gdy auto jest zamknięte, najpierw je otwieram bez uszkodzeń — szczegóły na stronie {a(EMERGENCY, 'awaryjne otwieranie samochodów')}.</p>
  <h3 class="text-lg font-semibold mb-2">Nowsze Seaty po 2016 roku</h3>
  <p class="mb-4">{VAG_NEW_MACHINE.format(brand='Seata')}</p>
  <h3 class="text-lg font-semibold mb-2">Modele Seat, z którymi pracuję</h3>
  <ul class="list-disc list-inside mb-4">
    <li>Seat Leon (hatchback i kombi)</li>
    <li>Seat Ibiza</li>
    <li>Seat Ateca i Arona</li>
    <li>Seat Toledo i Alhambra</li>
  </ul>
  <p class="mb-4">Seat korzysta z tej samej grupy rozwiązań co Volkswagen i Skoda, ale konkretny zakres prac zależy od modelu i rocznika. Dlatego przed przyjazdem pytam o VIN — dzięki temu ani Ty, ani ja nie działamy „w ciemno”, a cenę znasz, zanim wyjadę. Jeśli masz przy sobie wszystkie posiadane klucze do auta, zabierz je na wizytę — przy programowaniu sprawdzę, czy każdy z nich nadal działa.</p>
  <h3 class="text-lg font-semibold mb-2">Seat z drugiej ręki — sprawdź kluczyki</h3>
  <p class="mb-4">Kupując używanego Seata, zapytaj sprzedającego o liczbę kluczy. Jeśli dostałeś tylko jeden, dorób drugi od razu — kopia z działającego klucza jest prostsza i tańsza niż programowanie po utracie wszystkich. Przy okazji mogę sprawdzić, czy pilot ma dobry zasięg i czy obudowa nie jest pęknięta; zużytą obudowę wymieniam bez programowania. Przy wizycie przygotuj dowód rejestracyjny i dowód osobisty.</p>
{_brand_price_block('Seat')}</section>""",
        "faqs": [
            (
                "Czy zrobisz klucz do Seata Leon z rocznika po 2016?",
                "Tak, nowe urządzenie do grupy VAG obsługuje także nowsze roczniki. Możliwość "
                "potwierdzam po modelu, roczniku i VIN.",
            ),
            (
                "Mam jeden kluczyk do Seata. Ile kosztuje drugi?",
                "Klucz z grotem i kopią immobilizera kosztuje 300 zł.",
            ),
            (
                "Kluczyki zatrzasnęły się w Seacie. Co robić?",
                "Zadzwoń: 506 029 980. Otwieram auto bez uszkodzeń narzędziami Lishi, a w razie "
                "potrzeby od razu dorabiam nowy klucz.",
            ),
        ],
    },
}

NEW_EMERGENCY = {
    "name": "Awaryjne otwieranie samochodów",
    "slug": "awaryjne-otwieranie-samochodow",
    "item_label": "Awaryjne otwieranie samochodów",
    "parent_slug": "klucze-samochodowe",
    "meta_title": "Awaryjne otwieranie samochodów z dojazdem – Kraków",
    "meta_description": (
        "Zatrzaśnięte kluczyki w aucie lub zgubiony klucz? Otwieram samochód bez uszkodzeń "
        "narzędziami Lishi i na miejscu dorabiam klucz. Kraków i okolice."
    ),
    "h1_tag": "Awaryjne otwieranie samochodów bez uszkodzeń — z dojazdem, Kraków i okolice",
    "description": (
        "Nowość: awaryjnie otwieram samochody bez wybijania szyby i bez uszkadzania zamka — "
        "narzędziami Lishi, z dojazdem w Krakowie i okolicach. Jeśli klucz zginął, od razu "
        "dorabiam i programuję nowy."
    ),
    "seo_text": EMERGENCY_SEO,
    "faqs": EMERGENCY_FAQS,
}

# TODO (właściciel): Skoda – dodać stronę marki dopiero po potwierdzeniu, że nowa maszyna ją obsługuje.
