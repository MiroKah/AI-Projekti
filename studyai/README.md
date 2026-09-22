# StudyAI 📚🤖

Tuotantotasoinen RAG-sovellus (Retrieval-Augmented Generation), jonka avulla käyttäjä voi
keskustella omien PDF-dokumenttiensa kanssa. Vastaukset perustuvat **vain** ladattuun materiaaliin.

> **Tila:** Projektirunko (skeleton). Ominaisuuksien toteutus on seuraava vaihe.
> Tässä vaiheessa on luotu koko kansiorakenne, konfiguraatiot ja tyypit.

---

## 🏛️ Arkkitehtuuri

RAG-putki:

```
PDF ──► Tekstin purku ──► Chunkkaus ──► Embeddings ──► pgvector
                                                          │
Kysymys ──► Embeddings ──► Vektorihaku ──► Konteksti ──► OpenAI Responses API ──► Vastaus + lähteet
```

### Teknologiat

| Kerros    | Teknologia                                                        |
|-----------|-------------------------------------------------------------------|
| Frontend  | Next.js 15, React, TypeScript, Tailwind CSS, shadcn/ui            |
| Backend   | FastAPI, Python 3.12                                              |
| Tietokanta| PostgreSQL 16 + pgvector                                          |
| AI        | OpenAI Responses API, OpenAI Embeddings (`text-embedding-3-small`)|
| PDF       | PyMuPDF (fitz)                                                    |

### Clean Architecture (backend)

```
backend/app/
├── core/            # Konfiguraatio, logging, poikkeukset, DI-kontit
├── domain/          # Yrityslogiikan ydin: entiteetit, rajapinnat (ei riippuvuuksia)
├── application/     # Käyttötapaukset (use cases) + DTO:t
├── infrastructure/  # Ulkoiset toteutukset: DB, OpenAI, PDF, repositoriot
└── presentation/    # FastAPI-reitit, riippuvuudet, skeemat
```

Riippuvuudet osoittavat aina **sisäänpäin** (presentation → application → domain).
Infrastruktuuri toteuttaa domainin rajapinnat (dependency inversion).

---

## 📁 Kansiorakenne

```
studyai/
├── docker-compose.yml         # db + backend + frontend
├── .env.example               # juuren ympäristömuuttujat
├── .gitignore
├── README.md
├── db/
│   └── init.sql               # pgvector-skeema + taulut
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── .env.example
│   └── app/
│       ├── main.py
│       ├── core/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── presentation/
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    ├── next.config.ts
    ├── tailwind.config.ts
    ├── postcss.config.mjs
    ├── components.json
    ├── .env.local.example
    ├── src/
    │   ├── app/
    │   ├── components/
    │   ├── lib/
    │   └── types/
    └── public/
```

---

## 🚀 Käynnistys

### 1. Ympäristömuuttujat

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Täytä `backend/.env`-tiedostoon oma `OPENAI_API_KEY`.

### 2. Käynnistä Docker Composella

```bash
docker compose up --build
```

Palvelut:

| Palvelu   | Osoite                        |
|-----------|-------------------------------|
| Frontend  | http://localhost:3000         |
| Backend   | http://localhost:8000         |
| API-docs  | http://localhost:8000/docs    |
| PostgreSQL| localhost:5432                |

### 3. Paikallinen kehitys (ilman Dockeria)

**Backend:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

---

## 🗺️ Tietokantaskeema

| Taulu           | Kuvaus                                              |
|-----------------|-----------------------------------------------------|
| `documents`     | Ladatut PDF:t ja niiden käsittelytila                |
| `chunks`        | Tekstinpalat + `vector(1536)` embeddings            |
| `chat_sessions` | Keskusteluistunnot (liitetty dokumenttiin)          |
| `chat_messages` | Viestit + lähteet (JSONB)                           |

---

## 🔌 API-rajapinnat (suunniteltu)

| Metodi | Polku                          | Kuvaus                        |
|--------|--------------------------------|-------------------------------|
| POST   | `/api/v1/documents`            | Lataa PDF                     |
| GET    | `/api/v1/documents`            | Listaa dokumentit             |
| GET    | `/api/v1/documents/{id}`       | Hae dokumentti                |
| DELETE | `/api/v1/documents/{id}`       | Poista dokumentti             |
| POST   | `/api/v1/chat`                 | Kysy dokumentilta (RAG)       |
| GET    | `/api/v1/health`               | Terveystarkistus              |

---

## 🔒 Tietoturva & parhaat käytännöt

- Salaisuudet vain `.env`-tiedostoissa (ei koskaan repositorioon).
- PDF-käsittely eristettynä infrastruktuurikerrokseen.
- Vastaukset rajataan kontekstiin (prompt injection -suojaus).
- Vain ladattu materiaali vastausten pohjana (ei ulkoista tietoa).

---

## 📄 Lisenssi

MIT