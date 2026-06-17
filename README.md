# Talk to your data - Demo Snowflake + Streamlit

Demo live na prezentacje techniczna. Petla: widownia wypelnia ankiete przez QR ->
dane laduja do Snowflake -> na zywo odpytujesz ICH dane naturalnym jezykiem przez Cortex.

## Wymagania wstepne

- Konto Snowflake z dostepem ACCOUNTADMIN (jednorazowo do konfiguracji)
- Konto na [Streamlit Community Cloud](https://streamlit.io/cloud)
- Repozytorium na GitHubie (Community Cloud czyta kod z GitHub)
- Python 3.10+ (lokalnie, do testow)

---

## Krok 1: Konfiguracja Snowflake

Uruchom skrypty SQL w Snowsight (Worksheets) jako ACCOUNTADMIN:

**1a. Struktura i uprawnienia**

Otworz `sql/01_setup.sql` i uruchom calosc. Skrypt tworzy:
- baze `DEMO` i tabele `AUDIENCE_SURVEY`
- warehouse `DEMO_WH` (XSMALL, autosuspend 60s)
- role `DEMO_SURVEY_ROLE` z prawami INSERT + SELECT tylko na tabeli
- uzytkownika `DEMO_SURVEY_USER` z ta rola

Zmien haslo ustawione w skrypcie zanim udostepnisz dane komukolwiek.

**1b. Dane testowe (opcjonalnie)**

Uruchom `sql/02_seed_data.sql`, zeby wgrac 8 przykladowych odpowiedzi.
Przydatne jako siatka bezpieczenstwa gdy sala bedzie nieaktywna.

---

## Krok 2: Deploy survey-app na Streamlit Community Cloud

1. Wgraj repo na GitHub (fork lub wlasne repo).
2. Zaloguj sie na [share.streamlit.io](https://share.streamlit.io) i kliknij **New app**.
3. Wybierz repozytorium i ustaw:
   - **Branch:** main
   - **Main file path:** `survey-app/survey_app.py`
4. Rozwin **Advanced settings** i wklej sekcje **Secrets** z prawdziwymi wartosciami:

```toml
[snowflake]
account   = "twoja-organizacja-twoje-konto"
user      = "DEMO_SURVEY_USER"
password  = "TwojeHaslo"
warehouse = "DEMO_WH"
database  = "DEMO"
schema    = "PUBLIC"
role      = "DEMO_SURVEY_ROLE"
```

5. Kliknij **Deploy**. Aplikacja bedzie dostepna pod adresem `*.streamlit.app`.

**Jak znalezc wartosc `account`:**
W Snowsight kliknij inicjaly w lewym dolnym rogu -> klikij nazwe konta.
Format: `organizacja-konto`, np. `myorg-myaccount1`.
Alternatywnie odczytaj z URL Snowsight: `https://[account].snowflakecomputing.com`.

**Wazne:** dodaj `.streamlit/secrets.toml` do `.gitignore` - nigdy nie commituj prawdziwych secrets.

---

## Krok 3: Generowanie kodu QR

Masz juz adres survey-app, np. `https://twoja-ankieta.streamlit.app`.

Opcje generowania QR:
- Online: [qr-code-generator.com](https://www.qr-code-generator.com) lub [qrcode.me](https://qrcode.me)
- Lokalnie:
  ```
  pip install qrcode[pil]
  python -c "import qrcode; qrcode.make('TWOJ_URL').save('qr.png')"
  ```

Wstaw `qr.png` do slajdow. Miej tez skrocony URL (np. przez Bitly) jako backup.

---

## Krok 4: Wgranie text2sql-app do Snowsight

1. W Snowsight przejdz do **Streamlit** w lewym panelu.
2. Kliknij **+ Streamlit App**.
3. Podaj nazwe aplikacji, wybierz:
   - Warehouse: `DEMO_WH`
   - Database: `DEMO`
   - Schema: `PUBLIC`
4. Wklej zawartosc `text2sql-app/streamlit_app.py` do edytora kodu.
5. Kliknij **Run**.

Aplikacja uzywa `get_active_session()` i nie wymaga zadnych sekretow ani dodatkowej konfiguracji.

---

## Przykladowe pytania do demo

Te pytania sa sprawdzone i bezpieczne - Cortex radzi sobie z nimi przy typowym rozkladzie odpowiedzi:

- "Ile osob preferuje Pythona?"
- "Srednie lata doswiadczenia wedlug ulubionej chmury"
- "Ile kaw dziennie pija data engineerzy?"
- "Ktory jezyk programowania jest najpopularniejszy?"
- "Ile osob uzywa AI codziennie w pracy?"
- "Porownaj srednia liczbe kaw wedlug roli"
- "Ile odpowiedzi zebralismy lacznie?"
- "Pokaz wszystkie odpowiedzi posortowane od najnowszej"

---

## Sugerowany przebieg prezentacji

**Przed prezentacja:**
- Sprawdz polaczenie survey-app z Snowflake (wyslij testowa odpowiedz)
- Uruchom text2sql-app w Snowsight i przetestuj proste pytanie
- Opcjonalnie wgraj seed data jako siatke bezpieczenstwa

**1. Start (2 min):**
Pokaz QR na slajdzie, popros widownie o wypelnienie ankiety.
Miej na ekranie survey-app z licznikiem odpowiedzi.

**2. Czas wypelniania ankiety (3-5 min):**
Omow architekture (3 komponenty na 3 slajdach), obserwuj jak licznik rosnie.

**3. Live SELECT (1 min):**
W Snowsight -> Worksheets:
```sql
SELECT * FROM DEMO.PUBLIC.AUDIENCE_SURVEY ORDER BY submitted_at DESC LIMIT 20;
```
Pokaz ze dane naprawde sa w bazie - efekt "wow" dla widowni.

**4. Text2SQL (10-15 min):**
Przelacz na text2sql-app w Snowsight.
- Zacznij od prostego pytania (count, lista ról).
- Przejdz do agregacji (srednia, grupowanie, porownanie).
- Zmien model w dropdown i porownaj wygenerowany SQL.
- Pozwol widowni proponowac pytania - angaz widowni.

**5. Zamkniecie:**
Wskazuj na wygenerowany SQL obok wynikow - podkres ze Cortex pisze prawdziwy SQL
na prawdziwych danych widowni, a nie zwraca hardcoded odpowiedzi.

---

## Struktura repozytorium

```
.
├── survey-app/
│   ├── survey_app.py               # Aplikacja ankiety (Community Cloud)
│   ├── requirements.txt
│   └── .streamlit/
│       └── secrets.toml.example    # Wzor konfiguracji - nie commituj secrets.toml!
├── text2sql-app/
│   └── streamlit_app.py            # Text2SQL (Streamlit in Snowflake)
├── sql/
│   ├── 01_setup.sql                # Tabela, warehouse, rola, uzytkownik
│   └── 02_seed_data.sql            # Dane testowe (8 rekordow)
└── README.md
```

---

## Rozwiazywanie problemow

| Problem | Prawdopodobna przyczyna | Rozwiazanie |
|---|---|---|
| survey-app nie laczy z Snowflake | Bledny format account lub haslo | Sprawdz format `org-account` w Snowsight; zweryfikuj secrets w Community Cloud |
| Cortex COMPLETE zwraca blad 404 | Model niedostepny w regionie konta | Zmien model na `snowflake-arctic` lub `llama3.1-8b` |
| Brak danych po SELECT w Worksheets | Warehouse nie uruchomil sie | Sprawdz `AUTO_RESUME = TRUE` w DEMO_WH; uruchom WH recznie |
| Model generuje zly SQL | Pytanie zbyt ogolne lub zlozony JOIN | Uprosz pytanie lub zmien model; sprawdz schemat w expander |
| Licznik ankiety nie rosnie | Polaczenie OK, ale brak refresh | Kliknij przycisk "Odswiez licznik" |
