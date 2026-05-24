"""
Pass Network & Team Structure Dashboard
Julie Landrevie — Football Data & Video Analyst
Sources: StatsBomb Open Data + FBref
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba
import networkx as nx
from mplsoccer import Pitch, VerticalPitch
from statsbombpy import sb
import warnings
warnings.filterwarnings("ignore")


# ─── PLAYER NAME CLEANER ──────────────────────────────────────────────────────

# Maps full StatsBomb names to clean public-facing names
# Sources : StatsBomb open data — Ligue 1, La Liga, Champions League, World Cup
PLAYER_NAME_MAP = {
    # ── PSG / Ligue 1 ──────────────────────────────────────────────────────────
    "Achraf Hakimi Mouh":                      "Achraf Hakimi",
    "Kylian Mbappé Lottin":                    "Kylian Mbappé",
    "Lionel Andrés Messi Cuccittini":          "Lionel Messi",
    "Neymar da Silva Santos Junior":           "Neymar Jr.",
    "Danilo Luís Hélio Pereira":               "Danilo Pereira",
    "Vitor Machado Ferreira":                  "Vitinha",
    "Warren Zaire Emery":                      "Warren Zaïre-Emery",
    "Fabián Ruiz Peña":                        "Fabián Ruiz",
    "Juan Bernat Velasco":                     "Juan Bernat",
    "Sergio Ramos García":                     "Sergio Ramos",
    "Marcos Aoás Corrêa":                      "Marquinhos",
    "Carlos Soler Barragán":                   "Carlos Soler",
    "Nordi Mukiele Mulere":                    "Nordi Mukiele",
    "Pablo Sarabia García":                    "Pablo Sarabia",
    "Renato Júnior Luz Sanches":               "Renato Sanches",
    "Leandro Daniel Paredes":                  "Leandro Paredes",
    "Idrissa Gana Gueye":                      "Idrissa Gueye",
    "El Chadaille Bitshiabu":                  "E. Bitshiabu",
    # ── Ligue 1 général ────────────────────────────────────────────────────────
    "Arnaud Kalimuendo Muinga":                "Arnaud Kalimuendo",
    "Benoît Badiashile Mukinayi":              "Benoît Badiashile",
    "Benoît Guy Robert Costil":                "Benoît Costil",
    "Caio Henrique Oliveira Silva":            "Caio Henrique",
    "Chancel Mbemba Mangulu":                  "Chancel Mbemba",
    "Dante Bonfim da Costa Santos":            "Dante",
    "Deiver Andrés Machado Mena":              "Deiver Machado",
    "Facundo Axel Medina":                     "Facundo Medina",
    "Farid El Melali":                         "Farid El Melali",
    "Ikoma Loïs Openda":                       "Loïs Openda",
    "Ismaily Gonçalves dos Santos":            "Ismaily",
    "Jean Emile Junior Onana Onana":           "Jean Onana",
    "Jean Lucas de Souza Oliveira":            "Jean Lucas",
    "José Miguel da Rocha Fonte":              "José Fonte",
    "Junior Castello Lukeba":                  "Castello Lukeba",
    "Karl Brillant Toko Ekambi":               "Karl Toko Ekambi",
    "Leonardo Julián Balerdi Rossa":           "Leonardo Balerdi",
    "Lesley Chimuanya Ugochukwu":              "Lesley Ugochukwu",
    "Marshall Nyasha Munetsi":                 "Marshall Munetsi",
    "Mathis Rayan Cherki":                     "Rayan Cherki",
    "Mattéo Guendouzi Olié":                   "Mattéo Guendouzi",
    "Moses Daddy-Ajala Simon":                 "Moses Simon",
    "Mostafa Mohamed Ahmed Abdallah":          "Mostafa Mohamed",
    "Nicolás Alejandro Tagliafico":            "Nicolás Tagliafico",
    "Nordi Mukiele Mulere":                    "Nordi Mukiele",
    "Nuno Albertino Varela Tavares":           "Nuno Tavares",
    "Pablo Paulino Rosario":                   "Pablo Rosario",
    "Pau López Sabata":                        "Pau López",
    "Sepe Elye Wahi":                          "Elye Wahi",
    "Stephy Alvaro Mavididi":                  "Stephy Mavididi",
    "Terem Igobor Moffi":                      "Terem Moffi",
    "Tiago Emanuel Embaló Djaló":              "Tiago Djaló",
    "André Filipe Tavares Gomes":              "André Gomes",
    "Alexis Alejandro Sánchez Sánchez":        "Alexis Sánchez",
    "Eric Bertrand Bailly":                    "Eric Bailly",
    "Fábio Pereira da Silva":                  "Fábio",
    "Abdoul Bamo Meité":                       "Abdoulaye Meïté",
    # ── Barcelona ──────────────────────────────────────────────────────────────
    "Gerard Piqué Bernabéu":                   "Gerard Piqué",
    "Sergio Busquets i Burgos":                "Busquets",
    "Sergi Roberto Carnicer":                  "Sergi Roberto",
    "Jordi Alba Ramos":                        "Jordi Alba",
    "Anssumane Fati Vieira":                   "Ansu Fati",
    "Pedri González López":                    "Pedri",
    "Francisco Román Alarcón Suárez":          "Isco",
    "Martin Braithwaite Christensen":          "Martin Braithwaite",
    "Marc-André ter Stegen":                   "M. ter Stegen",
    "Marc Bartra Aregall":                     "Marc Bartra",
    # ── Real Madrid ────────────────────────────────────────────────────────────
    "Marcelo Vieira da Silva Júnior":          "Marcelo",
    "Dani Carvajal Ramos":                     "Dani Carvajal",
    "Vinicius José Paixão de Oliveira Júnior": "Vinícius Jr.",
    "Marco Asensio Willemsen":                 "Marco Asensio",
    "Saúl Ñíguez Esclapez":                    "Saúl",
    "Koke Resurrección Uribe":                 "Koke",
    # ── Alavés ─────────────────────────────────────────────────────────────────
    "Rodrigo Andrés Battaglia":                "Rodrigo Battaglia",
    "Fernando Pacheco Flores":                 "Fernando Pacheco",
    "Joaquín Navarro Jiménez":                 "Joaquín Navarro",
    "Rubén Duarte Sánchez":                    "Rubén Duarte",
    "José Ignacio Peleteiro Ramallo":          "Joselu",
    "Edgar Antonio Méndez Ortega":             "Edgar Méndez",
    "Víctor Laguardia Cisneros":               "Víctor Laguardia",
    "Tomás Alejandro Pina Caballero":          "Tomás Pina",
    "Martín Aguirregabiria Padilla":           "M. Aguirregabiria",
    "Luis Rioja González":                     "Luis Rioja",
    # ── Premier League / Champions League ──────────────────────────────────────
    "Mohamed Salah Ghaly":                     "Mohamed Salah",
    "Alisson Ramsay Becker":                   "Alisson",
    "Roberto Firmino Barbosa de Oliveira":     "Roberto Firmino",
    "Trent Alexander-Arnold":                  "T. Alexander-Arnold",
    "Raheem Shaquille Sterling":               "Raheem Sterling",
    "Leroy Aziz Sané":                         "Leroy Sané",
    "Kingsley Junior Coman":                   "Kingsley Coman",
    "Serge David Gnabry":                      "Serge Gnabry",
    "Ederson Santana de Moraes":               "Ederson",
    "İlkay Gündoğan":                          "İlkay Gündoğan",
    "Jadon Malik Sancho":                      "Jadon Sancho",
    "João Félix Sequeira":                     "João Félix",
    "Héctor Bellerín Moruno":                  "Héctor Bellerín",
    "Cristiano Ronaldo dos Santos Aveiro":     "Cristiano Ronaldo",
    # ── World Cup ──────────────────────────────────────────────────────────────
    "Steven Nzonzi":                           "Steven N'Zonzi",
    "Mattéo Guendouzi Olié":                   "Mattéo Guendouzi",
    # ── Prénoms composés / difficiles à lire ──────────────────────────────
    "Dayotchanculle Upamecano":                "D. Upamecano",
    "Dayot Upamecano":                         "D. Upamecano",
    "Dayotchanculle Wilfried Voho Upamecano":  "D. Upamecano",
    "Aurélien Tchouaméni":                     "Tchouaméni",
    "Aurélien Djani Tchouaméni":               "Tchouaméni",
    "Jules Koundé":                            "J. Koundé",
    "Théo Bernard François Hernández":         "Théo Hernández",
    "Randal Kolo Muani":                       "R. Kolo Muani",
    "Eduardo Camavinga":                       "Camavinga",
    "Khéphren Thuram-Ulien":                   "K. Thuram",
    "Marcus Thuram":                           "M. Thuram",
    "William Saliba":                          "W. Saliba",
    "Ibrahima Konaté":                         "I. Konaté",
    "Youssouf Fofana":                         "Y. Fofana",
    "Gonçalo Matias Ramos":                    "G. Ramos",
    "Diogo Luís Santo Jota":                   "Diogo Jota",
    "Rafael Leão":                             "R. Leão",
    "Bernardo Mota Veiga de Carvalho e Silva": "Bernardo Silva",
    "Rúben Santos Gato Alves Dias":            "Rúben Dias",
    "Nuno Filipe Rodrigues Mendes":            "Nuno Mendes",
    "João Pedro Cavaco Cancelo":               "J. Cancelo",
    "Alejandro Balde Losano":                  "A. Balde",
    "Ferran Torres García":                    "F. Torres",
    "Niclas Füllkrug":                         "N. Füllkrug",
    "Jamal Musiala":                           "J. Musiala",
    "Jude Bellingham":                         "J. Bellingham",
    "Bukayo Saka":                             "B. Saka",
    "Erling Braut Haaland":                    "E. Haaland",
}

# Règles de fallback intelligentes pour les noms non mappés
_KNOWN_LAST_NAMES = {
    # Prénoms composés courants à garder ensemble
    "ter", "van", "de", "da", "do", "dos", "du", "le", "la", "von", "el",
    "den", "der", "al", "ben", "bel", "mac", "mc", "i", "y", "af", "av",
}

def clean_name(full_name: str) -> str:
    """Retourne le NOM DE FAMILLE uniquement pour l'affichage sur le terrain.
    
    Priorité :
    1. Dictionnaire explicite → valeur mappée (déjà courte)
    2. Fallback : dernier mot significatif (nom de famille)
    """
    if not isinstance(full_name, str):
        return str(full_name)
    if full_name in PLAYER_NAME_MAP:
        return PLAYER_NAME_MAP[full_name]
    parts = full_name.strip().split()
    if len(parts) == 1:
        return full_name
    # Pour 2 mots : retourner directement le dernier (nom de famille)
    if len(parts) == 2:
        return parts[-1]
    # Pour 3+ mots : dernier mot non-particule = nom de famille
    for candidate in reversed(parts):
        if candidate.lower() not in _KNOWN_LAST_NAMES:
            return candidate
    return parts[-1]




# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pass Network & Team Structure",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600&family=DM+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }

.stApp { background-color: #0a0e1a; color: #e8eaf0; }

.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 14px 10px;
    text-align: center;
    transition: border-color 0.2s;
    height: 110px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-sizing: border-box;
}
.metric-card:hover { border-color: #4fd1c5; }
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: #4fd1c5;
    line-height: 1;
    white-space: nowrap;
}
.metric-sub {
    font-size: 11px;
    color: #718096;
    margin-top: 4px;
}

.section-header {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #4fd1c5;
    text-transform: uppercase;
    letter-spacing: 3px;
    border-bottom: 1px solid #2d3748;
    padding-bottom: 8px;
    margin: 28px 0 16px 0;
}

.player-card {
    background: #111827;
    border: 1px solid #2d3748;
    border-left: 3px solid #4fd1c5;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
}
.player-name { color: #e8eaf0; font-weight: 700; font-size: 13px; margin-bottom: 4px; }
.player-stat { color: #718096; }
.player-stat span { color: #4fd1c5; font-weight: 700; }

.badge {
    display: inline-block;
    background: #1a2235;
    border: 1px solid #4fd1c5;
    color: #4fd1c5;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 4px;
    margin: 2px;
}

div[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #2d3748;
}
div[data-testid="stSidebar"] .stSelectbox label,
div[data-testid="stSidebar"] .stRadio label { color: #a0aec0; font-size: 12px; }

.stSelectbox > div > div { background: #111827; border-color: #2d3748; color: #e8eaf0; }
.stRadio > div { gap: 8px; }

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 36px;
    font-weight: 800;
    color: #e8eaf0;
    line-height: 1.1;
    margin-bottom: 4px;
}
.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: #4fd1c5;
    letter-spacing: 2px;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


# ─── DATA LOADING ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def load_competitions():
    return sb.competitions()

@st.cache_data(ttl=3600, show_spinner=False)
def load_matches(competition_id, season_id):
    return sb.matches(competition_id=competition_id, season_id=season_id)

@st.cache_data(ttl=3600, show_spinner=False)
def load_events(match_id):
    return sb.events(match_id=match_id)

@st.cache_data(ttl=3600, show_spinner=False)
def load_lineups(match_id):
    return sb.lineups(match_id=match_id)


# ─── COMPUTATION HELPERS ──────────────────────────────────────────────────────

def get_player_positions(lineups, team_name):
    """Extract starting XI with their first listed position."""
    df = lineups[team_name].copy()
    result = []
    for _, row in df.iterrows():
        if row['positions']:
            pos = row['positions'][0]['position']
            from_period = row['positions'][0]['from_period']
            result.append({
                'player': row['player_name'],
                'nickname': row['player_nickname'] or row['player_name'].split()[-1],
                'position': pos,
                'jersey': row['jersey_number'],
                'start_period': from_period,
            })
    return pd.DataFrame(result)


def build_pass_network(events, team, period_filter='Full Match'):
    """Build pass network dataframe: nodes (avg positions) + edges (pass counts)."""
    passes = events[
        (events['type'] == 'Pass') &
        (events['team'] == team) &
        (events['pass_outcome'].isna())  # completed passes only
    ].copy()

    # Period filter
    if period_filter == '1st Half':
        passes = passes[passes['period'] == 1]
    elif period_filter == '2nd Half':
        passes = passes[passes['period'] == 2]

    if passes.empty:
        return pd.DataFrame(), pd.DataFrame()

    passes['x'] = passes['location'].apply(lambda l: l[0] if isinstance(l, list) else np.nan)
    passes['y'] = passes['location'].apply(lambda l: l[1] if isinstance(l, list) else np.nan)
    passes['end_x'] = passes['pass_end_location'].apply(lambda l: l[0] if isinstance(l, list) else np.nan)
    passes['end_y'] = passes['pass_end_location'].apply(lambda l: l[1] if isinstance(l, list) else np.nan)

    passes = passes.dropna(subset=['x', 'y', 'end_x', 'end_y', 'pass_recipient'])

    # Get starting XI (players on pitch from period 1)
    players_first = passes[passes['period'] == 1]['player'].value_counts()
    starting_xi = players_first[players_first >= 1].index.tolist()[:11]

    # Average positions (nodes)
    nodes = passes[passes['player'].isin(starting_xi)].groupby('player').agg(
        avg_x=('x', 'mean'),
        avg_y=('y', 'mean'),
        pass_count=('x', 'count')
    ).reset_index()

    # Pass pairs (edges)
    pair_passes = passes[
        passes['player'].isin(starting_xi) &
        passes['pass_recipient'].isin(starting_xi)
    ].copy()

    edges = pair_passes.groupby(['player', 'pass_recipient']).size().reset_index(name='count')
    edges = edges[edges['count'] >= 2]  # minimum threshold

    return nodes, edges


def compute_network_metrics(nodes, edges):
    """Compute graph centrality metrics."""
    if nodes.empty or edges.empty:
        return nodes

    G = nx.DiGraph()
    for _, row in nodes.iterrows():
        G.add_node(row['player'])
    for _, row in edges.iterrows():
        G.add_edge(row['player'], row['pass_recipient'], weight=row['count'])

    betweenness = nx.betweenness_centrality(G, weight='weight', normalized=True)
    in_degree = dict(G.in_degree(weight='weight'))
    out_degree = dict(G.out_degree(weight='weight'))

    nodes = nodes.copy()
    nodes['betweenness'] = nodes['player'].map(betweenness).fillna(0)
    nodes['in_degree'] = nodes['player'].map(in_degree).fillna(0)
    nodes['out_degree'] = nodes['player'].map(out_degree).fillna(0)
    nodes['total_degree'] = nodes['in_degree'] + nodes['out_degree']
    return nodes


def compute_team_metrics(nodes, edges):
    """High-level team structure metrics."""
    if nodes.empty or edges.empty:
        return {}

    G = nx.DiGraph()
    for _, row in nodes.iterrows():
        G.add_node(row['player'])
    for _, row in edges.iterrows():
        G.add_edge(row['player'], row['pass_recipient'], weight=row['count'])

    # Density = actual edges / possible edges
    n = len(G.nodes)
    density = nx.density(G) if n > 1 else 0

    # Avg clustering
    G_undirected = G.to_undirected()
    clustering = nx.average_clustering(G_undirected) if n > 1 else 0

    # Centralization (how concentrated passing is on one node)
    bc = list(nx.betweenness_centrality(G, normalized=True).values())
    max_bc = max(bc) if bc else 0
    centralization = sum(max_bc - v for v in bc) / (n - 1) if n > 1 else 0

    # avg pass count per edge
    avg_passes = edges['count'].mean() if len(edges) else 0
    total_passes = nodes['pass_count'].sum()

    return {
        'density': round(density, 3),
        'clustering': round(clustering, 3),
        'centralization': round(centralization * 100, 1),
        'avg_link_passes': round(avg_passes, 1),
        'total_passes': int(total_passes),
        'connections': len(edges),
    }


# ─── PLOTTING ─────────────────────────────────────────────────────────────────

DARK_BG = '#0a0e1a'
PITCH_LINE = '#2d3748'
ACCENT = '#4fd1c5'
ACCENT2 = '#f6ad55'
NODE_COLOR = '#4fd1c5'
EDGE_COLOR = '#4fd1c5'


def plot_pass_network(nodes, edges, team_name, period_label, title_suffix=''):
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=DARK_BG,
        line_color=PITCH_LINE,
        linewidth=1.5,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(12, 8))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    if nodes.empty or edges.empty:
        ax.text(60, 40, 'Insufficient data', color='white',
                fontsize=14, ha='center', va='center')
        return fig

    max_passes = nodes['pass_count'].max()
    max_edge = edges['count'].max()

    # Draw edges
    for _, edge in edges.iterrows():
        from_node = nodes[nodes['player'] == edge['player']]
        to_node = nodes[nodes['player'] == edge['pass_recipient']]
        if from_node.empty or to_node.empty:
            continue
        x_start, y_start = from_node.iloc[0]['avg_x'], from_node.iloc[0]['avg_y']
        x_end, y_end = to_node.iloc[0]['avg_x'], to_node.iloc[0]['avg_y']

        alpha = 0.15 + 0.6 * (edge['count'] / max_edge)
        lw = 0.5 + 4.5 * (edge['count'] / max_edge)
        ax.annotate('', xy=(x_end, y_end), xytext=(x_start, y_start),
                    arrowprops=dict(
                        arrowstyle='->', color=to_rgba(ACCENT, alpha),
                        lw=lw, connectionstyle='arc3,rad=0.05'
                    ))

    from matplotlib.patheffects import withStroke

    # ── Couche 1 : cercles (zorder=5)
    for _, node in nodes.iterrows():
        size = 800 + 2200 * (node['pass_count'] / max_passes)
        ax.scatter(node['avg_x'], node['avg_y'],
                   s=size, c=ACCENT, zorder=5, alpha=0.92,
                   linewidths=2.5, edgecolors='white')

    # ── Couche 2 : chiffres de passes (zorder=6)
    for _, node in nodes.iterrows():
        ax.text(node['avg_x'], node['avg_y'], str(int(node['pass_count'])),
                color='white', fontsize=8.5, fontweight='bold',
                ha='center', va='center', zorder=6,
                fontfamily='DejaVu Sans',
                path_effects=[withStroke(linewidth=2.5, foreground='#0a0e1a')])

    # ── Couche 3 : labels noms — placement avec anti-collision
    # Ordre rendu : cercles(5) → chiffres(6) → labels(10)
    # Règles :
    #   - Départ : juste au-dessus du cercle propre
    #   - Interdit : chevaucher le chiffre d'un autre node
    #   - Interdit : chevaucher un autre label
    #   - Toujours au plus proche du cercle propre
    import math as _math

    LABEL_W = 8.5    # largeur approx (noms courts = nom de famille)
    LABEL_H = 2.6
    GAP     = 0.4    # gap entre bord cercle et label

    def _r(pc):
        return ((800 + 2200 * (pc / max_passes)) ** 0.5) * 0.068

    nlist = [{'p': nd['player'], 'nx': nd['avg_x'],
              'ny': nd['avg_y'], 'r': _r(nd['pass_count'])}
             for _, nd in nodes.iterrows()]

    # Position initiale : centré au-dessus du cercle
    lpos = {n['p']: [n['nx'], n['ny'] - n['r'] - GAP - LABEL_H * 0.5]
            for n in nlist}

    # Répulsion en 2 passes, 100 itérations
    for iteration in range(100):
        moved = False
        for ni in nlist:
            p = ni['p']
            lx, ly = lpos[p]

            # Règle A : ne pas couvrir le CHIFFRE (centre) des autres nodes
            for nj in nlist:
                if nj['p'] == p:
                    continue
                dx = lx - nj['nx']
                dy = ly - nj['ny']
                zone = nj['r'] + 0.5
                dist = _math.sqrt(dx*dx + dy*dy) or 0.001
                if dist < zone:
                    push = (zone - dist + 0.2) / dist
                    lpos[p][0] += dx * push * 0.6
                    lpos[p][1] += dy * push * 0.6
                    lx, ly = lpos[p]
                    moved = True

            # Règle B : ne pas chevaucher les autres LABELS
            for nj in nlist:
                if nj['p'] == p:
                    continue
                lx2, ly2 = lpos[nj['p']]
                ox = LABEL_W   - abs(lx - lx2)
                oy = LABEL_H + 0.2 - abs(ly - ly2)
                if ox > 0 and oy > 0:
                    if oy <= ox:
                        sh = (oy * 0.5 + 0.15) * (1 if ly >= ly2 else -1)
                        lpos[p][1] += sh; ly += sh
                    else:
                        sh = (ox * 0.5 + 0.15) * (1 if lx >= lx2 else -1)
                        lpos[p][0] += sh; lx += sh
                    moved = True

        if not moved:
            break

    # Dessiner dans l'ordre : cercles, chiffres, labels
    for ni in nlist:
        p = ni['p']
        size = 800 + 2200 * (ni['r'] / max(_r(nd['pass_count']) for _, nd in nodes.iterrows()))
        ax.scatter(ni['nx'], ni['ny'],
                   s=800 + 2200 * (nodes[nodes['player']==p]['pass_count'].values[0] / max_passes),
                   c=ACCENT, zorder=5, alpha=0.92,
                   linewidths=2.5, edgecolors='white')

    from matplotlib.patheffects import withStroke
    for ni in nlist:
        p = ni['p']
        pc = nodes[nodes['player']==p]['pass_count'].values[0]
        ax.text(ni['nx'], ni['ny'], str(int(pc)),
                color='white', fontsize=8.5, fontweight='bold',
                ha='center', va='center', zorder=6,
                fontfamily='DejaVu Sans',
                path_effects=[withStroke(linewidth=2.5, foreground='#0a0e1a')])

    for ni in nlist:
        p     = ni['p']
        short = clean_name(p)
        lx    = max(1.0, min(119.0, lpos[p][0]))
        ly    = max(1.0, min(79.0,  lpos[p][1]))
        ax.text(lx, ly, short,
                color='#ffffff', fontsize=7.5, fontweight='bold',
                ha='center', va='center', zorder=10,
                fontfamily='DejaVu Sans',
                bbox=dict(boxstyle='square,pad=0.22', facecolor='#0d1117',
                          alpha=0.92, edgecolor='#4a5568', linewidth=0.5))

    plt.tight_layout()
    return fig


def plot_heatmap(events, team_name, period_filter='Full Match'):
    """Average position heatmap for the team."""
    passes = events[(events['type'] == 'Pass') & (events['team'] == team_name)].copy()
    if period_filter == '1st Half':
        passes = passes[passes['period'] == 1]
    elif period_filter == '2nd Half':
        passes = passes[passes['period'] == 2]

    passes['x'] = passes['location'].apply(lambda l: l[0] if isinstance(l, list) else np.nan)
    passes['y'] = passes['location'].apply(lambda l: l[1] if isinstance(l, list) else np.nan)
    passes = passes.dropna(subset=['x', 'y'])

    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color=DARK_BG,
        line_color=PITCH_LINE,
        linewidth=1.5,
    )
    fig, ax = pitch.draw(figsize=(12, 8))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    if not passes.empty:
        pitch.kdeplot(passes['x'], passes['y'], ax=ax,
                     cmap='YlOrRd', fill=True, levels=100,
                     alpha=0.75, bw_adjust=0.7)

    ax.set_title(f'{team_name}  |  Passing Heatmap  |  {period_filter}',
                 color='white', fontsize=13, fontweight='bold',
                 pad=14, fontfamily='DejaVu Sans')
    plt.tight_layout()
    return fig


def plot_centrality_bar(nodes, team_name):
    """Horizontal bar chart of betweenness centrality."""
    if nodes.empty or 'betweenness' not in nodes.columns:
        return None

    df = nodes.sort_values('betweenness', ascending=True).tail(11)
    df['short'] = df['player'].apply(clean_name)

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    colors = [ACCENT if v == df['betweenness'].max() else '#2d4a5a' for v in df['betweenness']]
    bars = ax.barh(df['short'], df['betweenness'], color=colors, height=0.6)

    for bar, val in zip(bars, df['betweenness']):
        ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height() / 2,
                f'{val:.3f}', va='center', color='#a0aec0', fontsize=9,
                fontfamily='DejaVu Sans')

    ax.set_xlabel('Betweenness Centrality', color='#718096', fontsize=10)
    ax.set_title(f'{team_name} — Passing Centrality', color='white',
                 fontsize=12, fontweight='bold', fontfamily='DejaVu Sans')
    ax.tick_params(colors='#a0aec0', labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('#2d3748')
    ax.xaxis.label.set_color('#718096')
    plt.tight_layout()
    return fig


def plot_comparison(metrics1, metrics2, team1, team2):
    """Radar-style comparison of team metrics."""
    labels = ['Density', 'Clustering', 'Centralization\n(inverted)', 'Avg Link\nPasses', 'Connections']
    
    def normalize(metrics):
        return [
            metrics.get('density', 0) * 10,  # scale to ~0-1
            metrics.get('clustering', 0),
            1 - metrics.get('centralization', 0) / 100,  # invert: lower = more distributed
            min(metrics.get('avg_link_passes', 0) / 20, 1),
            min(metrics.get('connections', 0) / 60, 1),
        ]

    v1 = normalize(metrics1)
    v2 = normalize(metrics2)

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    b1 = ax.bar(x - width / 2, v1, width, label=team1, color=ACCENT, alpha=0.85)
    b2 = ax.bar(x + width / 2, v2, width, label=team2, color=ACCENT2, alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color='#a0aec0', fontsize=9)
    ax.set_ylabel('Normalized Score', color='#718096', fontsize=10)
    ax.set_title('Team Structure Comparison', color='white',
                 fontsize=13, fontweight='bold', fontfamily='DejaVu Sans')
    ax.legend(facecolor='#111827', edgecolor='#2d3748', labelcolor='white', fontsize=10)
    ax.tick_params(colors='#718096')
    for spine in ax.spines.values():
        spine.set_color('#2d3748')
    ax.yaxis.label.set_color('#718096')

    plt.tight_layout()
    return fig


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding: 16px 0 20px 0;'>
        <div style='font-family: Syne, sans-serif; font-size: 18px; font-weight: 800; color: #e8eaf0;'>
            ⚽ Pass Network
        </div>
        <div style='font-family: 'DM Mono', monospace; font-size: 10px; color: #4fd1c5; 
                    letter-spacing: 2px; text-transform: uppercase; margin-top: 4px;'>
            Team Structure Analysis
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Competition selector
    comps = load_competitions()
    comp_options = {
        f"{r['competition_name']} {r['season_name']}": (r['competition_id'], r['season_id'])
        for _, r in comps.iterrows()
    }
    selected_comp_label = st.selectbox("🏆 Competition", list(comp_options.keys()),
                                        index=list(comp_options.keys()).index('La Liga 2020/2021') if 'La Liga 2020/2021' in comp_options else 0)
    comp_id, season_id = comp_options[selected_comp_label]

    # Match selector
    with st.spinner("Loading matches…"):
        matches = load_matches(comp_id, season_id)

    match_labels = {
        f"J{i+1} — {r['home_team']} {r['home_score']}-{r['away_score']} {r['away_team']}": r['match_id']
        for i, (_, r) in enumerate(matches.iterrows())
    }
    selected_match_label = st.selectbox("📅 Match", list(match_labels.keys()))
    match_id = match_labels[selected_match_label]

    # Period filter
    st.markdown("---")
    period_filter = st.radio("⏱ Période", ['Full Match', '1st Half', '2nd Half'], index=0)

    # Min passes slider for edges
    st.markdown("---")
    min_passes = st.slider("Min. passes per link", min_value=1, max_value=10, value=3)

    st.markdown("---")
    st.markdown("""
    <div style='font-family: 'DM Mono', monospace; font-size: 10px; color: #4a5568; line-height: 1.8;'>
        Data: StatsBomb Open Data<br>
        Built by Julie Landrevie<br>
        Stack: Python · mplsoccer · NetworkX
    </div>
    """, unsafe_allow_html=True)


# ─── LOAD DATA ────────────────────────────────────────────────────────────────

with st.spinner("Loading events…"):
    events = load_events(match_id)
    lineups = load_lineups(match_id)

teams = events['team'].unique().tolist()
team1 = teams[0]
team2 = teams[1]

# Build networks
nodes1, edges1 = build_pass_network(events, team1, period_filter)
edges1 = edges1[edges1['count'] >= min_passes] if not edges1.empty else edges1
nodes1 = compute_network_metrics(nodes1, edges1)
metrics1 = compute_team_metrics(nodes1, edges1)

nodes2, edges2 = build_pass_network(events, team2, period_filter)
edges2 = edges2[edges2['count'] >= min_passes] if not edges2.empty else edges2
nodes2 = compute_network_metrics(nodes2, edges2)
metrics2 = compute_team_metrics(nodes2, edges2)


# ─── HEADER ───────────────────────────────────────────────────────────────────

match_row = matches[matches['match_id'] == match_id].iloc[0]
home, away = match_row['home_team'], match_row['away_team']
score = f"{match_row['home_score']} – {match_row['away_score']}"

st.markdown(f"""
<div style='display: flex; align-items: center; justify-content: space-between; 
            border-bottom: 1px solid #2d3748; padding-bottom: 20px; margin-bottom: 24px;'>
    <div>
        <div class="hero-title">Pass Network<br>& Team Structure</div>
        <div class="hero-sub" style='margin-top: 8px;'>StatsBomb Open Data · {selected_comp_label}</div>
    </div>
    <div style='text-align: right; font-family: Syne, sans-serif;'>
        <div style='font-size: 14px; color: #718096; font-weight: 600;'>{home}</div>
        <div style='font-size: 42px; font-weight: 800; color: #4fd1c5; line-height: 1;'>{score}</div>
        <div style='font-size: 14px; color: #718096; font-weight: 600;'>{away}</div>
        <div style='font-family: 'DM Mono', monospace; font-size: 11px; color: #4a5568; margin-top: 6px;'>
            {period_filter}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─── TEAM METRICS CARDS ───────────────────────────────────────────────────────

st.markdown('<div class="section-header">📊 Structure Metrics</div>', unsafe_allow_html=True)

def metric_card(label, value, sub=''):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {'<div class="metric-sub">'+sub+'</div>' if sub else ''}
    </div>
    """

col_t1, col_sep, col_t2 = st.columns([5, 1, 5])

with col_t1:
    st.markdown(f"<div style='font-family: 'DM Mono', monospace;font-size:12px;color:#4fd1c5;text-align:center;font-weight:700;margin-bottom:12px;'>{team1}</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(metric_card('Total Passes', metrics1.get('total_passes', '—')), unsafe_allow_html=True)
    with c2: st.markdown(metric_card('Connections', metrics1.get('connections', '—')), unsafe_allow_html=True)
    with c3: st.markdown(metric_card('Density', f"{metrics1.get('density', 0):.2f}"), unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4: st.markdown(metric_card('Clustering', f"{metrics1.get('clustering', 0):.2f}"), unsafe_allow_html=True)
    with c5: st.markdown(metric_card('Centralization', f"{metrics1.get('centralization', 0):.1f}%"), unsafe_allow_html=True)
    with c6: st.markdown(metric_card('Passes/Link', f"{metrics1.get('avg_link_passes', 0):.1f}"), unsafe_allow_html=True)

with col_sep:
    st.markdown("<div style='border-left:1px solid #2d3748;height:120px;margin:auto;width:1px;margin-top:30px;'></div>", unsafe_allow_html=True)

with col_t2:
    st.markdown(f"<div style='font-family: 'DM Mono', monospace;font-size:12px;color:#f6ad55;text-align:center;font-weight:700;margin-bottom:12px;'>{team2}</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(metric_card('Total Passes', metrics2.get('total_passes', '—')).replace('#4fd1c5', '#f6ad55'), unsafe_allow_html=True)
    with c2: st.markdown(metric_card('Connections', metrics2.get('connections', '—')).replace('#4fd1c5', '#f6ad55'), unsafe_allow_html=True)
    with c3: st.markdown(metric_card('Density', f"{metrics2.get('density', 0):.2f}").replace('#4fd1c5', '#f6ad55'), unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4: st.markdown(metric_card('Clustering', f"{metrics2.get('clustering', 0):.2f}").replace('#4fd1c5', '#f6ad55'), unsafe_allow_html=True)
    with c5: st.markdown(metric_card('Centralization', f"{metrics2.get('centralization', 0):.1f}%").replace('#4fd1c5', '#f6ad55'), unsafe_allow_html=True)
    with c6: st.markdown(metric_card('Passes/Link', f"{metrics2.get('avg_link_passes', 0):.1f}").replace('#4fd1c5', '#f6ad55'), unsafe_allow_html=True)


# ─── TABS ─────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "🕸️ Pass Networks", "🌡️ Heatmaps", "📈 Centrality", "⚔️ Comparison"
])


# TAB 1 — PASS NETWORKS
with tab1:
    st.markdown('<div class="section-header">🕸️ Pass Networks — Completed passes only</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        fig1 = plot_pass_network(nodes1, edges1, team1, period_filter)
        st.pyplot(fig1, use_container_width=True)
        plt.close()
    with col_b:
        fig2 = plot_pass_network(nodes2, edges2, team2, period_filter)
        st.pyplot(fig2, use_container_width=True)
        plt.close()

    # Top passeurs
    st.markdown('<div class="section-header">🔝 Key Players</div>', unsafe_allow_html=True)
    colp1, colp2 = st.columns(2)

    def top_players_html(nodes, accent):
        if nodes.empty:
            return "<div style='color:#718096'>Insufficient data</div>"
        top = nodes.sort_values('pass_count', ascending=False).head(5)
        html = ""
        for _, r in top.iterrows():
            bc = r.get('betweenness', 0)
            html += f"""
            <div class="player-card" style="border-left-color:{accent}">
                <div class="player-name">{clean_name(r['player'])}</div>
                <div class="player-stat">Passes: <span style="color:{accent}">{int(r['pass_count'])}</span>
                    &nbsp;|&nbsp; Centralité : <span style="color:{accent}">{bc:.3f}</span></div>
            </div>
            """
        return html

    with colp1:
        st.markdown(f"<div style='font-family:Space Mono;font-size:11px;color:#4fd1c5;margin-bottom:10px;'>{team1}</div>", unsafe_allow_html=True)
        st.markdown(top_players_html(nodes1, '#4fd1c5'), unsafe_allow_html=True)
    with colp2:
        st.markdown(f"<div style='font-family:Space Mono;font-size:11px;color:#f6ad55;margin-bottom:10px;'>{team2}</div>", unsafe_allow_html=True)
        st.markdown(top_players_html(nodes2, '#f6ad55'), unsafe_allow_html=True)


# TAB 2 — HEATMAPS
with tab2:
    st.markdown('<div class="section-header">🌡️ Passing Position Heatmaps</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        fig3 = plot_heatmap(events, team1, period_filter)
        st.pyplot(fig3, use_container_width=True)
        plt.close()
    with col_b:
        fig4 = plot_heatmap(events, team2, period_filter)
        st.pyplot(fig4, use_container_width=True)
        plt.close()

    st.info("💡 **Lecture** : Les zones chaudes montrent où l'équipe initie ses passes. Concentration haute = jeu direct ; concentration médiane = build-up prudent.")


# TAB 3 — CENTRALITY
with tab3:
    st.markdown('<div class="section-header">📈 Centrality Analysis — Betweenness</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        fig5 = plot_centrality_bar(nodes1, team1)
        if fig5:
            st.pyplot(fig5, use_container_width=True)
            plt.close()
    with col_b:
        fig6 = plot_centrality_bar(nodes2, team2)
        if fig6:
            st.pyplot(fig6, use_container_width=True)
            plt.close()

    st.markdown('<div class="section-header">📋 Player Metrics Detail</div>', unsafe_allow_html=True)

    def player_metrics_table(nodes, team_name, accent):
        if nodes.empty:
            return
        st.markdown(f"<div style='font-family:Space Mono;font-size:11px;color:{accent};margin-bottom:8px;font-weight:700;'>{team_name}</div>", unsafe_allow_html=True)
        display = nodes[['player', 'pass_count', 'betweenness', 'in_degree', 'out_degree']].copy()
        display['player'] = display['player'].apply(clean_name)
        display.columns = ['Player', 'Passes', 'Betweenness', 'Passes Received', 'Passes Made']
        display = display.sort_values('Passes', ascending=False)
        display['Betweenness'] = display['Betweenness'].round(3)
        display['Passes Received'] = display['Passes Received'].round(0).astype(int)
        display['Passes Made'] = display['Passes Made'].round(0).astype(int)
        st.dataframe(display.reset_index(drop=True), use_container_width=True, height=300)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        player_metrics_table(nodes1, team1, '#4fd1c5')
    with col_t2:
        player_metrics_table(nodes2, team2, '#f6ad55')

    st.info("💡 **Betweenness centrality** : mesure combien de fois un joueur est sur le chemin de passe le plus court entre deux coéquipiers. Score élevé = pivot tactique clé.")


# TAB 4 — COMPARISON
with tab4:
    st.markdown('<div class="section-header">⚔️ Team Structure Comparison</div>', unsafe_allow_html=True)

    fig7 = plot_comparison(metrics1, metrics2, team1, team2)
    st.pyplot(fig7, use_container_width=True)
    plt.close()

    st.markdown('<div class="section-header">📖 Tactical Interpretation</div>', unsafe_allow_html=True)

    # Auto-generated tactical interpretation
    insights = []

    d1, d2 = metrics1.get('density', 0), metrics2.get('density', 0)
    if abs(d1 - d2) > 0.05:
        more = team1 if d1 > d2 else team2
        insights.append(f"**Density** : {more} présente un réseau plus dense — davantage d'options et de connexions entre joueurs.")

    c1, c2 = metrics1.get('clustering', 0), metrics2.get('clustering', 0)
    if abs(c1 - c2) > 0.05:
        more = team1 if c1 > c2 else team2
        insights.append(f"**Clustering** : {more} joue davantage en triangles serrés — jeu de possession structuré.")

    ce1, ce2 = metrics1.get('centralization', 0), metrics2.get('centralization', 0)
    if abs(ce1 - ce2) > 5:
        more = team1 if ce1 > ce2 else team2
        less = team2 if ce1 > ce2 else team1
        insights.append(f"**Centralization** : {more} dépend davantage d'un ou deux relayeurs clés, tandis que {less} distribue le jeu plus équitablement.")

    ap1, ap2 = metrics1.get('avg_link_passes', 0), metrics2.get('avg_link_passes', 0)
    if abs(ap1 - ap2) > 2:
        more = team1 if ap1 > ap2 else team2
        insights.append(f"**Links** : {more} utilise ses connexions plus intensément — davantage de passes par paire de joueurs.")

    if not insights:
        insights = ["Les deux équipes présentent des structures de jeu similaires sur ce match."]

    for insight in insights:
        st.markdown(f"""
        <div style='background:#111827;border:1px solid #2d3748;border-left:3px solid #4fd1c5;
                    border-radius:8px;padding:14px 16px;margin-bottom:10px;
                    font-family: 'Inter', sans-serif;font-size:14px;color:#cbd5e0;line-height:1.6;'>
            {insight}
        </div>
        """, unsafe_allow_html=True)

    # Full metrics table comparison
    st.markdown('<div class="section-header">📊 Full Comparison Table</div>', unsafe_allow_html=True)
    comp_df = pd.DataFrame({
        'Metric': ['Total Passes', 'Active Connections', 'Density', 'Avg Clustering', 'Centralization (%)', 'Avg Passes/Link'],
        team1: [
            metrics1.get('total_passes', '—'), metrics1.get('connections', '—'),
            f"{metrics1.get('density', 0):.3f}", f"{metrics1.get('clustering', 0):.3f}",
            f"{metrics1.get('centralization', 0):.1f}%", f"{metrics1.get('avg_link_passes', 0):.1f}",
        ],
        team2: [
            metrics2.get('total_passes', '—'), metrics2.get('connections', '—'),
            f"{metrics2.get('density', 0):.3f}", f"{metrics2.get('clustering', 0):.3f}",
            f"{metrics2.get('centralization', 0):.1f}%", f"{metrics2.get('avg_link_passes', 0):.1f}",
        ],
    })
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
