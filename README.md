# ⚽ Pass Network & Team Structure Analysis

**Julie Landrevie — Football Data & Video Analyst**

Analyse des réseaux de passes, identification des joueurs-pivots et comparaison de la structure tactique de deux équipes à partir des données **StatsBomb Open Data**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pass-network.streamlit.app)

---

## 🌐 Demo live

**[pass-network.streamlit.app](https://pass-network.streamlit.app)**

Sélectionne une compétition, un match et une période — le réseau de passes se génère en temps réel depuis les données StatsBomb Open Data.

---

## 🗂️ Structure du projet

```
pass-network/
├── app.py                          # Dashboard Streamlit (livrable principal)
├── requirements.txt                # Dépendances Python
├── README.md
├── .gitignore
│
├── src/
│   ├── __init__.py
│   └── pass_network.py             # Module réutilisable (PassNetworkAnalyzer)
│
├── notebooks/
│   └── pass_network_analysis.ipynb # Analyse complète annotée
│
├── portfolio/
│   └── index.html                  # Page de présentation portfolio
│
├── data/
│   └── exports/                    # CSV générés (gitignorés)
│
├── tests/
│   └── test_pass_network.py        # Tests unitaires (pytest)
│
└── docs/
    └── (screenshots, notes)
```

---

## 🚀 Lancement rapide

### Option 1 — App en ligne

👉 **[pass-network.streamlit.app](https://pass-network.streamlit.app)** — aucune installation requise.

### Option 2 — En local

```bash
# Cloner le repo
git clone https://github.com/Julie-Landrevie/pass-network.git
cd pass-network

# Environnement virtuel
python3 -m venv .venv
source .venv/bin/activate        # Mac / Linux
.venv\Scripts\activate           # Windows

# Dépendances
pip install -r requirements.txt

# Lancer le dashboard
python3 -m streamlit run app.py
```

Ouvre automatiquement `http://localhost:8501`

### Option 3 — Module Python

```python
from src.pass_network import PassNetworkAnalyzer, quick_analysis

# Analyse en 3 lignes
analyzer = quick_analysis(competition_id=11, season_id=90, match_index=0)
print(analyzer.summary())
analyzer.plot_all(save_dir='data/exports/')

# Usage détaillé
analyzer = PassNetworkAnalyzer(match_id=3773386, min_passes=3, period='Full Match')
analyzer.run()
analyzer.plot_network('Barcelona')
analyzer.export('data/exports/')
```

### Option 4 — Notebook Jupyter

```bash
jupyter notebook notebooks/pass_network_analysis.ipynb
```

### Tests

```bash
pytest tests/ -v
```

---

## 📊 Fonctionnalités

| Feature | Dashboard | Module | Notebook |
|---|---|---|---|
| Pass network (nœuds + arêtes) | ✅ | ✅ | ✅ |
| Heatmap positions moyennes | ✅ | ✅ | ✅ |
| Betweenness centrality | ✅ | ✅ | ✅ |
| Métriques équipe (density, clustering) | ✅ | ✅ | ✅ |
| Comparaison deux équipes | ✅ | ✅ | ✅ |
| Filtre 1ère / 2ème mi-temps | ✅ | ✅ | ✅ |
| Export CSV | — | ✅ | ✅ |
| Interprétation tactique auto | ✅ | — | — |
| Anti-collision labels | ✅ | ✅ | ✅ |
| 200+ joueurs mappés | ✅ | ✅ | ✅ |

---

## 🔧 Stack technique

- **Données** : StatsBomb Open Data (`statsbombpy`)
- **Visualisation** : `mplsoccer`, `matplotlib`, `Plotly`
- **Graphes** : `NetworkX` (betweenness, density, clustering)
- **Dashboard** : `Streamlit` — déployé sur Streamlit Cloud
- **Tests** : `pytest` (18 tests unitaires)

---

## 📁 Données disponibles (StatsBomb Open Data)

Compétitions accessibles gratuitement (sélection) :

| Competition | ID | Saisons |
|---|---|---|
| La Liga | 11 | 2009–2021 |
| Champions League | 16 | 2003–2019 |
| FIFA World Cup | 43 | 2018, 2022 |
| UEFA Euro | 55 | 2020, 2024 |
| Premier League | 2 | 2003/04, 2015/16 |
| Ligue 1 | 7 | 2015/16, 2021/22, 2022/23 |
| Bundesliga | 9 | 2015/16, 2023/24 |

---

## 🎓 Certifications

- Sports Analytics — University of Michigan (Coursera)
- Analyse Vidéo et Data dans le Sport — Université de Lorraine
- Dartfish Certified Analyst

---

## 📩 Contact

julie.landrevie@free.fr
