import sys, datetime as dt
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as md
D=lambda s: dt.date(2026,int(s[3:5]),int(s[0:2]))
rows=[("1","Planificación y análisis",None,None,"h"),
("1.1","Inicio y acta","11-04","18-04","p"),("1.2","Planificación general","19-04","31-05","p"),("1.3","Marco teórico y legislación","20-04","31-05","p"),
("2","Diseño y arquitectura",None,None,"h"),
("2.1","Diseño de arquitectura","01-06","15-07","d"),("2.2","Diseño de interfaz frontend","10-06","30-07","d"),("2.3","Preparación del Product Backlog","01-07","15-07","d"),
("3","Desarrollo iterativo (sprints)",None,None,"h"),
("3.1","Sprint 1 – Base del sistema","16-07","31-07","s"),("3.2","Sprint 2 – Usuarios y pacientes","01-08","15-08","s"),("3.3","Sprint 3 – Casos clínicos y antecedentes","16-08","31-08","s"),
("3.4","Sprint 4 – Exámenes e imágenes","01-09","15-09","s"),("3.5","Sprint 5 – Triage y priorización","16-09","30-09","s"),("3.6","Sprint 6 – Dashboard y reportes","01-10","15-10","s"),
("3.7","Sprint 7 – Seguridad e infraestructura","16-10","31-10","s"),("3.8","Sprint 8 – Integración y estabilización","01-11","15-11","s"),
("4","Pruebas y validación",None,None,"h"),
("4.1","QA y pruebas de integración","16-10","31-10","q"),("4.2","Validación clínica del prototipo (condicionada)","16-11","20-11","q"),("4.3","Capacitación de usuarios","10-11","25-11","q"),("4.4","Piloto y ajustes finales (condicionado)","20-11","30-11","q"),
("5","Cierre del proyecto",None,None,"h"),
("5.1","Documentación final","20-11","05-12","c"),("5.2","Entrega y cierre académico","01-12","10-12","c")]
col={"p":"#3B6FB6","d":"#7E5BB5","s":"#3C9A64","q":"#D9A21B","c":"#C0504D"}
fig,ax=plt.subplots(figsize=(9.5,6.6),dpi=230)
n=len(rows)
for i,(id_,name,a,b,k) in enumerate(rows):
    y=n-1-i
    if k=="h":
        ax.axhspan(y-0.5,y+0.5,color="#EEF1F5",zorder=0)
        continue
    s,e=D(a),D(b)+dt.timedelta(days=1)
    ax.barh(y,(e-s).days,left=md.date2num(s),height=0.6,color=col[k],edgecolor="none",zorder=3)
ax.set_yticks(range(n)); ax.set_yticklabels([("%s  %s"%(r[0],r[1])) for r in rows][::-1],fontsize=8.5)
for lab,r in zip(ax.get_yticklabels(),rows[::-1]):
    if r[4]=="h": lab.set_fontweight("bold")
for name,d,yo,ha in [("Inicio","11-04",0,"center"),("Inicio desarrollo","16-07",0,"center"),("Versión beta","15-10",0,"center"),("Validación clínica","20-11",1.3,"right"),("Cierre","10-12",0,"center")]:
    x=md.date2num(D(d)); ax.axvline(x,color="#555",lw=0.7,ls="--",zorder=2)
    ax.text(x,n-0.2+yo,name+"\n"+d+"-2026",fontsize=7.5,ha=ha,va="bottom")
ax.set_xlim(md.date2num(dt.date(2026,4,1)),md.date2num(dt.date(2026,12,20)))
ax.set_ylim(-0.6,n+2.6)
ax.xaxis.set_major_locator(md.MonthLocator()); ax.xaxis.set_major_formatter(md.DateFormatter("%m-%Y"))
ax.tick_params(axis="x",labelsize=8.5); ax.grid(axis="x",color="#DDD",lw=0.6,zorder=1)
for sp in ["top","right"]: ax.spines[sp].set_visible(False)
plt.tight_layout(); plt.savefig(sys.argv[1]); print("ok")
