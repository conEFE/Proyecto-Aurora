# -*- coding: utf-8 -*-
"""Genera los diagramas del capítulo X a partir de la arquitectura actual (D-07-01).
Uso: python3 diagramas_cap10.py <schema.json> <dir_salida>
schema.json se obtiene de los modelos SQLAlchemy (ver herramientas/README del plan, iteración 3)."""
import json, os, subprocess, sys

schema_path, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
F = 'fontname="DejaVu Sans"'

def render(name, src):
    p = os.path.join(out, name + ".dot")
    open(p, "w", encoding="utf-8").write(src)
    subprocess.run(["dot", "-Tpng", "-Gdpi=200", p, "-o", os.path.join(out, name + ".png")], check=True)

# --- Componentes ------------------------------------------------------------
render("cap10_componentes", f'''digraph G {{
 graph [{F}, rankdir=TB, splines=ortho, nodesep=0.35, ranksep=0.5, fontsize=11, label="Diagrama de componentes – arquitectura actual", labelloc=t];
 node [{F}, shape=component, fontsize=9, style=filled, fillcolor="#FFFFFF"];
 edge [{F}, fontsize=8, color="#444444"];
 subgraph cluster_nav {{ label="«device» Navegador del usuario"; style="rounded,filled"; fillcolor="#EEF3FA";
   spa [label="Aurora Web\\nReact + TypeScript (SPA)\\njsPDF (reportes)"]; }}
 subgraph cluster_web {{ label="«container» web"; style="rounded,filled"; fillcolor="#FDF3E6";
   caddy [label="Caddy\\nTLS (Let's Encrypt), sitio estático\\nproxy inverso /api"]; }}
 subgraph cluster_api {{ label="«container» backend – API FastAPI (monolito modular)"; style="rounded,filled"; fillcolor="#EAF5EC";
   rutas [label="Rutas REST\\nauth · patients · cases · images · triage\\nreports · dashboard · privacy · admin · inference"];
   auth [label="Autenticación y\\nautorización (JWT, roles)"];
   neg [label="Servicios de negocio\\npacientes, casos, imágenes, revisión,\\nreportes, privacidad, cuentas, comparador"];
   triage [label="Motor de triage\\n(reglas y parámetros versionados)"];
   audit [label="Auditoría\\n(bitácora append-only)"];
   stor [label="Almacenamiento\\nLocal | S3 cifrado"];
   prov [label="Proveedor de inferencia\\nprincipal → respaldo → simulado"];
   mail [label="Envío de correos\\n(consola | SMTP)"];
 }}
 db [shape=cylinder, label="PostgreSQL\\n(Amazon RDS en demostración)\\n19 tablas", fillcolor="#E8EEF9"];
 s3 [shape=folder, label="Amazon S3\\nimágenes cifradas y respaldos", fillcolor="#E8EEF9"];
 subgraph cluster_bkp {{ label="«container» respaldo (planificado, AWS)"; style="rounded,dashed"; fillcolor="#FFFFFF";
   bkp [style="dashed,filled", fillcolor="#FFFFFF", label="Misma API, en CPU\\nsi el equipo con GPU\\nno responde"]; }}
 subgraph cluster_inf {{ label="«container» servicio de inferencia (equipo con GPU)"; style="rounded,filled"; fillcolor="#F3ECF8";
   inf [label="API FastAPI\\nPOST /predict · GET /health"]; cnn [label="CNN ResNet18\\n(probabilidad)"]; yolo [label="YOLO11s\\n(masas)"]; }}
 spa -> caddy [label="HTTPS 443"];
 caddy -> rutas [label="HTTP interno :8000"];
 rutas -> auth; rutas -> neg; rutas -> triage;
 neg -> audit; neg -> stor; neg -> prov; neg -> triage;
 auth -> db [style=dashed]; neg -> db [label="SQL/TLS 5432"]; triage -> db [style=dashed]; audit -> db [style=dashed];
 stor -> s3 [label="HTTPS (SDK)"];
 prov -> inf [label="HTTP + token Bearer\\n(red Tailscale)"];
 inf -> cnn; inf -> yolo;
 neg -> mail;
 prov -> bkp [style=dashed];
}}''')

# --- Topología --------------------------------------------------------------
render("cap10_topologia", f'''digraph G {{
 graph [{F}, rankdir=LR, splines=true, nodesep=0.4, ranksep=0.7, fontsize=11, label="Topología de comunicaciones – entorno de demostración", labelloc=t];
 node [{F}, shape=box, style="rounded,filled", fillcolor="#FFFFFF", fontsize=9];
 edge [{F}, fontsize=8];
 usr [label="Usuarios\\n(administrativo, médico,\\nadministrador, jefatura)\\nnavegador web"];
 dns [label="Route 53\\nzona auroracare.cl\\n(delegada desde NIC Chile)"];
 net [shape=ellipse, label="Internet"];
 subgraph cluster_aws {{ label="AWS – us-east-2 (Ohio)"; style="rounded,filled"; fillcolor="#F6F8FB";
   subgraph cluster_sgw {{ label="Grupo de seguridad aurora-web: 80/443 TCP, 443 UDP (sin 22)"; style="rounded,dashed"; fillcolor="#EAF5EC";
     ec2 [label="EC2 t4g.micro (Elastic IP)\\nDocker: web (Caddy :443)\\n→ backend (:8000, red interna)"]; }}
   subgraph cluster_sgd {{ label="Grupo aurora-rds: 5432 solo desde aurora-web"; style="rounded,dashed"; fillcolor="#E8EEF9";
     rds [shape=cylinder, label="RDS PostgreSQL 16\\nprivada, cifrada"]; }}
   s3 [shape=folder, label="S3\\nimágenes y respaldos"];
   cw [label="CloudWatch Logs\\n/aurora/prod"];
   ssm [label="Systems Manager\\nSession Manager"];
 }}
 subgraph cluster_ts {{ label="Red privada Tailscale"; style="rounded,dashed";
   pc [label="Equipo con GPU\\nservicio de inferencia :8080\\n(firewall: solo 100.64.0.0/10)"]; }}
 gh [label="GitHub Actions\\nCI y publicación de\\nimágenes (GHCR)"];
 adm [label="Equipo de operación"];
 usr -> dns [label="DNS", style=dashed];
 usr -> net [label="HTTPS 443"]; net -> ec2 [label="HTTPS 443"];
 ec2 -> rds [label="TLS 5432"]; ec2 -> s3 [label="HTTPS"]; ec2 -> cw [label="logs", style=dashed];
 ec2 -> pc [label="HTTP + token\\ntúnel cifrado"];
 adm -> ssm [label="HTTPS + IAM", style=dashed]; ssm -> ec2 [style=dashed];
 gh -> ec2 [label="imágenes de\\ncontenedor", style=dashed];
}}''')

# --- Infraestructura --------------------------------------------------------
render("cap10_infraestructura", f'''digraph G {{
 graph [{F}, rankdir=TB, splines=true, nodesep=0.35, ranksep=0.55, fontsize=11, label="Infraestructura desplegada – entorno de demostración (al 16-11-2026)", labelloc=t, newrank=true];
 node [{F}, shape=box, style="rounded,filled", fillcolor="#FFFFFF", fontsize=9];
 edge [{F}, fontsize=8, color="#555555"];
 usr [label="Usuarios (navegador web)"];
 gh [label="GitHub\\nrepositorio · Actions · GHCR"];
 subgraph cluster_aws {{ label="Proyecto AWS (plan gratuito con créditos) – región us-east-2"; style="rounded,filled"; fillcolor="#F6F8FB";
   r53 [label="Route 53\\ndemo.auroracare.cl → Elastic IP"];
   subgraph cluster_ec2 {{ label="EC2 aurora-prod · t4g.micro arm64 · Amazon Linux 2023\\ndisco 10 GB gp3 cifrado · IMDSv2"; style="rounded,filled"; fillcolor="#EAF5EC";
     web [label="Contenedor web\\nCaddy + sitio React"]; api [label="Contenedor backend\\nAPI FastAPI"]; cron [label="Respaldo diario\\nbackup_db.sh (03:15)"]; }}
   sec [label="Seguridad y control\\nIAM (rol AuroraEC2Role)\\nSecrets Manager\\ngrupos de seguridad"];
   ops [label="Operación\\nCloudWatch Logs (30 días)\\nSession Manager\\npresupuesto USD 15/mes"];
   rds [shape=cylinder, label="RDS aurora-demo-db\\nPostgreSQL 16.15 · db.t4g.micro\\n20 GB gp3 cifrados · privada\\nrespaldo automático 1 día", fillcolor="#E8EEF9"];
   s3 [shape=folder, label="S3 (privado, versionado)\\nimágenes: Fernet + SSE-KMS\\nrespaldos: retención 35 días", fillcolor="#E8EEF9"];
 }}
 pc [label="Equipo con GPU (fuera de AWS)\\nservicio de inferencia CNN + YOLO\\nconectado por Tailscale", fillcolor="#F3ECF8"];
 {{rank=same; usr; gh;}}
 {{rank=same; rds; s3; pc;}}
 usr -> r53 [label="DNS", style=dashed]; usr -> web [label="HTTPS 443"];
 web -> api; api -> rds [label="TLS 5432"]; api -> s3 [label="HTTPS"]; cron -> rds [style=dashed]; cron -> s3 [label="volcado", style=dashed];
 api -> pc [label="POST /predict"]; sec -> api [style=dotted, arrowhead=none]; ops -> api [style=dotted, arrowhead=none];
 gh -> web [label="imágenes de contenedor", style=dashed];
}}''')

# --- Arquitectura (tabla por capas) -----------------------------------------
def fila(capa, sw, hw, color):
    return (f'<tr><td bgcolor="{color}" width="120"><b>{capa}</b></td><td bgcolor="{color}" width="420">{sw}</td>'
            f'<td bgcolor="{color}" width="200">{hw}</td></tr>')
tabla = ('<table border="0" cellborder="1" cellspacing="0" cellpadding="7">'
 '<tr><td bgcolor="#D9EAF7"><b>Capa</b></td><td bgcolor="#D9EAF7"><b>Componentes de software</b></td><td bgcolor="#D9EAF7"><b>Infraestructura / servicio</b></td></tr>'
 + fila("Usuarios", "Personal administrativo · Médico · Administrador", "Navegador web; HTTPS 443", "#F2F2F2")
 + fila("Presentación", "Aurora Web: React + TypeScript (SPA)<br/>cola de triage · casos · validación de IA · firma · dashboard · PDF (jsPDF)", "Caddy (TLS Let&apos;s Encrypt) en EC2", "#EEF3FA")
 + fila("Lógica de negocio", "API FastAPI – monolito modular (REST JSON + JWT)<br/>autenticación y roles · pacientes y casos · imágenes · motor de triage<br/>revisión, firma y reportes · dashboard · privacidad · auditoría", "Contenedor backend en EC2 t4g.micro", "#EAF5EC")
 + fila("Análisis automatizado", "Proveedor de inferencia (simulado | HTTP, con servicio de respaldo y respaldo simulado)<br/>servicio CNN ResNet18 + YOLO11s – prototipo sin validación clínica", "Equipo con GPU vía Tailscale<br/>(movible a AWS cambiando la URL)", "#F3ECF8")
 + fila("Datos", "PostgreSQL – 19 tablas (casos, triage versionado, resultados y validaciones de IA, firmas, auditoría)<br/>almacenamiento de imágenes cifrado (local | S3)", "Amazon RDS PostgreSQL 16 · Amazon S3", "#FBF7E6")
 + fila("Operación", "Respaldo diario a S3 · registros centralizados · integración continua · DNS y secretos", "CloudWatch Logs · GitHub Actions · Route 53 · Secrets Manager", "#F2F2F2")
 + '</table>')
render("cap10_arquitectura", f'digraph G {{ graph [{F}, label="Arquitectura de la solución – N-tier, monolito modular (software y hardware)", labelloc=t, fontsize=11]; node [{F}, shape=plaintext, fontsize=9]; t [label=<{tabla}>]; }}')

# --- Modelo lógico (entidades y relaciones) ---------------------------------
d = json.load(open(schema_path, encoding="utf-8"))
grupos = {
 "Identidad y acceso": ["users", "email_tokens", "audit_log", "error_log", "request_metrics"],
 "Pacientes y privacidad": ["patients", "consent_texts", "patient_consent_events", "data_subject_requests"],
 "Casos e imágenes": ["cases", "images", "inference_results", "ai_validations", "notifications"],
 "Triage": ["triage_configs", "triage_results"],
 "Revisión y reportes": ["clinical_reviews", "report_signatures", "reports"],
}
colors = ["#EEF3FA", "#EAF5EC", "#FBF7E6", "#F3ECF8", "#FDF3E6"]
lines = [f'digraph ER {{ graph [{F}, rankdir=LR, splines=true, nodesep=0.25, ranksep=0.9, fontsize=11, label="Modelo lógico – entidades y relaciones (generado desde los modelos SQLAlchemy)\\nLas referencias a users (autoría, médico asignado) se listan como FK y no se dibujan", labelloc=t, concentrate=false];',
         f' node [{F}, shape=plaintext, fontsize=8]; edge [{F}, color="#666666", arrowhead=crow, arrowtail=none, dir=both, arrowsize=0.6];']
for gi, (g, tabs) in enumerate(grupos.items()):
    lines.append(f' subgraph cluster_{gi} {{ label="{g}"; style="rounded,filled"; fillcolor="{colors[gi]}"; fontsize=10;')
    for t in tabs:
        cols = d[t]["cols"]
        rows = []
        for n, typ, pk, nul, fks, *_ in cols:
            tag = "PK" if pk else ("FK" if fks else "")
            if tag:
                rows.append(f'<tr><td align="left">{tag}</td><td align="left">{n}</td></tr>')
        rows.append(f'<tr><td></td><td align="left"><i>+ {sum(1 for c in cols if not c[2] and not c[4])} atributos</i></td></tr>')
        lines.append(f'  {t} [label=<<table border="0" cellborder="1" cellspacing="0" bgcolor="white"><tr><td colspan="2" bgcolor="#D9EAF7"><b>{t}</b></td></tr>{"".join(rows)}</table>>];')
    lines.append(" }")
seen = set()
for t, v in d.items():
    for n, typ, pk, nul, fks, *rest in v["cols"]:
        uniq = bool(rest and rest[0])
        for f in fks:
            tgt = f.split(".")[0]
            if tgt == "users":
                continue  # referencias de autoría: se listan como FK en cada tabla, sin arista
            key = (tgt, t, n)
            if key in seen: continue
            seen.add(key)
            lines.append(f' {tgt} -> {t} [arrowtail=tee, arrowhead={"tee" if uniq else "crow"}, tooltip="{n}"];')
lines.append("}")
render("cap10_modelo_logico", "\n".join(lines))
print("ok")

# --- Casos de uso (catálogo de Unidad 2 actualizado con funciones implementadas después) ---
uc = [("CU01", "Iniciar sesión"), ("CU02", "Gestionar usuarios y roles"), ("CU03", "Consultar bitácora\\nde auditoría"),
      ("CU04", "Registrar paciente\\ny consentimiento"), ("CU05", "Crear y gestionar\\ncaso clínico"), ("CU06", "Cargar exámenes\\ne imágenes"),
      ("CU07", "Analizar imagen"), ("CU08", "Calcular triage"), ("CU09", "Consultar cola\\npriorizada"), ("CU10", "Sobrescribir nivel\\nde triage"),
      ("CU11", "Revisar caso y\\nregistrar resultado"), ("CU12", "Generar reporte\\nclínico PDF"), ("CU13", "Configurar parámetros\\nde triage"),
      ("CU14", "Visualizar dashboard\\nde métricas"), ("CU15", "Validar informe de IA\\npor imagen"), ("CU16", "Firmar reporte\\nclínico"),
      ("CU17", "Cambiar contraseña"), ("CU18", "Gestionar solicitudes\\nde titulares de datos"),
      ("CU19", "Comparar desempeño\\nde médicos"), ("CU20", "Activar cuenta\\npor correo")]
nuevos = {"CU17", "CU18", "CU19", "CU20"}
L = [f'digraph UC {{ graph [{F}, rankdir=LR, nodesep=0.12, ranksep=1.1, fontsize=11, label="Diagrama de casos de uso – Plataforma Aurora (actualizado)", labelloc=t];',
     f' node [{F}, fontsize=8]; edge [{F}, fontsize=7, arrowhead=none, color="#555555"];',
     ' adm [shape=box, style="rounded", label="«actor»\\nPersonal\\nadministrativo"]; med [shape=box, style="rounded", label="«actor»\\nMédico"];',
     ' admin [shape=box, style="rounded", label="«actor»\\nAdministrador\\ndel sistema"]; jef [shape=box, style="rounded", label="«actor»\\nJefatura\\ny finanzas"]; inf [shape=box, style="rounded,dashed", label="«system»\\nServicio de\\ninferencia"];',
     ' subgraph cluster_s { label="Plataforma Aurora"; style="rounded,filled"; fillcolor="#F8F9FB";']
for cid, name in uc:
    fill = "#FFF4D6" if cid in nuevos else "#FFFFFF"
    L.append(f'  {cid} [shape=ellipse, style=filled, fillcolor="{fill}", label="{cid}\\n{name}"];')
L.append(" }")
rel = {"adm": ["CU01", "CU04", "CU05", "CU06", "CU09", "CU14", "CU17", "CU18", "CU20"],
       "med": ["CU01", "CU04", "CU05", "CU06", "CU09", "CU10", "CU11", "CU12", "CU13", "CU14", "CU15", "CU16", "CU17", "CU18", "CU20"],
       "admin": ["CU01", "CU02", "CU03", "CU14", "CU17", "CU19", "CU20"],
       "jef": ["CU01", "CU14", "CU17", "CU19", "CU20"]}
for a, cus in rel.items():
    for c in cus:
        L.append(f" {a} -> {c};")
L += [' CU07 -> inf;',
      ' CU06 -> CU07 [style=dashed, arrowhead=open, label="«include»"]; CU07 -> CU08 [style=dashed, arrowhead=open, label="«include»"];',
      ' CU11 -> CU15 [style=dashed, arrowhead=open, label="«include»"]; CU12 -> CU16 [style=dashed, arrowhead=open, label="«include»"];',
      ' CU10 -> CU11 [style=dashed, arrowhead=open, label="«extend»"]; CU12 -> CU11 [style=dashed, arrowhead=open, label="«extend»"];',
      ' {rank=same; adm; med; admin; jef;}', "}"]
render("cap10_casos_uso", "\n".join(L))
print("ok casos de uso")
