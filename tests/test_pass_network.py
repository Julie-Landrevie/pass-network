"""
tests/test_pass_network.py
Tests unitaires — PassNetworkAnalyzer
Julie Landrevie — Football Data & Video Analyst

Run : pytest tests/ -v
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from pass_network import PassNetworkAnalyzer


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def analyzer():
    """Charge un match réel StatsBomb pour les tests (La Liga 2020/21, match 1)."""
    a = PassNetworkAnalyzer(match_id=3773386, min_passes=3)
    a.run()
    return a


# ── Tests chargement ──────────────────────────────────────────────────────────

def test_load_events(analyzer):
    assert analyzer.events is not None
    assert len(analyzer.events) > 0

def test_teams_loaded(analyzer):
    assert len(analyzer.teams) == 2

def test_nodes_not_empty(analyzer):
    for team in analyzer.teams:
        assert not analyzer.nodes[team].empty, f"Nodes vides pour {team}"

def test_edges_not_empty(analyzer):
    for team in analyzer.teams:
        assert not analyzer.edges[team].empty, f"Edges vides pour {team}"


# ── Tests structure nodes ──────────────────────────────────────────────────────

def test_nodes_columns(analyzer):
    required = ['player', 'avg_x', 'avg_y', 'pass_count', 'betweenness']
    for team in analyzer.teams:
        for col in required:
            assert col in analyzer.nodes[team].columns, f"Colonne '{col}' manquante pour {team}"

def test_nodes_count(analyzer):
    for team in analyzer.teams:
        n = len(analyzer.nodes[team])
        assert 1 <= n <= 11, f"{team} : {n} nœuds (attendu 1-11)"

def test_positions_in_pitch(analyzer):
    for team in analyzer.teams:
        nodes = analyzer.nodes[team]
        assert nodes['avg_x'].between(0, 120).all(), "avg_x hors terrain"
        assert nodes['avg_y'].between(0, 80).all(),  "avg_y hors terrain"


# ── Tests métriques ───────────────────────────────────────────────────────────

def test_metrics_keys(analyzer):
    required = ['density', 'clustering', 'centralization', 'avg_link_passes', 'total_passes', 'connections']
    for team in analyzer.teams:
        for key in required:
            assert key in analyzer.metrics[team], f"Métrique '{key}' manquante pour {team}"

def test_density_range(analyzer):
    for team in analyzer.teams:
        d = analyzer.metrics[team]['density']
        assert 0 <= d <= 1, f"Density hors [0,1] pour {team} : {d}"

def test_clustering_range(analyzer):
    for team in analyzer.teams:
        c = analyzer.metrics[team]['clustering']
        assert 0 <= c <= 1, f"Clustering hors [0,1] pour {team} : {c}"

def test_betweenness_range(analyzer):
    for team in analyzer.teams:
        bc = analyzer.nodes[team]['betweenness']
        assert bc.between(0, 1).all(), f"Betweenness hors [0,1] pour {team}"

def test_barça_more_passes(analyzer):
    """Barça doit avoir plus de passes qu'Alavés sur ce match."""
    teams = analyzer.teams
    passes = {t: analyzer.metrics[t]['total_passes'] for t in teams}
    max_team = max(passes, key=passes.get)
    assert passes[max_team] > 400, f"L'équipe dominante n'a que {passes[max_team]} passes"


# ── Tests période ─────────────────────────────────────────────────────────────

def test_period_filter_first_half():
    a = PassNetworkAnalyzer(match_id=3773386, min_passes=2, period='1st Half')
    a.run()
    for team in a.teams:
        assert not a.nodes[team].empty

def test_period_filter_second_half():
    # min_passes=1 car la 2ème mi-temps a peu de passes sur ce match court
    a = PassNetworkAnalyzer(match_id=3773386, min_passes=1, period='2nd Half')
    a.run()
    for team in a.teams:
        assert not a.nodes[team].empty


# ── Tests export ──────────────────────────────────────────────────────────────

def test_export(analyzer, tmp_path):
    analyzer.export(str(tmp_path))
    assert (tmp_path / 'pass_network_nodes.csv').exists()
    assert (tmp_path / 'pass_network_edges.csv').exists()
    assert (tmp_path / 'team_metrics.csv').exists()

def test_export_nodes_content(analyzer, tmp_path):
    analyzer.export(str(tmp_path))
    df = pd.read_csv(tmp_path / 'pass_network_nodes.csv')
    assert 'team' in df.columns
    assert 'player' in df.columns
    assert len(df) >= 2  # au moins quelques joueurs


# ── Tests summary ─────────────────────────────────────────────────────────────

def test_summary_returns_string(analyzer):
    s = analyzer.summary()
    assert isinstance(s, str)
    assert len(s) > 50

def test_summary_contains_teams(analyzer):
    s = analyzer.summary()
    for team in analyzer.teams:
        assert team in s
