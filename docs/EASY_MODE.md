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

**Windows:** zamiast `./start.sh` uruchom **`start.bat`** (dwuklik albo z terminala). Robi
dokładnie to samo i sam otwiera przeglądarkę.

### Skrót w menu systemowym

Żeby uruchamiać jednym kliknięciem (bez terminala):

```bash
bash scripts/install-desktop.sh
```

Doda wpis **„Zapytaj swoje dokumenty”** w menu aplikacji oraz skrót na pulpicie.
Uruchomienie z menu pokaże okno terminala z postępem — to normalne.

**Windows** (skrót na pulpicie):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-desktop.ps1
```

### Jak korzystać

1. **Wybierz źródło dokumentów** — „Wgraj pliki” albo „Wskaż folder”.
2. **Wgraj pliki** — przeciągnij PDF, Word (DOCX), TXT lub MD. Albo **wskaż folder**:
   kliknij **„📁 Wybierz folder…”**, żeby otworzyć systemowe okno wyboru, albo wpisz ścieżkę
   ręcznie i kliknij „Sprawdź folder”.
3. Kliknij **„Dodaj do bazy”** / **„Indeksuj ten folder”** — zobaczysz **pasek postępu**
   (osobno czytanie plików i tworzenie embeddingów).
4. **Zadaj pytanie** w polu na dole. Odpowiedź pojawi się z listą źródeł.
5. Pod odpowiedzią asystent zaproponuje **klikane pytania uzupełniające** — jedno kliknięcie
   zada je od razu.
6. Jeśli odpowiedzi nie ma w dokumentach, asystent powie, że **nie ma informacji** —
   niczego nie wymyśla.

> Przy wskazywaniu folderu aplikacja **pomija** katalogi techniczne i ukryte
> (`.git`, `node_modules`, `.venv`, `__pycache__` itd.), żeby nie indeksować śmieci.

> Duże kolekcje (setki plików) indeksują się długo — pokazujemy **pasek postępu**
> (osobno faza czytania plików i faza tworzenia embeddingów). Pliki, których nie da się
> odczytać (np. uszkodzone lub zaszyfrowane PDF), są **pomijane z ostrzeżeniem**, zamiast
> przerywać całe indeksowanie.

### Wskazanie folderu (linia poleceń)

Jeśli wolisz terminal, użyj `rag.sh` — działa z dowolnego katalogu:

```bash
~/code_projects/rag-assistant/rag.sh ingest --raw ~/Dokumenty --index data/index-docs
~/code_projects/rag-assistant/rag.sh ask --index data/index-docs "o co pytasz?"
```

Albo z katalogu projektu, krócej:

```bash
make index-folder DIR=~/Dokumenty
make ask-folder Q="o co pytasz?"
```

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

**Windows:** run **`start.bat`** instead of `./start.sh` (double-click it or run it from a
terminal). It does the same and opens the browser for you.

### Add a menu shortcut

To launch with a single click (no terminal):

```bash
bash scripts/install-desktop.sh
```

This adds an **“Ask your documents”** entry to the application menu and a desktop shortcut.

**Windows** (desktop shortcut):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-desktop.ps1
```

### How to use

1. **Choose the source** — “Upload files” or “Point at a folder”.
2. **Upload files** — drag PDF, Word (DOCX), TXT or MD. Or **point at a folder**: click
   **“📁 Choose folder…”** to open the system dialog, or type the path and click
   “Check folder”.
3. Click **“Add to the library”** / **“Index this folder”** — a **progress bar** shows the
   reading and embedding phases.
4. **Ask a question** in the box at the bottom. The answer comes with a list of sources.
5. Below the answer the assistant offers **clickable follow-up questions** — one click asks
   them.
6. If the answer is not in your documents, the assistant says it **does not have the
   information** — it does not make things up.

> When pointing at a folder, the app **skips** technical and hidden directories
> (`.git`, `node_modules`, `.venv`, `__pycache__`, etc.) so it does not index junk.

> Large collections (hundreds of files) take a long time to index; a **progress bar** is
> shown (a separate phase for reading files and for building embeddings). Files that cannot
> be read (e.g. corrupted or encrypted PDFs) are **skipped with a warning** instead of
> aborting the whole indexing run.

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

