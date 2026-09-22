# Frontend-komponentit

Tämä hakemisto sisältää StudyAI-käyttöliittymän React-komponentit.

## Rakenne

```
components/
├── ui/           # shadcn/ui-peruskomponentit (Button, Input, Card, ...)
├── documents/    # Dokumenttien lataus ja listaus
└── chat/         # Keskustelunäkymä ja viestit
```

## Tila

Komponentit ovat toistaiseksi **runkoja (skeleton)**. Varsinainen toteutus
tehdään seuraavassa vaiheessa. shadcn/ui-komponentit generoidaan komennolla:

```bash
npx shadcn@latest add button input card textarea scroll-area