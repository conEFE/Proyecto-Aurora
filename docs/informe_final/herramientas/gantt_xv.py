# -*- coding: utf-8 -*-
"""Carta Gantt del capítulo XV: línea base frente a ejecución, por responsable, con hitos y corte al 23-11-2026.
Uso: python3 gantt_xv.py <salida.png>
Fechas reales: informe de Unidad 2 (declaradas por el equipo al 18-10-2026) e historial de Git/CHANGELOG del repositorio."""
import sys, datetime as dt
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as md
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

D = lambda s: dt.date(2026, int(s[3:5]), int(s[0:2]))
# id, actividad, responsable, base_ini, base_fin, real_ini, real_fin, estado (done|partial|progress|none|plan)
ROWS = [
 ("1", "Planificación y análisis", "FN", "11-04", "31-05", "11-04", "31-05", "done"),
 ("2", "Diseño, arquitectura y backlog", "EQ", "01-06", "30-07", "01-06", "30-07", "done"),
 ("3.1", "Sprint 1: base del sistema", "FJ", "16-07", "31-07", "16-07", "31-07", "done"),
 ("3.2", "Sprint 2: usuarios y pacientes", "FJ", "01-08", "15-08", "01-08", "15-08", "done"),
 ("3.3", "Sprint 3: casos clínicos", "FJ", "16-08", "31-08", "16-08", "31-08", "done"),
 ("3.4", "Sprint 4: exámenes e imágenes", "FJ", "01-09", "15-09", "01-09", "15-09", "done"),
 ("3.5", "Sprint 5: triage y priorización", "FC", "16-09", "30-09", "16-09", "30-09", "done"),
 ("3.6", "Sprint 6: dashboard y reportes (2.0.0–2.1.0)", "FJ", "01-10", "15-10", "01-10", "15-10", "done"),
 ("3.7a", "Métricas del modelo y firma (2.2.0)", "FC", None, None, "16-10", "03-11", "done"),
 ("3.7", "Sprint 7: seguridad e infraestructura (2.3.0–2.5.1)", "JM", "16-10", "31-10", "16-10", "11-11", "done"),
 ("3.8", "Sprint 8: integración y estabilización (2.6.0–2.10.0)", "EQ", "01-11", "15-11", "01-11", "16-11", "partial"),
 ("4.1", "QA y pruebas automatizadas", "FC", "16-10", "31-10", "16-10", "23-11", "partial"),
 ("4.2", "Validación clínica del prototipo", "FN", "16-11", "20-11", None, None, "none"),
 ("4.3", "Capacitación de usuarios", "FN", "10-11", "25-11", None, None, "none"),
 ("4.4", "Piloto y ajustes finales", "EQ", "20-11", "30-11", None, None, "none"),
 ("5.1", "Documentación final (informe)", "FN", "20-11", "05-12", "23-11", "05-12", "progress"),
 ("5.2", "Entrega y cierre académico", "EQ", "01-12", "10-12", "01-12", "10-12", "plan"),
]
COL = {"FN": "#A0335A", "FC": "#1F6F78", "JM": "#5B4C9E", "FJ": "#2E7D5B", "EQ": "#8A6A2E"}
NOM = {"FN": "Francisca Neira", "FC": "Felipe Campos", "JM": "Juan Francisco Meneses", "FJ": "F. Campos / J. F. Meneses", "EQ": "Equipo"}
MILES = [("Inicio", "11-04", "ok", 0, "center"), ("Inicio desarrollo", "16-07", "ok", 0, "center"), ("Versión 2.0.0", "07-10", "ok", 0, "right"),
         ("Firma SLA", "31-10", "no", 1, "right"), ("Modelo conectado", "11-11", "ok", 2, "right"), ("Validación clínica", "20-11", "no", 0, "right"),
         ("Aceptación MVP", "24-11", "plan", 1, "left"), ("Entrega", "10-12", "plan", 2, "left")]

fig, ax = plt.subplots(figsize=(11, 7.2), dpi=220)
n = len(ROWS)
for i, (id_, name, resp, bi, bf, ri, rf, st) in enumerate(ROWS):
    y = n - 1 - i
    if bi:
        ax.barh(y - 0.22, (D(bf) - D(bi)).days + 1, left=md.date2num(D(bi)), height=0.18, color="#B8B8B8", zorder=2)
    if ri:
        w = (D(rf) - D(ri)).days + 1
        if st == "done":
            ax.barh(y + 0.08, w, left=md.date2num(D(ri)), height=0.42, color=COL[resp], zorder=3)
        elif st == "partial":
            ax.barh(y + 0.08, w, left=md.date2num(D(ri)), height=0.42, color=COL[resp], hatch="///", edgecolor="white", zorder=3)
        elif st == "progress":
            ax.barh(y + 0.08, w, left=md.date2num(D(ri)), height=0.42, color=COL[resp], alpha=0.45, zorder=3, edgecolor=COL[resp])
        elif st == "plan":
            ax.barh(y + 0.08, w, left=md.date2num(D(ri)), height=0.42, facecolor="none", edgecolor=COL[resp], linestyle="--", zorder=3)
    else:
        ax.text(md.date2num(D(bf)) + 2, y + 0.05, "sin registro de ejecución", fontsize=6.5, va="center", color="#9A2F2F")
ax.set_yticks(range(n))
ax.set_yticklabels([f"{r[0]}  {r[1]}" for r in ROWS][::-1], fontsize=7.5)
corte = md.date2num(dt.date(2026, 11, 23))
ax.axvline(corte, color="#B03030", lw=1, ls="--", zorder=4)
ax.text(corte + 1, -0.9, "Corte 23-11-2026", color="#B03030", fontsize=7)
for name, d, st, lvl, ha in MILES:
    x = md.date2num(D(d)); y = n + 0.2 + lvl * 0.75
    mk = {"ok": ("D", "#222222", "#222222"), "no": ("D", "white", "#B03030"), "plan": ("D", "white", "#222222")}[st]
    ax.plot([x], [y], marker=mk[0], color=mk[2], markerfacecolor=mk[1], markersize=6, zorder=5)
    ax.text(x + (-1.5 if ha == "right" else 1.5 if ha == "left" else 0), y + 0.3, name, fontsize=6.3, ha=ha)
ax.set_xlim(md.date2num(dt.date(2026, 4, 1)), md.date2num(dt.date(2026, 12, 20)))
ax.set_ylim(-1.3, n + 2.9)
ax.xaxis.set_major_locator(md.MonthLocator()); ax.xaxis.set_major_formatter(md.DateFormatter("%m-%Y"))
ax.tick_params(axis="x", labelsize=7.5); ax.grid(axis="x", color="#E2E2E2", lw=0.6, zorder=0)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
leg = [Patch(color=COL[k], label=NOM[k]) for k in ("FN", "FC", "JM", "FJ", "EQ")]
leg += [Patch(color="#B8B8B8", label="Línea base (Unidad 1)"),
        Patch(facecolor="#777777", hatch="///", edgecolor="white", label="Ejecutado con pendientes"),
        Patch(facecolor="#777777", alpha=0.45, label="En curso"),
        Patch(facecolor="none", edgecolor="#444444", linestyle="--", label="Planificado"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="#222222", markeredgecolor="#222222", label="Hito cumplido"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="white", markeredgecolor="#B03030", label="Hito sin evidencia")]
ax.legend(handles=leg, fontsize=6.3, ncol=4, loc="upper center", bbox_to_anchor=(0.45, -0.06), frameon=False)
plt.tight_layout(); plt.savefig(sys.argv[1]); print("ok")
