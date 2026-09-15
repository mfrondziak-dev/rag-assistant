# Tryb łatwy / Easy mode

Przyjazna wersja dla osób nietechnicznych: wgrywasz pliki i zadajesz pytania w
przeglądarce. Bez terminala, bez komend.

A friendly version for non-technical users: upload files and ask questions in the browser.
No terminal, no commands.

---

## Polski

### Uruchomienie

Jedno polecenie w katalogu projektu:

```bash
./start.sh
```

Skrypt sam:
1. utworzy środowisko i doinstaluje zależności (tylko przy pierwszym uruchomieniu),
2. sprawdzi, czy Ollama działa — w razie potrzeby uruchomi ją w tle,
3. pobierze brakujące modele (`nomic-embed-text`, `llama3.1`) — jednorazowo,
4. otworzy aplikację w przeglądarce.

### Skrót w menu systemowym

Żeby uruchamiać jednym kliknięciem (bez terminala):

```bash
bash scripts/install-desktop.sh
```

Doda wpis **„Zapytaj swoje dokumenty”** w menu aplikacji oraz skrót na pulpicie.
Uruchomienie z menu pokaże okno terminala z postępem — to normalne.

### Jak korzystać

1. **Wgraj dokumenty** — przeciągnij pliki PDF, Word (DOCX), TXT lub MD.
2. Kliknij **„Dodaj do bazy”** — aplikacja przetworzy dokumenty.
3. **Zadaj pytanie** w polu na dole. Odpowiedź pojawi się z listą źródeł.
4. Jeśli odpowiedzi nie ma w dokumentach, asystent powie, że **nie ma informacji** —
   niczego nie wymyśla.

### Prywatność

Wszystko działa **lokalnie na Twoim komputerze**. Dokumenty zapisuje się w
`data/uploads/`, a indeks w `data/index-simple/` — oba katalogi są ignorowane przez git.
Nic nie jest wysyłane do internetu.

### Gdy coś nie działa

Aplikacja ma **wbudowaną diagnostykę** (sekcja „Problemy? Diagnostyka” w panelu po lewej).
Pokazuje ✅/⚠️/❌ dla: Ollama zainstalowana, Ollama uruchomiona, modele AI, dokumenty, baza —
i podpowiada, co zrobić. Przycisk **„Uruchom Ollamę”** potrafi ją wystartować za Ciebie,
a **„Sprawdź ponownie”** odświeża stan.

| Problem | Rozwiązanie |
|---|---|
| „Brak połączenia z lokalnym modelem AI” | Kliknij „Uruchom Ollamę” albo wpisz `ollama serve` i odśwież |
| „Brakuje modeli AI” | Wykonaj pokazane polecenie `ollama pull ...` |
| Dokument się nie przetworzył | Sprawdź, czy to PDF/DOCX/TXT/MD |
| Odpowiedzi są wolne | Zmniejsz liczbę fragmentów w Ustawieniach zaawansowanych |

---

## English

### Start

One command in the project directory:

```bash
./start.sh
```

The script will: create the environment and install dependencies (first run only), make sure
Ollama is running (starting it in the background if needed), download the missing models
(`nomic-embed-text`, `llama3.1`) once, and open the app in your browser.

### Add a menu shortcut

To launch with a single click (no terminal):

```bash
bash scripts/install-desktop.sh
```

This adds an **“Ask your documents”** entry to the application menu and a desktop shortcut.

### How to use

1. **Upload documents** — drag PDF, Word (DOCX), TXT or MD files.
2. Click **“Add to the library”** to process them.
3. **Ask a question** in the box at the bottom. The answer comes with a list of sources.
4. If the answer is not in your documents, the assistant says it **does not have the
   information** — it does not make things up.

### Privacy

Everything runs **locally on your computer**. Documents are stored in `data/uploads/` and
the index in `data/index-simple/` — both ignored by git. Nothing is sent to the internet.

---

## Panel diagnostyczny / Diagnostics panel

### Polski — gdy wszystko działa

Panel boczny (po lewej) i checklista:

```
Język
[ Polski ▾ ]

▸ Ustawienia zaawansowane
▸ Problemy? Diagnostyka
    ✅ Ollama zainstalowana
    ✅ Ollama uruchomiona
    ✅ Modele AI
    ✅ Dokumenty w bibliotece — 1
    ✅ Baza gotowa
    [ Sprawdź ponownie ]
```

### Polski — brak Ollamy

Górny panel (reszta aplikacji jest ukryta do czasu naprawienia problemu):

```
┌──────────────────────────────────────────────────────────────┐
│ ⚠️  Problemy? Diagnostyka                                     │
│                                                               │
│ ✅ Ollama zainstalowana                                        │
│ ❌ Ollama uruchomiona                                          │
│ ❌ Modele AI — nomic-embed-text, llama3.1                      │
│ ⚠️ Dokumenty w bibliotece                                      │
│ ⚠️ Baza gotowa                                                 │
│                                                               │
│ Kliknij „Uruchom Ollamę” poniżej albo w terminalu wpisz:       │
│    ┌──────────────────────┐                                   │
│    │ ollama serve         │                                   │
│    └──────────────────────┘                                   │
│                                                               │
│ [    Uruchom Ollamę    ]      [   Sprawdź ponownie   ]         │
└──────────────────────────────────────────────────────────────┘
```

Uwagi:
- Przycisk „Uruchom Ollamę” pojawia się tylko wtedy, gdy Ollama jest zainstalowana, ale
  nie działa.
- Gdy Ollama nie działa, panel **nie** radzi pobierać modeli (modele „brakują” tylko
  dlatego, że Ollama leży).

### English — when Ollama is not running

```
┌──────────────────────────────────────────────────────────────┐
│ ⚠️  Troubleshooting                                           │
│                                                               │
│ ✅ Ollama installed                                            │
│ ❌ Ollama running                                              │
│ ❌ AI models — nomic-embed-text, llama3.1                      │
│ ⚠️ Documents in the library                                    │
│ ⚠️ Library index ready                                         │
│                                                               │
│ Click “Start Ollama” below, or run in a terminal:             │
│    ┌──────────────────────┐                                   │
│    │ ollama serve         │                                   │
│    └──────────────────────┘                                   │
│                                                               │
│ [    Start Ollama    ]        [   Check again   ]             │
└──────────────────────────────────────────────────────────────┘
```

To see this screen without touching your real Ollama, run `make demo-error`.

