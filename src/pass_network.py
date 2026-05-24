"""
pass_network.py — Pass Network & Team Structure Analysis
=========================================================
Julie Landrevie — Football Data & Video Analyst

Module réutilisable pour construire, analyser et visualiser
les réseaux de passes à partir des données StatsBomb.

Usage rapide
------------
    from pass_network import PassNetworkAnalyzer

    analyzer = PassNetworkAnalyzer(match_id=3773386)
    analyzer.run()                          # pipeline complet
    analyzer.plot_network('Barcelona')      # visualisation
    analyzer.export('output/')              # export CSV + PNG

Fonction standalone
-------------------
    from pass_network import quick_analysis
    quick_analysis(competition_id=11, season_id=90, match_index=0)
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Literal, Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgba
from mplsoccer import Pitch

warnings.filterwarnings("ignore")

# ── Constantes visuelles ──────────────────────────────────────────────────────

DARK_BG    = "#0a0e1a"
PITCH_LINE = "#2d3748"
ACCENT_1   = "#4fd1c5"   # équipe 1 (teal)
ACCENT_2   = "#f6ad55"   # équipe 2 (orange)


# ─────────────────────────────────────────────────────────────────────────────
# Classe principale
# ─────────────────────────────────────────────────────────────────────────────

class PassNetworkAnalyzer:
    """
    Analyse complète du réseau de passes pour un match StatsBomb.

    Parameters
    ----------
    match_id : int
        Identifiant du match dans StatsBomb Open Data.
    min_passes : int
        Seuil minimum de passes par liaison pour l'afficher.
    period : 'Full Match' | '1st Half' | '2nd Half'
        Filtre temporel appliqué à toutes les analyses.
    """

    def __init__(
        self,
        match_id: int,
        min_passes: int = 3,
        period: Literal["Full Match", "1st Half", "2nd Half"] = "Full Match",
    ) -> None:
        self.match_id   = match_id
        self.min_passes = min_passes
        self.period     = period

        # Attributs remplis après run()
        self.events:  Optional[pd.DataFrame] = None
        self.lineups: Optional[dict]          = None
        self.teams:   list[str]               = []
        self.nodes:   dict[str, pd.DataFrame] = {}
        self.edges:   dict[str, pd.DataFrame] = {}
        self.metrics: dict[str, dict]          = {}

    # ── Chargement ────────────────────────────────────────────────────────────

    def load(self) -> "PassNetworkAnalyzer":
        """Charge les événements et les compositions depuis StatsBomb."""
        from statsbombpy import sb

        print(f"📥 Chargement du match {self.match_id}…")
        self.events  = sb.events(match_id=self.match_id)
        self.lineups = sb.lineups(match_id=self.match_id)
        self.teams   = self.events["team"].unique().tolist()
        print(f"   Équipes : {self.teams[0]} vs {self.teams[1]}")
        print(f"   Événements : {len(self.events):,}")
        return self

    # ── Construction réseau ───────────────────────────────────────────────────

    def _build_one_team(self, team: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Construit nodes et edges pour une équipe."""
        passes = self.events[
            (self.events["type"] == "Pass")
            & (self.events["team"] == team)
            & (self.events["pass_outcome"].isna())
        ].copy()

        if self.period == "1st Half":
            passes = passes[passes["period"] == 1]
        elif self.period == "2nd Half":
            passes = passes[passes["period"] == 2]

        passes["x"]     = passes["location"].apply(lambda l: l[0] if isinstance(l, list) else np.nan)
        passes["y"]     = passes["location"].apply(lambda l: l[1] if isinstance(l, list) else np.nan)
        passes["end_x"] = passes["pass_end_location"].apply(lambda l: l[0] if isinstance(l, list) else np.nan)
        passes["end_y"] = passes["pass_end_location"].apply(lambda l: l[1] if isinstance(l, list) else np.nan)
        passes = passes.dropna(subset=["x", "y", "end_x", "end_y", "pass_recipient"])

        # XI de départ : calculé sur TOUS les events période 1, avant le filtre période
        all_passes_p1 = self.events[
            (self.events["type"] == "Pass") &
            (self.events["team"] == team) &
            (self.events["pass_outcome"].isna()) &
            (self.events["period"] == 1)
        ]
        starters = all_passes_p1["player"].value_counts()
        xi = starters[starters >= 1].index.tolist()[:11]

        nodes = (
            passes[passes["player"].isin(xi)]
            .groupby("player")
            .agg(avg_x=("x", "mean"), avg_y=("y", "mean"), pass_count=("x", "count"))
            .reset_index()
        )

        pair_df = passes[passes["player"].isin(xi) & passes["pass_recipient"].isin(xi)]
        edges = pair_df.groupby(["player", "pass_recipient"]).size().reset_index(name="count")
        edges = edges[edges["count"] >= self.min_passes]

        return nodes, edges

    def build_networks(self) -> "PassNetworkAnalyzer":
        """Construit les réseaux pour les deux équipes."""
        for team in self.teams:
            nodes, edges = self._build_one_team(team)
            self.nodes[team] = nodes
            self.edges[team] = edges
            print(f"   🕸️  {team} : {len(nodes)} nœuds · {len(edges)} liaisons")
        return self

    # ── Métriques NetworkX ────────────────────────────────────────────────────

    def _add_centrality(self, team: str) -> None:
        nodes, edges = self.nodes[team], self.edges[team]
        if nodes.empty or edges.empty:
            return

        G = nx.DiGraph()
        for _, r in nodes.iterrows():
            G.add_node(r["player"])
        for _, r in edges.iterrows():
            G.add_edge(r["player"], r["pass_recipient"], weight=r["count"])

        bc  = nx.betweenness_centrality(G, weight="weight", normalized=True)
        ind = dict(G.in_degree(weight="weight"))
        oud = dict(G.out_degree(weight="weight"))

        self.nodes[team] = nodes.copy()
        self.nodes[team]["betweenness"] = self.nodes[team]["player"].map(bc).fillna(0)
        self.nodes[team]["in_degree"]   = self.nodes[team]["player"].map(ind).fillna(0)
        self.nodes[team]["out_degree"]  = self.nodes[team]["player"].map(oud).fillna(0)

    def _compute_team_metrics(self, team: str) -> dict:
        nodes, edges = self.nodes[team], self.edges[team]
        if nodes.empty or edges.empty:
            return {}

        G = nx.DiGraph()
        for _, r in nodes.iterrows():
            G.add_node(r["player"])
        for _, r in edges.iterrows():
            G.add_edge(r["player"], r["pass_recipient"], weight=r["count"])

        n  = len(G.nodes)
        bc = list(nx.betweenness_centrality(G, normalized=True).values())
        max_bc = max(bc) if bc else 0

        return {
            "density":         round(nx.density(G), 3) if n > 1 else 0,
            "clustering":      round(nx.average_clustering(G.to_undirected()), 3) if n > 1 else 0,
            "centralization":  round(sum(max_bc - v for v in bc) / (n - 1) * 100, 1) if n > 1 else 0,
            "avg_link_passes": round(edges["count"].mean(), 1),
            "total_passes":    int(nodes["pass_count"].sum()),
            "connections":     len(edges),
        }

    def compute_metrics(self) -> "PassNetworkAnalyzer":
        """Calcule centralité et métriques globales pour chaque équipe."""
        for team in self.teams:
            self._add_centrality(team)
            self.metrics[team] = self._compute_team_metrics(team)
            m = self.metrics[team]
            print(
                f"   📊 {team} — density={m.get('density')}"
                f" · clustering={m.get('clustering')}"
                f" · centralization={m.get('centralization')}%"
            )
        return self

    # ── Pipeline complet ──────────────────────────────────────────────────────

    def run(self) -> "PassNetworkAnalyzer":
        """Load → build → metrics : pipeline complet."""
        return self.load().build_networks().compute_metrics()

    # ── Visualisations ────────────────────────────────────────────────────────

    def _setup_dark_pitch(self, figsize=(12, 8)):
        pitch = Pitch(
            pitch_type="statsbomb",
            pitch_color=DARK_BG,
            line_color=PITCH_LINE,
            linewidth=1.5,
            corner_arcs=True,
        )
        fig, ax = pitch.draw(figsize=figsize)
        fig.patch.set_facecolor(DARK_BG)
        ax.set_facecolor(DARK_BG)
        return fig, ax, pitch

    def plot_network(
        self,
        team: str,
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> plt.Figure:
        """
        Visualise le réseau de passes pour une équipe.

        Parameters
        ----------
        team : str         — Nom de l'équipe (doit être dans self.teams)
        save_path : str    — Chemin de sauvegarde PNG (optionnel)
        show : bool        — Afficher avec plt.show()
        """
        nodes, edges = self.nodes.get(team, pd.DataFrame()), self.edges.get(team, pd.DataFrame())
        accent = ACCENT_1 if team == self.teams[0] else ACCENT_2

        fig, ax, _ = self._setup_dark_pitch()

        if nodes.empty or edges.empty:
            ax.text(60, 40, "Données insuffisantes", color="white", fontsize=14, ha="center")
            return fig

        max_p, max_e = nodes["pass_count"].max(), edges["count"].max()

        for _, edge in edges.iterrows():
            fn = nodes[nodes["player"] == edge["player"]]
            tn = nodes[nodes["player"] == edge["pass_recipient"]]
            if fn.empty or tn.empty:
                continue
            xs, ys = fn.iloc[0][["avg_x", "avg_y"]]
            xe, ye = tn.iloc[0][["avg_x", "avg_y"]]
            alpha = 0.15 + 0.65 * (edge["count"] / max_e)
            lw    = 0.5  + 5.0  * (edge["count"] / max_e)
            ax.annotate(
                "",
                xy=(xe, ye),
                xytext=(xs, ys),
                arrowprops=dict(
                    arrowstyle="->",
                    color=to_rgba(accent, alpha),
                    lw=lw,
                    connectionstyle="arc3,rad=0.05",
                ),
            )

        for _, node in nodes.iterrows():
            size  = 900 + 2500 * (node["pass_count"] / max_p)
            ax.scatter(node["avg_x"], node["avg_y"], s=size, c=accent,
                       zorder=5, alpha=0.9, linewidths=2, edgecolors="white")
            short = node["player"].split()[-1]
            ax.text(node["avg_x"], node["avg_y"] - 3.8, short,
                    color="white", fontsize=8, fontweight="bold",
                    ha="center", va="top", zorder=6, fontfamily="monospace")
            ax.text(node["avg_x"], node["avg_y"], str(int(node["pass_count"])),
                    color=DARK_BG, fontsize=7.5, fontweight="bold",
                    ha="center", va="center", zorder=7)

        ax.set_title(
            f"{team}  |  Pass Network  |  {self.period}",
            color="white", fontsize=13, fontweight="bold", pad=14,
        )

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
            print(f"✅ Sauvegardé : {save_path}")
        if show:
            plt.show()
        return fig

    def plot_heatmap(
        self,
        team: str,
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> plt.Figure:
        """Heatmap KDE des positions de passe."""
        passes = self.events[(self.events["type"] == "Pass") & (self.events["team"] == team)].copy()

        if self.period == "1st Half":
            passes = passes[passes["period"] == 1]
        elif self.period == "2nd Half":
            passes = passes[passes["period"] == 2]

        passes["x"] = passes["location"].apply(lambda l: l[0] if isinstance(l, list) else np.nan)
        passes["y"] = passes["location"].apply(lambda l: l[1] if isinstance(l, list) else np.nan)
        passes = passes.dropna(subset=["x", "y"])

        fig, ax, pitch = self._setup_dark_pitch()

        if not passes.empty:
            pitch.kdeplot(passes["x"], passes["y"], ax=ax,
                          cmap="YlOrRd", fill=True, levels=100, alpha=0.75, bw_adjust=0.7)

        ax.set_title(
            f"{team}  |  Passing Heatmap  |  {self.period}",
            color="white", fontsize=13, fontweight="bold", pad=14,
        )

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
        if show:
            plt.show()
        return fig

    def plot_all(self, save_dir: Optional[str] = None) -> None:
        """Génère toutes les visualisations (réseaux + heatmaps) côte à côte."""
        save = Path(save_dir) if save_dir else None
        if save:
            save.mkdir(parents=True, exist_ok=True)

        # Pass networks
        fig, axes = plt.subplots(1, 2, figsize=(22, 9), facecolor=DARK_BG)
        pitch = Pitch(pitch_type="statsbomb", pitch_color=DARK_BG,
                      line_color=PITCH_LINE, linewidth=1.5, corner_arcs=True)

        for ax_idx, team in enumerate(self.teams):
            pitch.draw(ax=axes[ax_idx])
            axes[ax_idx].set_facecolor(DARK_BG)
            nodes = self.nodes.get(team, pd.DataFrame())
            edges = self.edges.get(team, pd.DataFrame())
            accent = ACCENT_1 if ax_idx == 0 else ACCENT_2

            if nodes.empty or edges.empty:
                continue

            max_p, max_e = nodes["pass_count"].max(), edges["count"].max()
            for _, edge in edges.iterrows():
                fn = nodes[nodes["player"] == edge["player"]]
                tn = nodes[nodes["player"] == edge["pass_recipient"]]
                if fn.empty or tn.empty:
                    continue
                xs, ys = fn.iloc[0][["avg_x", "avg_y"]]
                xe, ye = tn.iloc[0][["avg_x", "avg_y"]]
                alpha = 0.15 + 0.65 * (edge["count"] / max_e)
                lw    = 0.5  + 5.0  * (edge["count"] / max_e)
                axes[ax_idx].annotate("", xy=(xe, ye), xytext=(xs, ys),
                    arrowprops=dict(arrowstyle="->", color=to_rgba(accent, alpha),
                                   lw=lw, connectionstyle="arc3,rad=0.05"))

            for _, node in nodes.iterrows():
                size = 900 + 2500 * (node["pass_count"] / max_p)
                axes[ax_idx].scatter(node["avg_x"], node["avg_y"], s=size, c=accent,
                           zorder=5, alpha=0.9, linewidths=2, edgecolors="white")
                short = node["player"].split()[-1]
                axes[ax_idx].text(node["avg_x"], node["avg_y"] - 3.8, short,
                        color="white", fontsize=8, fontweight="bold", ha="center", va="top", zorder=6)
                axes[ax_idx].text(node["avg_x"], node["avg_y"], str(int(node["pass_count"])),
                        color=DARK_BG, fontsize=7.5, ha="center", va="center", zorder=7)

            axes[ax_idx].set_title(team, color="white", fontsize=13, fontweight="bold")

        fig.suptitle(f"Pass Networks — {self.period}", color="white", fontsize=15, fontweight="bold", y=1.01)
        plt.tight_layout()

        if save:
            p = save / "pass_networks.png"
            plt.savefig(p, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
            print(f"✅ {p}")
        plt.show()

    # ── Export ────────────────────────────────────────────────────────────────

    def export(self, output_dir: str = ".") -> None:
        """
        Exporte les nodes, edges et métriques en CSV.

        Parameters
        ----------
        output_dir : str — dossier de destination
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        all_nodes, all_edges = [], []
        for team in self.teams:
            n = self.nodes.get(team, pd.DataFrame()).copy()
            e = self.edges.get(team, pd.DataFrame()).copy()
            if not n.empty:
                n["team"] = team
                all_nodes.append(n)
            if not e.empty:
                e["team"] = team
                all_edges.append(e)

        if all_nodes:
            pd.concat(all_nodes).to_csv(out / "pass_network_nodes.csv", index=False)
        if all_edges:
            pd.concat(all_edges).to_csv(out / "pass_network_edges.csv", index=False)

        metrics_rows = [{"team": t, **m} for t, m in self.metrics.items()]
        pd.DataFrame(metrics_rows).to_csv(out / "team_metrics.csv", index=False)

        print(f"\n✅ Export dans '{out}/' :")
        print("   pass_network_nodes.csv")
        print("   pass_network_edges.csv")
        print("   team_metrics.csv")

    # ── Résumé texte ──────────────────────────────────────────────────────────

    def summary(self) -> str:
        """Résumé textuel des métriques pour les deux équipes."""
        lines = [f"\n{'═'*60}", f" Match {self.match_id} | {self.period}", f"{'═'*60}"]
        for team in self.teams:
            m = self.metrics.get(team, {})
            nodes = self.nodes.get(team, pd.DataFrame())
            lines += [
                f"\n📋 {team}",
                f"   Passes total    : {m.get('total_passes', '—')}",
                f"   Connexions      : {m.get('connections', '—')}",
                f"   Density         : {m.get('density', '—')}",
                f"   Clustering      : {m.get('clustering', '—')}",
                f"   Centralization  : {m.get('centralization', '—')}%",
                f"   Passes/liaison  : {m.get('avg_link_passes', '—')}",
            ]
            if not nodes.empty and "betweenness" in nodes.columns:
                top = nodes.sort_values("betweenness", ascending=False).iloc[0]
                lines.append(f"   Pivot clé       : {top['player']} (BC={top['betweenness']:.3f})")

        lines.append(f"\n{'═'*60}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Fonction standalone
# ─────────────────────────────────────────────────────────────────────────────

def quick_analysis(
    competition_id: int = 11,
    season_id: int = 90,
    match_index: int = 0,
    min_passes: int = 3,
    period: str = "Full Match",
    export_dir: Optional[str] = None,
) -> PassNetworkAnalyzer:
    """
    Lance une analyse complète en quelques lignes.

    Parameters
    ----------
    competition_id : int   — ID compétition StatsBomb
    season_id      : int   — ID saison StatsBomb
    match_index    : int   — Index du match dans la liste (0 = premier)
    min_passes     : int   — Seuil minimum de passes par liaison
    period         : str   — 'Full Match', '1st Half', '2nd Half'
    export_dir     : str   — Dossier d'export CSV (None = pas d'export)

    Returns
    -------
    PassNetworkAnalyzer avec toutes les données chargées

    Example
    -------
    >>> from pass_network import quick_analysis
    >>> analyzer = quick_analysis(competition_id=11, season_id=90)
    >>> print(analyzer.summary())
    >>> analyzer.plot_all(save_dir='output/')
    """
    from statsbombpy import sb

    matches  = sb.matches(competition_id=competition_id, season_id=season_id)
    match_id = int(matches.iloc[match_index]["match_id"])
    home     = matches.iloc[match_index]["home_team"]
    away     = matches.iloc[match_index]["away_team"]
    print(f"🎯 Analyse : {home} vs {away}  (match_id={match_id})")

    analyzer = PassNetworkAnalyzer(match_id=match_id, min_passes=min_passes, period=period)
    analyzer.run()
    print(analyzer.summary())

    if export_dir:
        analyzer.export(export_dir)

    return analyzer


# ─────────────────────────────────────────────────────────────────────────────
# Exécution directe
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pass Network & Team Structure Analysis")
    parser.add_argument("--competition", type=int, default=11,    help="Competition ID (default: 11 = La Liga)")
    parser.add_argument("--season",      type=int, default=90,    help="Season ID (default: 90 = 2020/2021)")
    parser.add_argument("--match-index", type=int, default=0,     help="Match index in season (default: 0)")
    parser.add_argument("--min-passes",  type=int, default=3,     help="Min passes per link (default: 3)")
    parser.add_argument("--period",      type=str, default="Full Match",
                        choices=["Full Match", "1st Half", "2nd Half"])
    parser.add_argument("--export",      type=str, default=None,  help="Export directory for CSV files")
    parser.add_argument("--no-plot",     action="store_true",      help="Skip visualizations")

    args = parser.parse_args()

    analyzer = quick_analysis(
        competition_id=args.competition,
        season_id=args.season,
        match_index=args.match_index,
        min_passes=args.min_passes,
        period=args.period,
        export_dir=args.export,
    )

    if not args.no_plot:
        analyzer.plot_all(save_dir=args.export)
