"""Conta estações do OpenStreetMap por tipo (teste)."""
import sys, collections
sys.path.insert(0, "scripts")
import geo
est = geo.estacoes()
print(len(est), collections.Counter(e[3] for e in est))
print(sorted(e[0] for e in est if e[3] == "Trem")[:60])
print([e for e in est if "Mau" in e[0] or "Capuava" in e[0] or "Guapituba" in e[0] or "Santo Andr" in e[0] or "Utinga" in e[0]])
