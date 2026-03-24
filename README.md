# GRF Dashboard

Dashboard analytique pour les données GRF 2025/2026 — Randstad Solutions Clients.

## Fonctionnalités

- **Vue d'ensemble** — KPIs globaux, graphiques synthétiques
- **Demandes Pilott** — Suivi des demandes par client, statut, recours
- **BAPS Contrats** — Analyse des contrats par ETT, client, mois
- **Pixid Commandes** — Suivi des commandes et postes
- **Candidatures** — Analyse des expressions de besoin et candidatures
- **Recherche globale** — Recherche full-text dans toutes les sources simultanément

## Sources de données (7 fichiers)

| Fichier | Lignes | Description |
|---------|--------|-------------|
| BAPS | 8 324 | Contrats par client/ETT/agence/mois |
| Pilott | 4 778 | Demandes détaillées 2026 |
| Pixid Commandes | 13 960 | Commandes publiées sur PIXID |
| Pixid Besoin/Cand. | 24 681 | Expressions de besoin et candidatures |
| Peopulse Randstad | 674 | Demandes par agence |
| Peopulse RIS | 392 | Demandes RIS |
| Peopulse Selectt | 2 022 | Demandes Selectt |

## Installation locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déploiement Streamlit Cloud

1. Fork ce repo sur GitHub
2. Aller sur [share.streamlit.io](https://share.streamlit.io)
3. Connecter le repo → sélectionner `app.py`
4. Deploy

## Structure

```
grf_app/
├── app.py              # Application principale
├── requirements.txt    # Dépendances Python
├── README.md
└── data/               # Données CSV (ne pas committer si données sensibles)
    ├── baps.csv
    ├── pilott.csv
    ├── pixid_commandes.csv
    ├── pixid_besoin.csv
    ├── peopulse_randstad.csv
    ├── peopulse_ris.csv
    └── peopulse_selectt.csv
```

## Note sécurité

Les fichiers CSV contiennent des données RH potentiellement sensibles.  
Ajouter `data/` au `.gitignore` si le repo est public.
