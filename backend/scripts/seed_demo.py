"""Datos de demostración para el informe de gestión: pacientes y casos ficticios repartidos en varias semanas.

Solo datos ficticios (RUT de prueba desde 40.000.000) e IA SIMULADA. Usa los servicios de la aplicación
(triage, imágenes, validación de la IA y revisión médica) y después corre las fechas hacia atrás, para que el
Dashboard muestre semanas, tiempos de revisión y concordancia realistas.

No crea usuarios: usa un MEDICO activo (y un ADMINISTRATIVO activo si existe). No se repite si ya se aplicó.
Para deshacerlo, restaurar el respaldo tomado antes (la auditoría es de solo agregar).

Uso (desde backend/, con las migraciones aplicadas):
    python -m scripts.seed_demo [--patients 120] [--weeks 10]
    python -m scripts.seed_demo --fix-history   # ordena la historia de datos cargados con una versión anterior
"""

import argparse
import io
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
load_dotenv(Path(__file__).resolve().parents[1] / ".env", encoding="utf-8")

from PIL import Image as PILImage  # noqa: E402

from app.db.models.case import Case, CaseStatus  # noqa: E402
from app.db.models.image import ExamType, Image  # noqa: E402
from app.db.models.inference_result import InferenceResult  # noqa: E402
from app.db.models.patient import Patient  # noqa: E402
from app.db.models.privacy import ConsentEvent  # noqa: E402
from app.db.models.review import AIValidation, ClinicalReview  # noqa: E402
from app.db.models.triage import Notification, TriageLevel, TriageResult  # noqa: E402
from app.db.models.user import User, UserRole  # noqa: E402
from app.deps import SessionLocal  # noqa: E402
from app.schemas.cases import CaseCreate  # noqa: E402
from app.schemas.reviews import AIValidationIn, ReviewIn  # noqa: E402
from app.services import (  # noqa: E402
    case_service,
    image_service,
    privacy_service,
    review_service,
    seed_service,
    triage_service,
)
from app.utils.rut import compute_dv  # noqa: E402

RUT_BASE = 40_000_000

FIRST_NAMES = [
    "Ana",
    "Beatriz",
    "Camila",
    "Daniela",
    "Elena",
    "Francisca",
    "Gabriela",
    "Ignacia",
    "Javiera",
    "Karina",
    "Lorena",
    "María",
    "Natalia",
    "Olga",
    "Paula",
    "Rocío",
    "Sofía",
    "Teresa",
    "Valentina",
    "Ximena",
]
LAST_NAMES = [
    "Ficticia",
    "Prueba",
    "Demo",
    "Ejemplo",
    "Muestra",
    "Simulada",
    "Ensayo",
    "Modelo",
    "Patrón",
    "Piloto",
]
FINDINGS = {
    "ALTA": "Nódulo de bordes irregulares en el cuadrante superior externo. Hallazgo ficticio de demostración.",
    "MEDIA": "Asimetría focal sin masa definida. Hallazgo ficticio de demostración.",
    "BAJA": "Mamas de densidad heterogénea sin hallazgos sospechosos. Hallazgo ficticio de demostración.",
}
RECOMMENDATION = {"ALTA": "BIOPSIA", "MEDIA": "ESTUDIO_COMPLEMENTARIO", "BAJA": "CONTROL_RUTINA"}
BIRADS_FINAL = {"ALTA": [4, 5], "MEDIA": [3, 4], "BAJA": [1, 2]}
# Horas desde el primer triage hasta la revisión médica, por nivel (mínimo, máximo)
REVIEW_HOURS = {"ALTA": (1.5, 20), "MEDIA": (10, 60), "BAJA": (24, 140)}


def rut(n: int) -> str:
    return f"{n}-{compute_dv(str(n))}"


def fake_image(seed: int) -> bytes:
    img = PILImage.new("L", (512, 512), color=40 + seed * 17 % 160)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def symptoms(rng: random.Random) -> dict:
    roll = rng.random()
    if roll < 0.10:
        return {"birads_reported": rng.choice([4, 5])}
    if roll < 0.18:
        return {"palpable_mass": True}
    if roll < 0.22:
        return {"nipple_discharge": True}
    if roll < 0.40:
        return {"birads_reported": rng.choice([2, 3])}
    return {}


def verdict(rng: random.Random, detected: bool) -> str:
    roll = rng.random()
    if roll < 0.04:
        return "NO_EVALUABLE"
    if roll < 0.14:
        return "FALSO_POSITIVO" if detected else "FALSO_NEGATIVO"
    return "CONCORDANTE"


def assessment(rng: random.Random) -> str:
    roll = rng.random()
    return "APROPIADO" if roll < 0.82 else "SOBREESTIMADO" if roll < 0.92 else "SUBESTIMADO"


def shift_case(db, case: Case, created: datetime) -> datetime:
    """Corre la creación del caso, sus imágenes, inferencias y triages; devuelve el primer triage."""
    case.created_at = created
    first = created + timedelta(seconds=40)
    for i, img in enumerate(db.query(Image).filter(Image.case_id == case.id).all()):
        img.uploaded_at = created + timedelta(seconds=20 + i)
        for inf in db.query(InferenceResult).filter(InferenceResult.image_id == img.id).all():
            inf.created_at = created + timedelta(seconds=35 + i)
    results = db.query(TriageResult).filter(TriageResult.case_id == case.id).order_by(TriageResult.id).all()
    for i, r in enumerate(results):
        r.computed_at = first + timedelta(seconds=20 * i)
    for note in db.query(Notification).filter(Notification.case_id == case.id).all():
        note.created_at = first
        note.read_at = first + timedelta(minutes=30)
    return first


def demo_patients(db) -> list[Patient]:
    return (
        db.query(Patient)
        .filter(Patient.rut >= f"{RUT_BASE}-", Patient.rut < f"{RUT_BASE + 10_000}-")
        .order_by(Patient.id)
        .all()
    )


def align_history(db, patients: list[Patient], rng: random.Random) -> int:
    """Deja la historia de cada paciente en orden: registro y consentimiento unos días antes de su primer caso, y
    cada ajuste de nivel poco después del primer triage del caso. Devuelve cuántos pacientes se corrigieron."""
    fixed = 0
    for p in patients:
        first_case = (
            db.query(Case.created_at).filter(Case.patient_id == p.id).order_by(Case.created_at).first()
        )
        if first_case is None:
            continue
        if p.created_at is None or p.created_at >= first_case[0]:
            registered = first_case[0] - timedelta(days=rng.uniform(1, 14), minutes=rng.uniform(0, 600))
            p.created_at = registered
            p.consent_at = registered
            db.query(ConsentEvent).filter(ConsentEvent.patient_id == p.id).update(
                {ConsentEvent.occurred_at: registered}, synchronize_session=False
            )
            fixed += 1
        for case_id, created in db.query(Case.id, Case.created_at).filter(Case.patient_id == p.id).all():
            results = (
                db.query(TriageResult).filter(TriageResult.case_id == case_id).order_by(TriageResult.id).all()
            )
            computed = [r.computed_at for r in results if r.override_by is None]
            first = computed[0] if computed else created + timedelta(seconds=40)
            review = db.query(ClinicalReview.created_at).filter(ClinicalReview.case_id == case_id).first()
            for r in results:
                if r.override_by is not None and (review is None or r.computed_at > review[0]):
                    r.computed_at = first + timedelta(minutes=rng.uniform(10, 50))
    db.commit()
    return fixed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--patients", type=int, default=120)
    parser.add_argument("--weeks", type=int, default=10)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--fix-history",
        action="store_true",
        help="Solo ordena la historia de los datos de demostración ya cargados (registro, consentimiento y ajustes)",
    )
    args = parser.parse_args()
    rng = random.Random(args.seed)
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        if args.fix_history:
            patients = demo_patients(db)
            fixed = align_history(db, patients, rng)
            print(f"Historia ordenada: {fixed} de {len(patients)} pacientes de demostración corregidos.")
            return 0
        seed_service.ensure_reference_data(db)
        if db.query(Patient).filter(Patient.rut == rut(RUT_BASE)).first():
            print("Los datos de demostración ya están cargados. No se repiten.")
            return 0
        medico = (
            db.query(User)
            .filter(User.role == UserRole.MEDICO, User.is_active.is_(True))
            .order_by(User.id)
            .first()
        )
        if medico is None:
            print("Se necesita al menos un usuario MEDICO activo.")
            return 1
        staff = (
            db.query(User)
            .filter(User.role == UserRole.ADMINISTRATIVO, User.is_active.is_(True))
            .order_by(User.id)
            .first()
        ) or medico
        consent_text = privacy_service.active_consent_text(db)

        patients = []
        for i in range(args.patients):
            age = rng.randint(30, 78)
            p = Patient(
                rut=rut(RUT_BASE + i),
                first_name=rng.choice(FIRST_NAMES),
                last_name=rng.choice(LAST_NAMES),
                birth_date=(now - timedelta(days=age * 365 + rng.randint(0, 364))).date(),
                sex="F",
                family_history_first_degree=rng.random() < 0.18,
                previous_breast_cancer=rng.random() < 0.07,
                created_by=staff.id,
            )
            db.add(p)
            db.flush()
            privacy_service.record_consent(db, p, consent_text, staff)
            patients.append(p)
        db.commit()

        span = args.weeks * 7 * 24  # horas
        counts = {"casos": 0, "cerrados": 0, "ajustes": 0}
        case_ids: list[int] = []
        for n, p in enumerate(patients):
            for _ in range(2 if rng.random() < 0.12 else 1):
                # Más casos en las semanas recientes (tendencia creciente), en horario hábil
                age_h = span * (1 - rng.random() ** 0.8)
                created = now - timedelta(hours=age_h)
                created = created.replace(hour=rng.randint(8, 18), minute=rng.randint(0, 59))
                if created > now - timedelta(hours=1):
                    created = now - timedelta(hours=rng.uniform(1, 6))
                case = case_service.create_case(db, CaseCreate(patient_id=p.id, **symptoms(rng)), staff)
                counts["casos"] += 1
                case_ids.append(case.id)
                if rng.random() < 0.75:
                    img = image_service.upload_image(
                        db,
                        case.id,
                        f"mamografia_demo_{n}.png",
                        fake_image(n),
                        ExamType.MAMOGRAFIA,
                        "L",
                        staff,
                    )
                    image_service.run_inference(db, img.id)
                case = db.get(Case, case.id)
                first = shift_case(db, case, created)
                db.commit()

                result = triage_service.current_result(db, case.id)
                level = result.final_level.value
                if rng.random() < 0.08 and case.status != CaseStatus.CERRADO:
                    new = rng.choice([lv for lv in TriageLevel if lv != result.final_level])
                    adjusted = triage_service.override(
                        db, case.id, new, "Ajuste clínico (dato de demostración)", medico
                    )
                    # El ajuste ocurre poco después del primer triage (la historia queda en orden)
                    adjusted.computed_at = first + timedelta(minutes=rng.uniform(10, 50))
                    db.commit()
                    level = new.value
                    counts["ajustes"] += 1

                lo, hi = REVIEW_HOURS[level]
                reviewed = first + timedelta(hours=rng.uniform(lo, hi))
                # Los casos recientes quedan pendientes (y alguno ALTA atrasado, para la alerta)
                if reviewed > now - timedelta(hours=2) or rng.random() < 0.06:
                    continue
                db.refresh(case)
                if case.status == CaseStatus.PRIORIZADO:
                    review_service.take_case(db, case.id, medico)
                for img in db.query(Image).filter(Image.case_id == case.id).all():
                    inf = db.query(InferenceResult).filter(InferenceResult.image_id == img.id).first()
                    if inf is None:
                        continue
                    review_service.validate_ai(
                        db, case.id, img.id, AIValidationIn(verdict=verdict(rng, inf.detected)), medico
                    )
                review_service.create_review(
                    db,
                    case.id,
                    ReviewIn(
                        birads_final=rng.choice(BIRADS_FINAL[level]),
                        findings=FINDINGS[level],
                        recommendation=RECOMMENDATION[level],
                        triage_assessment=assessment(rng),
                    ),
                    medico,
                )
                rv = db.query(ClinicalReview).filter(ClinicalReview.case_id == case.id).one()
                rv.created_at = reviewed
                case = db.get(Case, case.id)
                case.closed_at = reviewed
                image_ids = db.query(Image.id).filter(Image.case_id == case.id)
                db.query(AIValidation).filter(AIValidation.image_id.in_(image_ids)).update(
                    {AIValidation.created_at: reviewed - timedelta(minutes=5)}, synchronize_session=False
                )
                db.commit()
                counts["cerrados"] += 1

        align_history(db, patients, rng)

        levels: dict[str, int] = {}
        for case_id in case_ids:
            r = triage_service.current_result(db, case_id)
            levels[r.final_level.value] = levels.get(r.final_level.value, 0) + 1
    print(
        f"Datos de demostración cargados: {args.patients} pacientes, {counts['casos']} casos "
        f"({counts['cerrados']} cerrados, {counts['ajustes']} ajustes de nivel) en {args.weeks} semanas."
    )
    print(f"Casos por nivel: {levels}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
