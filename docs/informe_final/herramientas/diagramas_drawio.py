# -*- coding: utf-8 -*-
"""Diagramas del capítulo X en notación estándar (UML, ER) y con fuente editable en draw.io.
Uso: python3 diagramas_drawio.py <dir_salida> [nombre ...]
Genera <dir>/<nombre>.drawio y <dir>/<nombre>.svg; el PNG se exporta con svg_a_png.cjs."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from drawio_lib import Diagram, AZUL, VERDE, AMARILLO, ROJO, MORADO, GRIS

OUT = sys.argv[1]
SOLO = set(sys.argv[2:])
os.makedirs(OUT, exist_ok=True)
DIAGRAMAS = {}


def diagrama(f):
    DIAGRAMAS[f.__name__] = f
    return f


# ================================================================ Componentes (UML)
@diagrama
def cap10_componentes():
    D = Diagram(1530, 830)
    # navegador y contenedor web
    D.box(30, 30, 350, 130, "«device»\n**Navegador web**", GRIS, "node", valign="top", size=11)
    D.box(60, 85, 290, 55, "«component»\nAurora Web (React SPA)", "#ffffff", "component", size=11)
    D.box(30, 220, 350, 130, "«executionEnvironment»\n**Contenedor web**", GRIS, "node", valign="top", size=11)
    D.box(60, 275, 290, 55, "«component»\nCaddy (HTTPS, proxy /api)", "#ffffff", "component", size=11)
    D.edge([(205, 140), (205, 275)], "HTTPS 443")
    # backend
    D.box(440, 30, 640, 560, "«executionEnvironment»\n**Contenedor backend: API FastAPI (monolito modular)**", AZUL, "node",
          valign="top", size=11)
    D.box(470, 95, 580, 50, "«component»\nRutas REST (JSON + JWT)", "#ffffff", "component", size=11)
    filas = [["Autenticación\ny roles", "Pacientes y\nconsentimiento", "Casos e\nimágenes"],
             ["Motor de triage", "Revisión, firma\ny reportes", "Privacidad\n(Ley 21.719)"],
             ["Bitácora de\nauditoría", "Dashboard y\ncomparador", "Administración\nde usuarios"],
             ["Almacenamiento", "Envío de correos", "Proveedor de\ninferencia"]]
    xs = [470, 670, 870]
    for r, fila in enumerate(filas):
        y = 185 + r * 95
        for c, nom in enumerate(fila):
            D.box(xs[c], y, 180, 55, nom, "#ffffff", "component", size=11)
    for c in range(3):  # las rutas delegan en los módulos de dominio
        D.edge([(xs[c] + 90, 145), (xs[c] + 90, 185)], dashed=True, end="open")
    D.edge([(380, 302), (410, 302), (410, 120), (470, 120)], "HTTP :8000", label_at=(410, 210))
    D.edge([(920, 240), (920, 252), (660, 252), (660, 455), (560, 455), (560, 470)], dashed=True, end="open")
    D.edge([(1030, 240), (1030, 258), (1065, 258), (1065, 480), (1050, 480)], dashed=True, end="open")
    D.edge([(940, 430), (940, 448), (760, 448), (760, 470)], dashed=True, end="open")
    # externos
    D.box(80, 410, 250, 110, "«database»\nPostgreSQL 16\n(Amazon RDS)\n19 tablas", "#ffffff", "cylinder", size=11)
    D.edge([(440, 465), (330, 465)], "SQL/TLS 5432")
    D.box(330, 690, 200, 80, "«storage»\nAmazon S3\nimágenes cifradas", "#ffffff", "folder", size=11)
    D.edge([(560, 525), (560, 640), (430, 640), (430, 690)], "HTTPS (SDK)", label_at=(495, 640))
    D.lollipop(560, 560, "IAlmacenamiento")
    D.box(670, 700, 180, 70, "«external»\nServidor SMTP", "#ffffff", "rect", size=11)
    D.edge([(760, 525), (760, 700)], "SMTP", label_at=(760, 660))
    D.lollipop(760, 560, "ICorreo")
    # inferencia
    D.box(1170, 30, 330, 270, "«executionEnvironment»\n**Servicio de inferencia (PC con GPU)**", MORADO, "node", valign="top", size=11)
    D.box(1200, 95, 270, 55, "«component»\nAPI /predict · /health", "#ffffff", "component", size=11)
    D.box(1200, 210, 125, 55, "CNN\nResNet18", "#ffffff", "component", size=11)
    D.box(1345, 210, 125, 55, "YOLO11s\n(masas)", "#ffffff", "component", size=11)
    D.edge([(1262, 150), (1262, 210)])
    D.edge([(1407, 150), (1407, 210)])
    D.edge([(1050, 497), (1125, 497), (1125, 122), (1200, 122)], "HTTP + token\n(Tailscale)", label_at=(1125, 230))
    D.lollipop(1125, 345, "IInferencia")
    D.box(1170, 400, 330, 120, "«executionEnvironment»\n**Respaldo en AWS (planificado)**", "#ffffff", "node", valign="top",
          size=11, dashed=True)
    D.box(1200, 450, 270, 50, "Servicio de inferencia en CPU", "#ffffff", "component", size=11, dashed=True)
    D.edge([(960, 525), (960, 600), (1335, 600), (1335, 520)], "si el principal no responde", dashed=True)
    return D


# ================================================================ Modelo lógico (ER, pata de gallo)
@diagrama
def cap10_modelo_logico():
    d = json.load(open(os.path.join(HERE, "schema_modelos.json"), encoding="utf-8"))
    D = Diagram(1640, 1500)
    W = 200

    def rows(t):
        out = []
        for n, typ, pk, nul, fks, *_ in d[t]["cols"]:
            k = "PK" if pk else ("FK" if fks else "")
            typ = typ.split("(")[0].replace("TIMESTAMP", "TIMESTAMP").replace("CHARACTER VARYING", "VARCHAR")
            typ = {"DATETIME": "TIMESTAMP"}.get(typ, typ).lower()
            if typ.startswith("varchar") or typ.startswith("enum"):
                typ = typ[:9]
            out.append((k, n, typ[:10]))
        return out

    pos = {  # tabla: (x, y, color)
        "users": (30, 560, GRIS), "email_tokens": (30, 30, GRIS), "audit_log": (30, 270, GRIS),
        "error_log": (30, 1000, GRIS), "request_metrics": (30, 1260, GRIS),
        "consent_texts": (1410, 30, VERDE), "patients": (1120, 30, VERDE),
        "patient_consent_events": (1410, 230, VERDE), "data_subject_requests": (1410, 440, VERDE),
        "cases": (830, 330, AZUL), "images": (540, 620, AZUL), "inference_results": (540, 930, AZUL),
        "ai_validations": (830, 1000, AZUL), "notifications": (1120, 650, AZUL),
        "triage_configs": (540, 30, AMARILLO), "triage_results": (540, 260, AMARILLO),
        "clinical_reviews": (1120, 830, MORADO), "report_signatures": (1410, 760, MORADO), "reports": (1410, 980, MORADO),
    }
    ys, box = {}, {}
    for t, (x, y, c) in pos.items():
        ys[t], box[t] = D.entity(x, y, W, t, rows(t), c)
    # relaciones entre entidades de negocio (las de users se resumen abajo para no saturar)
    rel = [
        ("patients", "consent_text_id", "consent_texts", [(1320, None), (1320, 54), (1410, 54)]),
        ("patient_consent_events", "patient_id", "patients", None),
        ("patient_consent_events", "consent_text_id", "consent_texts", None),
        ("data_subject_requests", "patient_id", "patients", None),
        ("cases", "patient_id", "patients", None),
        ("images", "case_id", "cases", None),
        ("triage_results", "case_id", "cases", None),
        ("triage_results", "config_version", "triage_configs", None),
        ("inference_results", "image_id", "images", None),
        ("ai_validations", "image_id", "images", None),
        ("ai_validations", "inference_result_id", "inference_results", None),
        ("notifications", "case_id", "cases", None),
        ("clinical_reviews", "case_id", "cases", None),
        ("report_signatures", "case_id", "cases", None),
        ("reports", "case_id", "cases", None),
        ("reports", "signature_id", "report_signatures", None),
        ("email_tokens", "user_id", "users", None),
        ("audit_log", "user_id", "users", None),
        ("error_log", "user_id", "users", None),
    ]
    used, chan = {}, {}

    def canal(x):  # separa las líneas verticales que comparten el mismo espacio entre columnas
        k = round(x / 40); n = chan.get(k, 0); chan[k] = n + 1
        return x + (n // 2 + 1) * 9 * (1 if n % 2 else -1) if n else x
    for child, col, parent, _ in rel:
        cx, cy, cw, ch = box[child]; px, py, pw, ph = box[parent]
        fy = ys[child][col]
        k = used.get(parent, 0); used[parent] = k + 1
        pky = py + 33 + (k % 4) * 4
        if parent == "cases" and child in ("reports", "report_signatures"):
            x1 = canal(1075); x2 = canal(1365)
            pts = [(px + pw, pky), (x1, pky), (x1, 1072 + k * 6), (x2, 1072 + k * 6), (x2, fy), (cx, fy)]
            D.edge(pts, end="erMany", start="erOne")
            continue
        if cx > px + pw:      # hijo a la derecha del padre
            mid = canal((px + pw + cx) / 2)
            pts = [(cx, fy), (mid, fy), (mid, pky), (px + pw, pky)]
        elif cx + cw < px:    # hijo a la izquierda
            mid = canal((cx + cw + px) / 2)
            pts = [(cx + cw, fy), (mid, fy), (mid, pky), (px, pky)]
        else:                 # misma columna: por el costado derecho
            side = canal(max(cx + cw, px + pw) + 20)
            pts = [(cx + cw, fy), (side, fy), (side, pky), (px + pw, pky)]
        D.edge(pts, start="erMany", end="erOne")
    D.text(30, 1400, 1580, 80,
           "Notación de pata de gallo: | | = uno y solo uno; pata de gallo = muchos. Colores: gris, identidad y acceso; verde, pacientes y "
           "privacidad; azul, casos e imágenes; amarillo, triage; morado, revisión y reportes.\nLas columnas FK hacia users "
           "(autoría, médico asignado o revisor) se muestran en cada tabla y no se dibujan como líneas para no saturar el diagrama.",
           size=11, align="left", valign="top")
    return D


# ================================================================ Topología (UML de despliegue)
@diagrama
def cap10_topologia():
    D = Diagram(1500, 820)
    D.box(30, 60, 210, 120, "«device»\n**PC de los usuarios**\nnavegador web\n(4 roles)", GRIS, "node", size=11)
    D.box(30, 600, 210, 110, "«device»\n**Equipo de operación**\nAWS CLI", GRIS, "node", size=11)
    D.box(300, 80, 170, 100, "Internet", "#ffffff", "cloud", size=12)
    D.edge([(240, 125), (310, 125)], "HTTPS 443", label_at=(272, 105))
    # AWS
    D.box(540, 30, 650, 720, "**AWS · región us-east-2 (Ohio)**", "#ffffff", "group", valign="top", align="left", size=12)
    D.box(570, 75, 200, 70, "Route 53\nauroracare.cl", "#ffffff", "rect", size=11)
    D.edge([(420, 95), (420, 70), (670, 70), (670, 75)], "DNS", dashed=True, label_at=(540, 70))
    D.box(570, 190, 590, 230, "Grupo de seguridad aurora-web: 80/443 TCP, 443 UDP; sin SSH", "#ffffff", "group", valign="top",
          align="left", size=11, dashed=True)
    D.box(600, 225, 530, 175, "«device» **EC2 aurora-prod** (t4g.micro, IP elástica)", AZUL, "node", valign="top", size=11)
    D.box(625, 280, 150, 95, "«executionEnvironment»\nweb\nCaddy :443", "#ffffff", "node", size=10)
    D.box(800, 280, 150, 95, "«executionEnvironment»\nbackend\nFastAPI :8000", "#ffffff", "node", size=10)
    D.box(975, 280, 140, 95, "«executionEnvironment»\nagente\nTailscale", "#ffffff", "node", size=10)
    D.edge([(775, 327), (800, 327)])
    D.edge([(950, 327), (975, 327)])
    D.edge([(470, 150), (500, 150), (500, 327), (625, 327)], "HTTPS 443", label_at=(500, 240))
    D.box(570, 470, 280, 120, "Grupo de seguridad aurora-rds: 5432 solo desde aurora-web", "#ffffff", "group", valign="top",
          align="left", size=10, dashed=True)
    D.box(615, 505, 190, 75, "RDS PostgreSQL 16\n(privada, cifrada)", "#ffffff", "cylinder", size=11)
    D.edge([(860, 375), (860, 440), (710, 440), (710, 505)], "TLS 5432", label_at=(785, 440))
    D.box(900, 500, 180, 70, "Amazon S3\nimágenes y respaldos", "#ffffff", "folder", size=11)
    D.edge([(900, 375), (900, 460), (990, 460), (990, 500)], "HTTPS", label_at=(945, 460))
    D.box(900, 620, 180, 55, "CloudWatch Logs\ny alarmas", "#ffffff", "rect", size=11)
    D.edge([(1100, 375), (1100, 647), (1080, 647)], "registros", dotted=True, label_at=(1100, 600))
    D.box(570, 640, 200, 60, "Systems Manager\n(Session Manager)", "#ffffff", "rect", size=11)
    D.edge([(240, 670), (570, 670)], "HTTPS + IAM", dashed=True)
    D.edge([(670, 640), (670, 610), (560, 610), (560, 360), (625, 360)], "sesión", dashed=True, label_at=(560, 500))
    # Tailscale y GitHub
    D.box(1250, 210, 230, 200, "**Red privada Tailscale**", "#ffffff", "group", valign="top", size=11, dashed=True)
    D.box(1270, 260, 190, 120, "«device»\n**PC con GPU**\nservicio de inferencia\n:8080", MORADO, "node", size=11)
    D.edge([(1115, 327), (1270, 327)], "HTTP + token\n(túnel cifrado)", label_at=(1180, 360))
    D.box(1270, 520, 190, 90, "«external»\nGitHub Actions\n+ GHCR", GRIS, "rect", size=11)
    D.edge([(1270, 565), (1235, 565), (1235, 250), (1130, 250)], "imágenes de\ncontenedor", dashed=True, label_at=(1235, 470))
    return D


# ================================================================ Infraestructura cloud (despliegue en AWS)
@diagrama
def cap10_infraestructura():
    D = Diagram(1600, 900)
    D.box(30, 40, 200, 90, "«device»\nUsuarios\n(navegador)", GRIS, "node", size=11)
    D.box(300, 40, 250, 90, "«external»\nGitHub\nActions · GHCR", GRIS, "rect", size=11)
    D.box(1300, 40, 260, 110, "«device»\n**PC con GPU (fuera de AWS)**\nCNN + YOLO", MORADO, "node", size=11)
    D.box(30, 190, 1540, 680, "**Proyecto de AWS · región us-east-2** (plan gratuito con créditos)", "#ffffff", "group",
          valign="top", align="left", size=12)
    D.box(60, 240, 190, 70, "Route 53\ndemo.auroracare.cl", "#ffffff", "rect", size=11)
    D.edge([(130, 130), (130, 240)], "DNS", dashed=True, label_at=(130, 160))
    # EC2
    D.box(300, 240, 880, 300, "«device» **EC2 aurora-prod** · t4g.micro arm64 · Amazon Linux 2023 · disco cifrado · IMDSv2", VERDE,
          "node", valign="top", size=11)
    D.box(330, 300, 190, 80, "«container»\nweb (Caddy)", "#ffffff", "component", size=11)
    D.box(570, 300, 190, 80, "«container»\nbackend (FastAPI)", "#ffffff", "component", size=11)
    D.box(810, 300, 160, 80, "agente\nTailscale", "#ffffff", "rect", size=11)
    D.box(1000, 300, 150, 80, "monitor_salud.sh\n(cada minuto)", "#ffffff", "rect", size=11)
    D.box(330, 430, 190, 80, "backup_db.sh\n(diario, 03:15)", "#ffffff", "rect", size=11)
    D.edge([(520, 340), (570, 340)], "/api")
    D.edge([(760, 340), (810, 340)])
    D.edge([(230, 85), (260, 85), (260, 340), (330, 340)], "HTTPS 443", label_at=(260, 160))
    D.edge([(425, 130), (425, 300)], "imágenes", dashed=True, label_at=(425, 210))
    D.edge([(890, 300), (890, 95), (1300, 95)], "POST /predict (Tailscale)", label_at=(1090, 95))
    # datos
    D.box(300, 600, 880, 230, "**Datos** (sin acceso público)", "#ffffff", "group", valign="top", align="left", size=11)
    D.box(340, 650, 300, 140, "«database»\nAmazon RDS aurora-demo-db\nPostgreSQL 16 · db.t4g.micro\n20 GB cifrados", AZUL,
          "cylinder", size=11)
    D.box(780, 660, 340, 120, "«storage»\nAmazon S3 (privado, versionado)\nimages/ · backups/ (35 días)", AMARILLO, "folder", size=11)
    D.edge([(640, 380), (640, 560), (490, 560), (490, 650)], "SQL/TLS 5432", label_at=(565, 560))
    D.edge([(700, 380), (700, 580), (950, 580), (950, 660)], "HTTPS", label_at=(825, 580))
    D.edge([(425, 510), (425, 545), (1000, 545), (1000, 660)], "volcado", dashed=True, label_at=(870, 545))
    # operación y seguridad
    D.box(1240, 240, 300, 80, "CloudWatch Logs\n/aurora/prod · /aurora/monitor", "#ffffff", "rect", size=11)
    D.box(1240, 360, 300, 70, "Alarmas de CloudWatch", "#ffffff", "rect", size=11)
    D.box(1240, 470, 300, 70, "Amazon SNS aurora-alertas\n(aviso por correo)", "#ffffff", "rect", size=11)
    D.edge([(1150, 340), (1200, 340), (1200, 280), (1240, 280)], "métrica", dotted=True, label_at=(1200, 310))
    D.edge([(1390, 320), (1390, 360)], dotted=True)
    D.edge([(1390, 430), (1390, 470)], dotted=True)
    D.box(1240, 600, 300, 110, "**Seguridad**\nIAM (rol de mínimo privilegio)\nSecrets Manager · Session Manager\ngrupos aurora-web y aurora-rds",
          ROJO, "rect", size=11)
    D.box(1240, 750, 300, 70, "Presupuesto USD 15/mes\n(alertas al 85 % y 100 %)", "#ffffff", "rect", size=11)
    return D


# ================================================================ Arquitectura por capas
@diagrama
def cap10_arquitectura():
    D = Diagram(1500, 800)
    capas = [("Usuarios", GRIS, ["Personal\nadministrativo", "Médico", "Administrador", "Jefatura y\nfinanzas"], "Navegador web (HTTPS)"),
             ("Presentación", AZUL, ["Aurora Web\nReact + TypeScript", "Caddy\nHTTPS y proxy /api"], "Contenedor web en EC2"),
             ("Lógica de negocio", VERDE, ["Autenticación\ny roles", "Pacientes\ny casos", "Imágenes", "Motor de\ntriage",
                                          "Revisión\ny firma", "Reportes y\ndashboard", "Privacidad", "Auditoría"],
              "Contenedor backend en EC2\n(API FastAPI)"),
             ("Análisis automatizado", MORADO, ["Proveedor de inferencia\n(principal → respaldo → simulado)",
                                                "Servicio CNN ResNet18\n+ YOLO11s"], "PC con GPU (Tailscale);\nrespaldo en AWS planificado"),
             ("Datos", AMARILLO, ["PostgreSQL 16\n19 tablas", "Imágenes cifradas\n(Fernet + SSE-KMS)"], "Amazon RDS · Amazon S3"),
             ("Operación", GRIS, ["Respaldo\ndiario", "Registros y\nalarmas", "Integración\ncontinua", "DNS y\nsecretos"],
              "CloudWatch · GitHub Actions\nRoute 53 · Secrets Manager")]
    D.text(200, 15, 900, 30, "**Componentes de software**", 12)
    D.text(1140, 15, 330, 30, "**Infraestructura**", 12)
    y = 50
    for nombre, color, comps, infra in capas:
        h = 105
        D.box(30, y, 160, h, "**" + nombre + "**", color, "rect", size=12)
        D.box(200, y, 920, h, "", color, "rect")
        n = len(comps); gap = 10; w = (900 - gap * (n - 1)) / n
        for i, c in enumerate(comps):
            D.box(210 + i * (w + gap), y + 15, w, h - 30, c, "#ffffff", "rounded", size=11)
        D.box(1140, y, 330, h, infra, color, "rect", size=11)
        if y > 50:
            D.edge([(660, y - 18), (660, y)], end="block")
        y += h + 18
    return D


# ================================================================ Componente de análisis (CNN + YOLO)
@diagrama
def it15_cnn():
    D = Diagram(1300, 870)
    D.box(450, 20, 400, 60, "Mamografía (PNG, JPEG o DICOM)\nescala de grises, 1 canal", "#ffffff", "note", size=11)
    D.box(450, 120, 400, 60, "Preprocesamiento\necualización CLAHE (2,0; 8 × 8)", GRIS, "rounded", size=11)
    D.edge([(650, 80), (650, 120)])
    D.box(60, 220, 560, 600, "**Etapa 1: clasificación (CNN ResNet18)**", "#ffffff", "group", valign="top", size=12)
    D.box(820, 220, 420, 320, "**Etapa 2: localización (YOLO11s)**", "#ffffff", "group", valign="top", size=12)
    D.edge([(560, 180), (560, 200), (340, 200), (340, 265)])
    D.edge([(740, 180), (740, 200), (1030, 200), (1030, 265)])
    capas = [("Entrada 672 × 1024 × 1\n(ajuste sin deformar, con relleno)", "#ffffff"),
             ("Conv 7 × 7, 64 filtros, paso 2\n(capa inicial adaptada a 1 canal)", AZUL),
             ("Bloques residuales\n64 → 128 → 256 → 512 filtros", "#ffffff"),
             ("Promedio global (512 valores)", "#ffffff"),
             ("Dropout 40 % + densa 512 → 1\n(capa de salida reemplazada)", AZUL),
             ("Sigmoide: probabilidad de malignidad\n≥ 0,35 → sospechosa", "#ffffff")]
    y = 265
    for i, (t, c) in enumerate(capas):
        D.box(120, y, 440, 62, t, c, "rect", size=11)
        if i:
            D.edge([(340, y - 30), (340, y)])
        y += 92
    D.box(870, 265, 320, 62, "Redimensión: lado mayor 1.280 px\n3 canales", "#ffffff", "rect", size=11)
    D.box(870, 357, 320, 62, "Detector YOLO11s", "#ffffff", "rect", size=11)
    D.box(870, 449, 320, 62, "Cajas de la clase «masa»\nconfianza ≥ 0,25", "#ffffff", "rect", size=11)
    D.edge([(1030, 327), (1030, 357)]); D.edge([(1030, 419), (1030, 449)])
    D.box(700, 700, 520, 90, "Respuesta (POST /predict): probabilidad, sospecha, cajas,\ntiempo y versión del modelo → inference_results",
          VERDE, "rounded", size=11)
    D.edge([(560, 758), (620, 758), (620, 745), (700, 745)])
    D.edge([(1030, 511), (1030, 700)])
    D.text(60, 835, 1180, 25, "En azul, las capas de ResNet18 modificadas; el resto de la red viene preentrenado con ImageNet.", 11,
           align="left")
    return D


for name, f in DIAGRAMAS.items():
    if SOLO and name not in SOLO:
        continue
    f().save(os.path.join(OUT, name))
    print("ok", name)
