"""Seed de desarrollo: 3 usuarios (uno por rol), 10 pacientes ficticios y casos en los 3 niveles de triage.

Solo datos ficticios y RUT de prueba. La contraseña de los usuarios de prueba se lee del entorno:

    AURORA_SEED_PASSWORD=...   (mínimo 8 caracteres)

Uso (desde backend/, con las migraciones aplicadas):
    python -m scripts.seed_dev
"""

import io
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
load_dotenv(Path(__file__).resolve().parents[1] / ".env", encoding="utf-8")

from PIL import Image as PILImage  # noqa: E402

from app.auth.security import hash_password  # noqa: E402
from app.db.models.case import Case  # noqa: E402
from app.db.models.image import ExamType  # noqa: E402
from app.db.models.patient import Patient  # noqa: E402
from app.db.models.triage import TriageResult  # noqa: E402
from app.db.models.user import User, UserRole  # noqa: E402
from app.deps import SessionLocal  # noqa: E402
from app.schemas.cases import CaseCreate  # noqa: E402
from app.services import case_service, image_service, seed_service, triage_service  # noqa: E402
from app.utils.rut import compute_dv  # noqa: E402

USERS = [
    ("10000003", UserRole.ADMIN, "Admin Demo", "admin@aurora-demo.cl"),
    ("10000004", UserRole.MEDICO, "Dra. Valentina Demo", "medico@aurora-demo.cl"),
    ("10000005", UserRole.ADMINISTRATIVO, "Carlos Demo", "administrativo@aurora-demo.cl"),
]

# (nombre, apellido, edad, antecedente familiar, cáncer previo)
PATIENTS = [
    ("Ana", "Ficticia", 58, True, False),
    ("Beatriz", "Prueba", 45, False, False),
    ("Carla", "Demo", 63, True, True),
    ("Daniela", "Ejemplo", 34, False, False),
    ("Elena", "Muestra", 72, False, True),
    ("Fernanda", "Ficticia", 51, False, False),
    ("Gabriela", "Prueba", 39, True, False),
    ("Helena", "Demo", 67, False, False),
    ("Isabel", "Ejemplo", 48, False, True),
    ("Josefa", "Muestra", 29, False, False),
]

# (índice paciente, síntomas/BI-RADS, días de antigüedad, ¿imagen?)
CASES = [
    (0, {"birads_reported": 4}, 1, True),  # ALTA por R_BIRADS
    (1, {"palpable_mass": True}, 0, True),  # ALTA por R_SINTOMA
    (2, {}, 20, True),  # puntaje alto (antecedentes + edad + espera)
    (3, {}, 0, False),  # BAJA
    (4, {"birads_reported": 2}, 5, True),
    (5, {}, 3, True),
    (6, {"nipple_discharge": True}, 2, False),  # ALTA
    (7, {"birads_reported": 3}, 10, True),
    (8, {}, 1, False),
    (9, {}, 0, False),  # BAJA
]


def rut(body: str) -> str:
    return f"{body}-{compute_dv(body)}"


def fake_image(seed: int) -> bytes:
    img = PILImage.new("L", (512, 512), color=40 + seed * 17 % 160)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> int:
    password = os.getenv("AURORA_SEED_PASSWORD", "")
    if len(password) < 8:
        print("Defina AURORA_SEED_PASSWORD (mínimo 8 caracteres) para los usuarios de prueba.")
        return 1
    today = date.today()
    with SessionLocal() as db:
        seed_service.ensure_reference_data(db)
        if db.query(Patient).filter(Patient.last_name.in_(["Ficticia", "Prueba", "Demo"])).count():
            print("El seed ya fue aplicado (hay pacientes ficticios). No se repite.")
            return 0

        users = {}
        for body, role, name, email in USERS:
            u = db.query(User).filter(User.rut == rut(body)).first()
            if u is None:
                u = User(
                    rut=rut(body),
                    email=email,
                    full_name=name,
                    password_hash=hash_password(password),
                    role=role,
                )
                db.add(u)
            users[role] = u
        db.commit()
        staff = users[UserRole.ADMINISTRATIVO]

        patients = []
        for i, (first, last, age, family, previous) in enumerate(PATIENTS):
            p = Patient(
                rut=rut(str(30000000 + i)),
                first_name=first,
                last_name=last,
                birth_date=date(today.year - age, 3, 15),
                sex="F",
                family_history_first_degree=family,
                previous_breast_cancer=previous,
                consent_given=True,
                consent_at=datetime.now(timezone.utc),
                consent_registered_by=staff.id,
                created_by=staff.id,
            )
            db.add(p)
            patients.append(p)
        db.commit()

        for n, (idx, fields, days_ago, with_image) in enumerate(CASES):
            case = case_service.create_case(db, CaseCreate(patient_id=patients[idx].id, **fields), staff)
            # Antigüedad simulada: se corre la creación y el primer triage en la misma cantidad de días
            shift = timedelta(days=days_ago)
            db.get(Case, case.id).created_at -= shift
            for result in db.query(TriageResult).filter(TriageResult.case_id == case.id).all():
                result.computed_at -= shift
            db.commit()
            if with_image:
                image = image_service.upload_image(
                    db, case.id, f"mamografia_{n}.png", fake_image(n), ExamType.MAMOGRAFIA, "L", staff
                )
                image_service.run_inference(db, image.id)
            triage_service.recalculate(db, db.get(Case, case.id))

        levels = {}
        for c in db.query(Case).all():
            r = triage_service.current_result(db, c.id)
            levels[r.final_level.value] = levels.get(r.final_level.value, 0) + 1
    print("Seed aplicado: 3 usuarios, 10 pacientes ficticios y 10 casos.")
    print(f"Casos por nivel: {levels}")
    print("Usuarios: " + ", ".join(f"{rut(b)} ({r.value})" for b, r, _, _ in USERS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
