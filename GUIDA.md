# RAG API — Guida Setup Completa

## Modello scelto
**Qwen3 Coder 480B A35B** via OpenRouter (gratuito)
- 480B parametri totali, 35B attivi per token (MoE)
- 262K context window
- Ottimizzato per coding agentico e tool use
- ID modello: `qwen/qwen3-coder-480b-a35b:free`

---

## Step 1 — Ottieni la chiave OpenRouter

1. Vai su **https://openrouter.ai**
2. Clicca **Sign In** in alto a destra → registrati con Google o email
3. Una volta loggato, vai su **https://openrouter.ai/keys**
4. Clicca **Create Key**
5. Dai un nome alla chiave (es. `rag-project`) → clicca **Create**
6. **Copia subito la chiave** — inizia con `sk-or-v1-...`
   ⚠️ Non la potrai rivedere dopo, salvala in un posto sicuro

---

## Step 2 — Imposta la variabile d'ambiente

### Windows (PowerShell)
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-TUACHIAVE"
```

### Windows (CMD)
```cmd
set OPENROUTER_API_KEY=sk-or-v1-TUACHIAVE
```

### Linux / Mac
```bash
export OPENROUTER_API_KEY=sk-or-v1-TUACHIAVE
```

> 💡 Per renderla permanente su Windows: cerca "Variabili d'ambiente" nel menu Start
> e aggiungila nelle variabili utente.

---

## Step 3 — Installa le dipendenze

```bash
pip install -r requirements.txt
```

---

## Step 4 — Installa e avvia Ollama (per gli embeddings)

1. Scarica Ollama da **https://ollama.com**
2. Installalo con le opzioni default
3. Apri un terminale e scarica il modello embeddings:

```bash
ollama pull nomic-embed-text
```

4. Avvia Ollama (tienilo aperto in background):

```bash
ollama serve
```

---

## Step 5 — Prepara i tuoi documenti

Crea una cartella chiamata `data` nella stessa directory dei file Python
e metti dentro i tuoi file `.md` da indicizzare:

```
progetto/
├── data/
│   ├── documento1.md
│   └── documento2.md
├── api.py
├── create_database.py
├── query_data.py
└── requirements.txt
```

---

## Step 6 — Crea il database vettoriale

```bash
python create_database.py
```

Output atteso:
```
Caricati 2 documenti.
Divisi 2 documenti in 45 pezzi.
Salvati 45 pezzi in chroma.
```

---

## Step 7 — Avvia l'API

```bash
uvicorn api:app --reload --port 8000
```

---

## Step 8 — Testa l'API

Apri il browser su:
```
http://localhost:8000/docs
```

Trovi l'interfaccia Swagger per testare tutti gli endpoint.

### Oppure via curl:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"domanda": "La tua domanda qui"}'
```

---

## Endpoints disponibili

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/` | Stato API e modello attivo |
| POST | `/query` | Interroga il database |
| POST | `/rebuild-db` | Rigenera il database dai file .md |
| GET | `/health` | Health check |

---

## Struttura file

```
progetto/
├── data/               ← metti qui i tuoi file .md
├── chroma/             ← generato automaticamente da create_database.py
├── api.py              ← FastAPI server
├── create_database.py  ← indicizza i documenti
├── query_data.py       ← logica RAG + OpenRouter
└── requirements.txt    ← dipendenze Python
```

---

## Riavvio rapido (sessioni successive)

```bash
# Terminale 1 — Ollama (embeddings)
ollama serve

# Terminale 2 — API
uvicorn api:app --reload --port 8000
```
