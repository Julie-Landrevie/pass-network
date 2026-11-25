"""
Pass Network & Team Structure — Julie Landrevie (français / anglais, clair / sombre)
Sources : StatsBomb Open Data. Charte commune : jl_ui.py et .streamlit/config.toml.
"""
import math
import warnings

import streamlit as st

warnings.filterwarnings("ignore")

from jl_ui import C, footer, fr_num, header, is_dark, kpi, mpl_style, note, pitch_kwargs, setup, t  # noqa: E402

setup("Pass Network — Julie Landrevie", "Pass Network — Julie Landrevie", icon="⚽")

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, to_rgba  # noqa: E402
from matplotlib.patheffects import withStroke  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
from mplsoccer import Pitch  # noqa: E402
from statsbombpy import sb  # noqa: E402

mpl_style()
# Couleurs des équipes, les mêmes dans toutes les sections : domicile vert d'eau, extérieur rouille
HOME_COLOR = C["teal"]
AWAY_COLOR = C["rust"]
PERIODS = {"Full Match": ("Match entier", "Full match"),
           "1st Half": ("1re mi-temps", "1st half"),
           "2nd Half": ("2e mi-temps", "2nd half")}


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

# ─── GRAPHIQUES (couleurs du thème affiché, clair ou sombre) ───

def _dark(color, k=0.55):
    r, g, b, _ = to_rgba(color)
    return (r * k, g * k, b * k, 1)


def _light(color, k=0.45):
    r, g, b, _ = to_rgba(color)
    return (r + (1 - r) * k, g + (1 - g) * k, b + (1 - b) * k)


def plot_pass_network(nodes, edges, color=HOME_COLOR):
    pitch = Pitch(pitch_type='statsbomb', corner_arcs=True, **pitch_kwargs(linewidth=1.5))
    fig, ax = pitch.draw(figsize=(12, 8))

    if nodes.empty or edges.empty:
        ax.text(60, 40, t("Données insuffisantes", "Insufficient data"), color=C["ink2"],
                fontsize=14, ha='center', va='center')
        return fig

    max_passes = nodes['pass_count'].max()
    max_edge = edges['count'].max()

    # Liens : épaisseur et opacité proportionnelles au nombre de passes
    for _, edge in edges.iterrows():
        from_node = nodes[nodes['player'] == edge['player']]
        to_node = nodes[nodes['player'] == edge['pass_recipient']]
        if from_node.empty or to_node.empty:
            continue
        x_start, y_start = from_node.iloc[0]['avg_x'], from_node.iloc[0]['avg_y']
        x_end, y_end = to_node.iloc[0]['avg_x'], to_node.iloc[0]['avg_y']
        alpha = 0.18 + 0.6 * (edge['count'] / max_edge)
        lw = 0.5 + 4.5 * (edge['count'] / max_edge)
        ax.annotate('', xy=(x_end, y_end), xytext=(x_start, y_start),
                    arrowprops=dict(arrowstyle='->', color=to_rgba(color, alpha),
                                    lw=lw, connectionstyle='arc3,rad=0.05'))

    # Cercles (taille = passes réussies), chiffres, puis noms
    for _, node in nodes.iterrows():
        size = 800 + 2200 * (node['pass_count'] / max_passes)
        ax.scatter(node['avg_x'], node['avg_y'], s=size, c=color, zorder=5, alpha=0.95,
                   linewidths=2.5, edgecolors=C["bg"])
    for _, node in nodes.iterrows():
        ax.text(node['avg_x'], node['avg_y'], str(int(node['pass_count'])),
                color='white', fontsize=10, fontweight='bold', ha='center', va='center', zorder=6,
                path_effects=[withStroke(linewidth=2.2, foreground=_dark(color))])

    # Noms : placement anti-collision (au plus près du cercle, sans couvrir chiffres ni autres noms)
    LABEL_W, LABEL_H, GAP = 8.5, 2.6, 0.4

    def _r(pc):
        return ((800 + 2200 * (pc / max_passes)) ** 0.5) * 0.068

    nlist = [{'p': nd['player'], 'nx': nd['avg_x'], 'ny': nd['avg_y'], 'r': _r(nd['pass_count'])}
             for _, nd in nodes.iterrows()]
    lpos = {n['p']: [n['nx'], n['ny'] - n['r'] - GAP - LABEL_H * 0.5] for n in nlist}

    for _ in range(100):
        moved = False
        for ni in nlist:
            p = ni['p']
            lx, ly = lpos[p]
            for nj in nlist:
                if nj['p'] == p:
                    continue
                dx, dy = lx - nj['nx'], ly - nj['ny']
                zone = nj['r'] + 0.5
                dist = math.sqrt(dx * dx + dy * dy) or 0.001
                if dist < zone:
                    push = (zone - dist + 0.2) / dist
                    lpos[p][0] += dx * push * 0.6
                    lpos[p][1] += dy * push * 0.6
                    lx, ly = lpos[p]
                    moved = True
            for nj in nlist:
                if nj['p'] == p:
                    continue
                lx2, ly2 = lpos[nj['p']]
                ox = LABEL_W - abs(lx - lx2)
                oy = LABEL_H + 0.2 - abs(ly - ly2)
                if ox > 0 and oy > 0:
                    if oy <= ox:
                        sh = (oy * 0.5 + 0.15) * (1 if ly >= ly2 else -1)
                        lpos[p][1] += sh
                        ly += sh
                    else:
                        sh = (ox * 0.5 + 0.15) * (1 if lx >= lx2 else -1)
                        lpos[p][0] += sh
                        lx += sh
                    moved = True
        if not moved:
            break

    for ni in nlist:
        p = ni['p']
        lx = max(1.0, min(119.0, lpos[p][0]))
        ly = max(1.0, min(79.0, lpos[p][1]))
        ax.text(lx, ly, clean_name(p), color=C["ink"], fontsize=9, fontweight='bold',
                ha='center', va='center', zorder=10,
                bbox=dict(boxstyle='square,pad=0.22', facecolor=C["card"], alpha=0.95,
                          edgecolor=C["grid"], linewidth=0.6))

    plt.tight_layout()
    return fig


def plot_heatmap(events, team_name, period_filter='Full Match', color=HOME_COLOR):
    """Zones d'où l'équipe joue ses passes."""
    passes = events[(events['type'] == 'Pass') & (events['team'] == team_name)].copy()
    if period_filter == '1st Half':
        passes = passes[passes['period'] == 1]
    elif period_filter == '2nd Half':
        passes = passes[passes['period'] == 2]
    passes['x'] = passes['location'].apply(lambda l: l[0] if isinstance(l, list) else np.nan)
    passes['y'] = passes['location'].apply(lambda l: l[1] if isinstance(l, list) else np.nan)
    passes = passes.dropna(subset=['x', 'y'])

    pitch = Pitch(pitch_type='statsbomb', line_zorder=2, **pitch_kwargs(linewidth=1.5))
    fig, ax = pitch.draw(figsize=(12, 8))
    if not passes.empty:
        cmap = LinearSegmentedColormap.from_list('team', [C["bg"], to_rgba(color, 0.35), color, _light(color, 0.45) if is_dark() else _dark(color, 0.7)])
        pitch.kdeplot(passes['x'], passes['y'], ax=ax, cmap=cmap, fill=True, levels=100,
                      alpha=0.85, bw_adjust=0.7)
    ax.set_title(f"{team_name} · {t(*PERIODS[period_filter])}", color=C["ink"], fontsize=14, pad=12)
    plt.tight_layout()
    return fig


def plot_centrality_bar(nodes, color=HOME_COLOR):
    """Barres horizontales de centralité d'intermédiarité ; la joueuse pivot est mise en avant."""
    if nodes.empty or 'betweenness' not in nodes.columns:
        return None
    df = nodes.sort_values('betweenness', ascending=True).tail(11).copy()
    df['short'] = df['player'].apply(clean_name)
    fig, ax = plt.subplots(figsize=(9, 5))
    top = df['betweenness'].max()
    colors = [color if v == top else to_rgba(color, 0.35) for v in df['betweenness']]
    bars = ax.barh(df['short'], df['betweenness'], color=colors, height=0.6)
    for bar, val in zip(bars, df['betweenness']):
        ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height() / 2, fr_num(val, 3),
                va='center', color=C["ink"], fontsize=9)
    ax.set_xlabel(t("Centralité d’intermédiarité", "Betweenness centrality"), fontsize=10)
    ax.tick_params(length=0, labelsize=9)
    ax.spines['left'].set_visible(False)
    ax.grid(axis='x', color=C["grid"])
    ax.set_axisbelow(True)
    plt.tight_layout()
    return fig


def plot_comparison(metrics1, metrics2, team1, team2):
    """Indicateurs de structure normalisés, côte à côte."""
    labels = [t("Densité", "Density"), t("Triangles\n(clustering)", "Clustering"),
              t("Répartition\n(centralisation inversée)", "Spread\n(inverted centralization)"),
              t("Passes\npar lien", "Passes\nper link"), t("Liens", "Links")]

    def normalize(m):
        return [m.get('density', 0), m.get('clustering', 0),
                1 - m.get('centralization', 0) / 100,
                min(m.get('avg_link_passes', 0) / 20, 1), min(m.get('connections', 0) / 60, 1)]

    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(x - width / 2, normalize(metrics1), width, label=team1, color=HOME_COLOR)
    ax.bar(x + width / 2, normalize(metrics2), width, label=team2, color=AWAY_COLOR)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel(t("Score normalisé", "Normalized score"), fontsize=10)
    ax.tick_params(length=0)
    ax.spines['left'].set_visible(False)
    ax.grid(axis='y', color=C["grid"])
    ax.set_axisbelow(True)
    ax.set_ylim(0, 1.08)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fr_num(v, 1)))
    ax.legend(fontsize=10, loc='upper center', ncol=2, bbox_to_anchor=(0.5, 1.12))
    plt.tight_layout()
    return fig


def show(fig):
    st.pyplot(fig, width="stretch")
    plt.close(fig)


# ─── BARRE LATÉRALE ───────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"### Pass Network\n{t('Structure collective', 'Team structure')}")

    comps = load_competitions()
    comp_options = {f"{r['competition_name']} {r['season_name']}": (r['competition_id'], r['season_id'])
                    for _, r in comps.iterrows()}
    DEFAULT_COMP = "UEFA Women's Euro 2025"
    comp_keys = list(comp_options.keys())
    selected_comp_label = st.selectbox(t("Compétition", "Competition"), comp_keys,
                                       index=comp_keys.index(DEFAULT_COMP) if DEFAULT_COMP in comp_keys else 0)
    comp_id, season_id = comp_options[selected_comp_label]

    with st.spinner(t("Chargement des matchs…", "Loading matches…")):
        matches = load_matches(comp_id, season_id)

    # Ordre chronologique : le dernier match (la finale d'un tournoi) est proposé par défaut
    matches = matches.sort_values(["match_date", "kick_off"], na_position="first").reset_index(drop=True)
    match_ids = matches['match_id'].tolist()
    match_txt = {r['match_id']: f"{i + 1}. {r['home_team']} {r['home_score']}-{r['away_score']} {r['away_team']}"
                 for i, (_, r) in enumerate(matches.iterrows())}
    match_id = st.selectbox(t("Match", "Match"), match_ids, index=len(match_ids) - 1,
                            format_func=lambda m: match_txt[m])

    period_filter = st.radio(t("Période", "Period"), list(PERIODS), index=0,
                             format_func=lambda k: t(*PERIODS[k]))
    min_passes = st.slider(t("Passes minimum par lien", "Minimum passes per link"),
                           min_value=1, max_value=10, value=3)
    st.caption(t("Données : StatsBomb Open Data · Python, mplsoccer, NetworkX",
                 "Data: StatsBomb Open Data · Python, mplsoccer, NetworkX"))


# ─── DONNÉES DU MATCH ─────────────────────────────────────────────────────────

with st.spinner(t("Chargement des événements…", "Loading events…")):
    events = load_events(match_id)

match_row = matches[matches['match_id'] == match_id].iloc[0]
teams = events['team'].unique().tolist()
team1 = match_row['home_team'] if match_row['home_team'] in teams else teams[0]
team2 = match_row['away_team'] if match_row['away_team'] in teams else [x for x in teams if x != team1][0]

nodes1, edges1 = build_pass_network(events, team1, period_filter)
edges1 = edges1[edges1['count'] >= min_passes] if not edges1.empty else edges1
nodes1 = compute_network_metrics(nodes1, edges1)
metrics1 = compute_team_metrics(nodes1, edges1)

nodes2, edges2 = build_pass_network(events, team2, period_filter)
edges2 = edges2[edges2['count'] >= min_passes] if not edges2.empty else edges2
nodes2 = compute_network_metrics(nodes2, edges2)
metrics2 = compute_team_metrics(nodes2, edges2)


# ─── EN-TÊTE ──────────────────────────────────────────────────────────────────

header(t("Réseau de passes et structure collective", "Pass network and team structure"),
       f"{selected_comp_label} · {t(*PERIODS[period_filter])} · "
       + t("passes réussies des onze titulaires", "completed passes between the starting eleven"))

st.markdown(
    f"""<div style="display:flex;align-items:baseline;gap:1.2rem;flex-wrap:wrap;margin:0.2rem 0 1rem 0;">
<span style="font-size:1.15rem;"><span style="color:{HOME_COLOR};">●</span> <b>{match_row['home_team']}</b></span>
<span style="font-family:'DM Serif Display',Georgia,serif;font-size:2.4rem;line-height:1;">
{match_row['home_score']} – {match_row['away_score']}</span>
<span style="font-size:1.15rem;"><b>{match_row['away_team']}</b> <span style="color:{AWAY_COLOR};">●</span></span>
</div>""", unsafe_allow_html=True)


# ─── INDICATEURS ──────────────────────────────────────────────────────────────

def team_kpis(metrics, team, color):
    st.markdown(f"<span style='color:{color};'>●</span> **{team}**", unsafe_allow_html=True)
    r1 = st.columns(3)
    kpi(r1[0], str(metrics.get('total_passes', '—')), t("Passes réussies", "Completed passes"))
    kpi(r1[1], str(metrics.get('connections', '—')), t("Liens actifs", "Active links"))
    kpi(r1[2], fr_num(metrics.get('density', 0), 2), t("Densité", "Density"))
    st.write("")
    r2 = st.columns(3)
    kpi(r2[0], fr_num(metrics.get('clustering', 0), 2), t("Triangles (clustering)", "Clustering"))
    kpi(r2[1], fr_num(metrics.get('centralization', 0), 1, pct=True), t("Centralisation", "Centralization"))
    kpi(r2[2], fr_num(metrics.get('avg_link_passes', 0), 1), t("Passes par lien", "Passes per link"))


col_t1, col_t2 = st.columns(2, gap="large")
with col_t1:
    team_kpis(metrics1, team1, HOME_COLOR)
with col_t2:
    team_kpis(metrics2, team2, AWAY_COLOR)
st.write("")


# ─── ONGLETS ──────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([t("Réseaux de passes", "Pass networks"), t("Zones de passe", "Passing zones"),
                                  t("Centralité", "Centrality"), t("Comparaison", "Comparison")])

with tab1:
    st.caption(t("Position moyenne de chaque titulaire ; taille du cercle = passes réussies ; "
                 f"un lien = au moins {min_passes} passes entre deux joueuses ou joueurs.",
                 "Average position of each starter; circle size = completed passes; "
                 f"a link = at least {min_passes} passes between two players."))
    col_a, col_b = st.columns(2)
    for col, nodes, edges, team, color in ((col_a, nodes1, edges1, team1, HOME_COLOR),
                                           (col_b, nodes2, edges2, team2, AWAY_COLOR)):
        with col:
            st.markdown(f"<span style='color:{color};'>●</span> **{team}**", unsafe_allow_html=True)
            show(plot_pass_network(nodes, edges, color=color))

    st.subheader(t("Plus gros volumes de passes", "Highest passing volumes"))

    def top_players(nodes):
        if nodes.empty:
            st.caption(t("Données insuffisantes", "Insufficient data"))
            return
        top = nodes.sort_values('pass_count', ascending=False).head(5)
        df = pd.DataFrame({
            t("Joueuse / joueur", "Player"): top['player'].apply(clean_name),
            t("Passes", "Passes"): top['pass_count'].astype(int),
            t("Centralité", "Centrality"): top.get('betweenness', pd.Series(0, index=top.index)).map(lambda v: fr_num(v, 3)),
        })
        st.dataframe(df, hide_index=True, width="stretch")

    colp1, colp2 = st.columns(2)
    with colp1:
        st.markdown(f"<span style='color:{HOME_COLOR};'>●</span> **{team1}**", unsafe_allow_html=True)
        top_players(nodes1)
    with colp2:
        st.markdown(f"<span style='color:{AWAY_COLOR};'>●</span> **{team2}**", unsafe_allow_html=True)
        top_players(nodes2)

with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        show(plot_heatmap(events, team1, period_filter, color=HOME_COLOR))
    with col_b:
        show(plot_heatmap(events, team2, period_filter, color=AWAY_COLOR))
    note(t("<b>Lecture</b> : les zones foncées montrent d’où l’équipe joue ses passes. Concentration haute : jeu plus direct ; "
           "concentration au milieu : construction plus patiente.",
           "<b>How to read it</b>: darker zones show where the team plays its passes from. High concentration: more direct play; "
           "central concentration: more patient build-up."))

with tab3:
    col_a, col_b = st.columns(2)
    for col, nodes, team, color in ((col_a, nodes1, team1, HOME_COLOR), (col_b, nodes2, team2, AWAY_COLOR)):
        with col:
            st.markdown(f"<span style='color:{color};'>●</span> **{team}**", unsafe_allow_html=True)
            fig = plot_centrality_bar(nodes, color=color)
            if fig:
                show(fig)

    st.subheader(t("Détail par joueuse ou joueur", "Player detail"))

    def player_metrics_table(nodes):
        if nodes.empty:
            return
        d = nodes.sort_values('pass_count', ascending=False)
        df = pd.DataFrame({
            t("Joueuse / joueur", "Player"): d['player'].apply(clean_name),
            t("Passes", "Passes"): d['pass_count'].astype(int),
            t("Centralité", "Betweenness"): d['betweenness'].map(lambda v: fr_num(v, 3)),
            t("Passes reçues", "Passes received"): d['in_degree'].round(0).astype(int),
            t("Passes données", "Passes made"): d['out_degree'].round(0).astype(int),
        })
        st.dataframe(df, hide_index=True, width="stretch", height=300)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(f"<span style='color:{HOME_COLOR};'>●</span> **{team1}**", unsafe_allow_html=True)
        player_metrics_table(nodes1)
    with col_t2:
        st.markdown(f"<span style='color:{AWAY_COLOR};'>●</span> **{team2}**", unsafe_allow_html=True)
        player_metrics_table(nodes2)

    note(t("<b>Centralité d’intermédiarité</b> : part des plus courts chemins de passe entre deux coéquipières qui passent "
           "par cette joueuse. Score élevé : pivot du jeu.",
           "<b>Betweenness centrality</b>: share of the shortest passing paths between two teammates that go through this "
           "player. High score: a hub of the team’s play."))

with tab4:
    show(plot_comparison(metrics1, metrics2, team1, team2))

    st.subheader(t("Lecture tactique", "Tactical reading"))
    insights = []
    d1, d2 = metrics1.get('density', 0), metrics2.get('density', 0)
    if abs(d1 - d2) > 0.05:
        more = team1 if d1 > d2 else team2
        insights.append(t(f"<b>Densité</b> : {more} a un réseau plus dense, avec davantage d’options et de liens entre joueuses.",
                          f"<b>Density</b>: {more} has a denser network, with more options and links between players."))
    c1, c2 = metrics1.get('clustering', 0), metrics2.get('clustering', 0)
    if abs(c1 - c2) > 0.05:
        more = team1 if c1 > c2 else team2
        insights.append(t(f"<b>Triangles</b> : {more} joue davantage en triangles serrés, signe d’une possession structurée.",
                          f"<b>Clustering</b>: {more} plays more in tight triangles, a sign of structured possession."))
    ce1, ce2 = metrics1.get('centralization', 0), metrics2.get('centralization', 0)
    if abs(ce1 - ce2) > 5:
        more = team1 if ce1 > ce2 else team2
        less = team2 if ce1 > ce2 else team1
        insights.append(t(f"<b>Centralisation</b> : {more} dépend davantage d’une ou deux relayeuses clés ; {less} répartit le jeu plus équitablement.",
                          f"<b>Centralization</b>: {more} relies more on one or two key relays; {less} spreads the play more evenly."))
    ap1, ap2 = metrics1.get('avg_link_passes', 0), metrics2.get('avg_link_passes', 0)
    if abs(ap1 - ap2) > 2:
        more = team1 if ap1 > ap2 else team2
        insights.append(t(f"<b>Liens</b> : {more} utilise ses liens plus intensément, avec plus de passes par paire.",
                          f"<b>Links</b>: {more} uses its links more intensely, with more passes per pair."))
    if not insights:
        insights = [t("Les deux équipes ont des structures de jeu proches sur ce match.",
                      "Both teams show similar passing structures in this match.")]
    for ins in insights:
        note(ins)

    st.subheader(t("Tableau complet", "Full table"))
    rows = [(t("Passes réussies", "Completed passes"), lambda m: str(m.get('total_passes', '—'))),
            (t("Liens actifs", "Active links"), lambda m: str(m.get('connections', '—'))),
            (t("Densité", "Density"), lambda m: fr_num(m.get('density', 0), 3)),
            (t("Triangles (clustering moyen)", "Average clustering"), lambda m: fr_num(m.get('clustering', 0), 3)),
            (t("Centralisation", "Centralization"), lambda m: fr_num(m.get('centralization', 0), 1, pct=True)),
            (t("Passes par lien", "Passes per link"), lambda m: fr_num(m.get('avg_link_passes', 0), 1))]
    comp_df = pd.DataFrame({t("Indicateur", "Metric"): [r[0] for r in rows],
                            team1: [r[1](metrics1) for r in rows],
                            team2: [r[1](metrics2) for r in rows]})
    st.dataframe(comp_df, width="stretch", hide_index=True)

footer("Données : StatsBomb (Open Data)", "Data: StatsBomb (Open Data)")
