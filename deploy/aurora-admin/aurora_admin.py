#!/usr/bin/env python3
"""aurora-admin: administra una instancia de Aurora Care por institución (hospital o CESFAM).

Cada institución es una pila de CloudFormation (institucion.yaml) con su servidor, IP fija, bucket cifrado, rol y
registro DNS. Su configuración y sus secretos viven en Parameter Store bajo /aurora/<institución>/.

Uso (desde la raíz del repositorio, con credenciales de AWS del equipo):
    python deploy/aurora-admin/aurora_admin.py inscribir hospital-x --version sha-<commit> \\
        --admin-rut 12345678-5 --admin-email admin@hospital-x.cl --admin-nombre "Nombre Apellido"
    python deploy/aurora-admin/aurora_admin.py listar
    python deploy/aurora-admin/aurora_admin.py clave-admin hospital-x
    python deploy/aurora-admin/aurora_admin.py actualizar hospital-x --version sha-<commit>   (o --todas)
    python deploy/aurora-admin/aurora_admin.py respaldar hospital-x
    python deploy/aurora-admin/aurora_admin.py pausar hospital-x | reactivar hospital-x
    python deploy/aurora-admin/aurora_admin.py baja hospital-x --confirmar hospital-x [--borrar-datos]

Credenciales: perfil `aurora` (aws login --remote --region us-east-2 --profile aurora). Si boto3 no las encuentra:
    eval "$(aws configure export-credentials --profile aurora --format env)"

Clave de operador: todo comando la pide (sin mostrarla). La primera vez se define con
    python deploy/aurora-admin/aurora_admin.py configurar-clave
En Parameter Store solo queda su huella (scrypt con sal, cifrada) en /aurora-admin/clave-operador; la clave no se
guarda en ningún lado. Protege la herramienta, no la cuenta de AWS: quien tenga credenciales con permisos completos
podría usar la consola directamente, así que el acceso al proyecto de AWS debe estar igual de controlado.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "institucion.yaml"
REGION = "us-east-2"
ZONE_ID = "Z0628464DNWEOT5ICYNC"  # auroracare.cl
BASE_DOMAIN = "auroracare.cl"
IMAGE_PREFIX = "ghcr.io/conefe/proyecto-aurora"
STACK_PREFIX = "aurora-inst-"
TAG = "aurora:institucion"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,28}[a-z0-9]$")
# Nombres reservados: la demostración actual y nombres de infraestructura
RESERVED = {"demo", "www", "api", "admin", "mail", "prod"}
SECRET_KEYS = ("POSTGRES_PASSWORD", "SECRET_KEY", "ENCRYPTION_KEY", "AURORA_ADMIN_PASSWORD")
OPERATOR_KEY_PARAM = "/aurora-admin/clave-operador"
OPERATOR_KEY_MIN = 12
SCRYPT = {"n": 2**15, "r": 8, "p": 1, "maxmem": 64 * 1024 * 1024, "dklen": 32}


def fail(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def stack_name(inst: str) -> str:
    return f"{STACK_PREFIX}{inst}"


def param_path(inst: str) -> str:
    return f"/aurora/{inst}/"


def rut_ok(rut: str) -> bool:
    clean = rut.replace(".", "").upper()
    if not re.fullmatch(r"\d{7,8}-[\dK]", clean):
        return False
    body, dv = clean.split("-")
    total, factor = 0, 2
    for d in reversed(body):
        total += int(d) * factor
        factor = 2 if factor == 7 else factor + 1
    expected = 11 - total % 11
    return dv == {11: "0", 10: "K"}.get(expected, str(expected))


class Aws:
    def __init__(self, profile: str | None, region: str):
        try:
            session = boto3.Session(profile_name=profile, region_name=region) if profile else boto3.Session(region_name=region)
            self.account = session.client("sts").get_caller_identity()["Account"]
        except (NoCredentialsError, ClientError) as exc:
            fail(f"sin credenciales de AWS válidas ({exc}). Vea el encabezado de este archivo.")
        except Exception as exc:  # perfil inexistente u otro problema de configuración
            fail(f"no se pudo abrir la sesión de AWS: {exc}")
        self.cfn = session.client("cloudformation")
        self.ssm = session.client("ssm")
        self.ec2 = session.client("ec2")
        self.s3 = session.client("s3")

    # --- Parameter Store -------------------------------------------------------------------------
    def params(self, inst: str, decrypt: bool = False) -> dict[str, str]:
        out: dict[str, str] = {}
        for page in self.ssm.get_paginator("get_parameters_by_path").paginate(
            Path=param_path(inst), WithDecryption=decrypt
        ):
            for p in page["Parameters"]:
                out[p["Name"].rsplit("/", 1)[1]] = p["Value"]
        return out

    def put(self, inst: str, key: str, value: str, secret: bool, overwrite: bool = False) -> None:
        self.ssm.put_parameter(
            Name=f"{param_path(inst)}{key}",
            Value=value,
            Type="SecureString" if secret else "String",
            Overwrite=overwrite,
            **({} if overwrite else {"Tags": [{"Key": TAG, "Value": inst}]}),
        )

    def delete_params(self, inst: str) -> int:
        names = [f"{param_path(inst)}{k}" for k in self.params(inst)]
        for i in range(0, len(names), 10):
            self.ssm.delete_parameters(Names=names[i : i + 10])
        return len(names)

    # --- CloudFormation --------------------------------------------------------------------------
    def stack(self, inst: str) -> dict | None:
        try:
            return self.cfn.describe_stacks(StackName=stack_name(inst))["Stacks"][0]
        except ClientError as exc:
            if "does not exist" in str(exc):
                return None
            raise

    def outputs(self, inst: str) -> dict[str, str]:
        st = self.stack(inst)
        return {o["OutputKey"]: o["OutputValue"] for o in (st or {}).get("Outputs", [])}

    def institutions(self) -> list[str]:
        names = []
        for page in self.cfn.get_paginator("describe_stacks").paginate():
            for st in page["Stacks"]:
                if st["StackName"].startswith(STACK_PREFIX) and st["StackStatus"] != "DELETE_COMPLETE":
                    names.append(st["StackName"][len(STACK_PREFIX) :])
        return sorted(names)

    # --- Comandos en el servidor (Session Manager) -----------------------------------------------
    def run(self, instance_id: str, script: str, timeout: int = 900) -> tuple[str, str, str]:
        cmd = self.ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": [script], "executionTimeout": [str(timeout)]},
        )["Command"]["CommandId"]
        deadline = time.time() + timeout + 60
        while time.time() < deadline:
            time.sleep(5)
            try:
                inv = self.ssm.get_command_invocation(CommandId=cmd, InstanceId=instance_id)
            except ClientError:
                continue
            if inv["Status"] not in ("Pending", "InProgress", "Delayed"):
                return inv["Status"], inv["StandardOutputContent"], inv["StandardErrorContent"]
        return "TimedOut", "", ""


def as_ec2_user(script: str) -> str:
    """Envuelve un script para ejecutarlo como ec2-user en /opt/aurora."""
    body = "set -euo pipefail\ncd /opt/aurora\n" + script
    return "sudo -u ec2-user bash -lc " + "'" + body.replace("'", "'\"'\"'") + "'"


DC = "docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml --env-file deploy/.env"


# --- Clave de operador ---------------------------------------------------------------------------
def _hash_key(key: str, salt: bytes) -> bytes:
    return hashlib.scrypt(key.encode(), salt=salt, **SCRYPT)


def _read_key(prompt: str) -> str:
    if not sys.stdin.isatty():
        fail("la clave de operador se ingresa en una terminal interactiva.")
    return getpass.getpass(prompt)


def _stored_key(aws: Aws) -> dict | None:
    try:
        raw = aws.ssm.get_parameter(Name=OPERATOR_KEY_PARAM, WithDecryption=True)["Parameter"]["Value"]
    except ClientError as exc:
        if "ParameterNotFound" in str(exc):
            return None
        raise
    return json.loads(raw)


def require_operator_key(aws: Aws) -> None:
    stored = _stored_key(aws)
    if stored is None:
        fail("todavía no hay clave de operador. Defínala con: aurora_admin.py configurar-clave")
    salt = base64.b64decode(stored["salt"])
    expected = base64.b64decode(stored["hash"])
    for attempt in range(3):
        if hmac.compare_digest(_hash_key(_read_key("Clave de operador: "), salt), expected):
            return
        time.sleep(2 * (attempt + 1))
        print("Clave incorrecta.", file=sys.stderr)
    fail("demasiados intentos.")


def cmd_configurar_clave(aws: Aws, a: argparse.Namespace) -> None:
    if _stored_key(aws) is not None:
        print("Ya hay una clave de operador: para cambiarla, ingrese primero la actual.")
        require_operator_key(aws)
    new = _read_key(f"Nueva clave de operador (mínimo {OPERATOR_KEY_MIN} caracteres): ")
    if len(new) < OPERATOR_KEY_MIN:
        fail(f"la clave debe tener al menos {OPERATOR_KEY_MIN} caracteres.")
    if _read_key("Repítala: ") != new:
        fail("las claves no coinciden.")
    salt = os.urandom(16)
    value = json.dumps({"alg": "scrypt", **{k: SCRYPT[k] for k in ("n", "r", "p")},
                        "salt": base64.b64encode(salt).decode(), "hash": base64.b64encode(_hash_key(new, salt)).decode()})
    aws.ssm.put_parameter(Name=OPERATOR_KEY_PARAM, Value=value, Type="SecureString", Overwrite=True)
    print("Clave de operador guardada (solo su huella). Si la olvida, otra persona con acceso al proyecto de AWS")
    print(f"puede borrar {OPERATOR_KEY_PARAM} y definir una nueva.")


# --- Comandos ------------------------------------------------------------------------------------
def cmd_inscribir(aws: Aws, a: argparse.Namespace) -> None:
    inst = a.institucion
    if not ID_RE.match(inst) or inst in RESERVED:
        fail("el identificador debe tener 3 a 30 caracteres: minúsculas, números y guiones (y no ser reservado).")
    if not rut_ok(a.admin_rut):
        fail("el RUT del ADMIN no es válido.")
    if aws.stack(inst):
        fail(f"la institución «{inst}» ya existe (pila {stack_name(inst)}).")
    if aws.params(inst):
        fail(f"ya hay parámetros en {param_path(inst)}. Si quedaron de una baja incompleta, bórrelos antes.")
    domain = a.dominio or f"{inst}.{BASE_DOMAIN}"

    print(f"1/3 Guardando configuración y secretos en Parameter Store ({param_path(inst)})…")
    fernet_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
    secret_values = {
        "POSTGRES_PASSWORD": secrets.token_urlsafe(32),
        "SECRET_KEY": secrets.token_urlsafe(48),
        "ENCRYPTION_KEY": fernet_key,
        # Temporal: el ADMIN debe cambiarla en su primer ingreso
        "AURORA_ADMIN_PASSWORD": "Aurora-" + secrets.token_urlsafe(9) + "7",
    }
    plain_values = {
        "AURORA_IMAGE_PREFIX": a.imagenes,
        "AURORA_VERSION": a.version,
        "AURORA_ADMIN_RUT": a.admin_rut,
        "AURORA_ADMIN_EMAIL": a.admin_email,
        "AURORA_ADMIN_NAME": a.admin_nombre,
        "INFERENCE_PROVIDER": a.modelo,
        "INFERENCE_URL": a.modelo_url or "-",
    }
    if a.modelo == "http":
        if not a.modelo_url:
            fail("con --modelo http hay que indicar --modelo-url.")
        import getpass

        token = getpass.getpass("Token del modelo (INFERENCE_API_TOKEN, no se muestra): ").strip()
        if token:
            secret_values["INFERENCE_API_TOKEN"] = token
    for k, v in secret_values.items():
        aws.put(inst, k, v, secret=True)
    for k, v in plain_values.items():
        aws.put(inst, k, v, secret=False)

    print(f"2/3 Creando la pila {stack_name(inst)} (servidor, IP, bucket, rol y DNS {domain})…")
    aws.cfn.create_stack(
        StackName=stack_name(inst),
        TemplateBody=TEMPLATE.read_text(),
        Parameters=[
            {"ParameterKey": "InstitutionId", "ParameterValue": inst},
            {"ParameterKey": "DomainName", "ParameterValue": domain},
            {"ParameterKey": "HostedZoneId", "ParameterValue": a.zona},
            {"ParameterKey": "InstanceType", "ParameterValue": a.tipo},
            {"ParameterKey": "RepoRef", "ParameterValue": a.ref},
        ],
        Capabilities=["CAPABILITY_IAM"],
        Tags=[{"Key": TAG, "Value": inst}],
        OnFailure="DO_NOTHING" if a.conservar_si_falla else "ROLLBACK",
    )
    print("3/3 Esperando la instalación (10 a 20 minutos; la pila termina cuando Aurora responde)…")
    try:
        aws.cfn.get_waiter("stack_create_complete").wait(
            StackName=stack_name(inst), WaiterConfig={"Delay": 20, "MaxAttempts": 120}
        )
    except Exception:
        events = aws.cfn.describe_stack_events(StackName=stack_name(inst))["StackEvents"]
        reasons = [f"{e['LogicalResourceId']}: {e.get('ResourceStatusReason', '')}" for e in events if "FAILED" in e["ResourceStatus"]]
        print("La creación falló:", *reasons[:5], sep="\n  ")
        print(f"Los parámetros de {param_path(inst)} quedaron; use «baja {inst} --confirmar {inst}» para limpiar.")
        sys.exit(1)

    out = aws.outputs(inst)
    print(f"\nListo: {out.get('Url')}  (IP {out.get('PublicIp')}, servidor {out.get('InstanceId')}, bucket {out.get('Bucket')})")
    print("El certificado HTTPS se emite en los primeros minutos, cuando el DNS ya resuelve.")
    print(f"Contraseña temporal del ADMIN: python deploy/aurora-admin/aurora_admin.py clave-admin {inst}")
    print("Entréguela por un canal privado; el ADMIN debe cambiarla en su primer ingreso.")


def cmd_listar(aws: Aws, a: argparse.Namespace) -> None:
    insts = aws.institutions()
    if not insts:
        print("No hay instituciones inscritas.")
        return
    print(f"{'Institución':<20} {'Estado de la pila':<22} {'Servidor':<10} {'Versión':<20} URL")
    for inst in insts:
        st = aws.stack(inst) or {}
        out = {o["OutputKey"]: o["OutputValue"] for o in st.get("Outputs", [])}
        state = "—"
        if out.get("InstanceId"):
            res = aws.ec2.describe_instances(InstanceIds=[out["InstanceId"]])["Reservations"]
            state = res[0]["Instances"][0]["State"]["Name"] if res else "—"
        version = aws.params(inst).get("AURORA_VERSION", "—")
        print(f"{inst:<20} {st.get('StackStatus', '—'):<22} {state:<10} {version[:19]:<20} {out.get('Url', '—')}")


def cmd_clave_admin(aws: Aws, a: argparse.Namespace) -> None:
    value = aws.params(a.institucion, decrypt=True).get("AURORA_ADMIN_PASSWORD")
    if not value:
        fail("no hay contraseña temporal guardada para esa institución.")
    print("No la pegue en chats ni correos: entréguela por un canal privado.")
    print(value)


def instance_of(aws: Aws, inst: str) -> str:
    iid = aws.outputs(inst).get("InstanceId")
    if not iid:
        fail(f"la institución «{inst}» no existe o su pila no terminó.")
    return iid


def cmd_actualizar(aws: Aws, a: argparse.Namespace) -> None:
    targets = aws.institutions() if a.todas else [a.institucion]
    if not targets or targets == [None]:
        fail("indique una institución o --todas.")
    for inst in targets:
        iid = instance_of(aws, inst)
        aws.put(inst, "AURORA_VERSION", a.version, secret=False, overwrite=True)
        script = as_ec2_user(
            f"""git fetch --quiet origin {a.ref} && git checkout --quiet FETCH_HEAD
sed -i -E 's|^AURORA_VERSION=.*|AURORA_VERSION={a.version}|' deploy/.env
{DC} pull --quiet backend web
{DC} up -d backend web
for i in $(seq 1 40); do [ "$(docker inspect -f '{{{{.State.Health.Status}}}}' aurora-backend-1)" = healthy ] && break; sleep 5; done
docker inspect -f '{{{{.State.Health.Status}}}}' aurora-backend-1
grep -E '^AURORA_VERSION=' deploy/.env"""
        )
        status, out, err = aws.run(iid, script)
        print(f"[{inst}] {status}\n{out.strip()}\n{err.strip()[-800:]}")


def cmd_respaldar(aws: Aws, a: argparse.Namespace) -> None:
    status, out, err = aws.run(instance_of(aws, a.institucion), as_ec2_user("./deploy/backup_db.sh 2>&1 | tail -3"))
    print(f"{status}\n{out.strip()}\n{err.strip()[-800:]}")


def cmd_pausar(aws: Aws, a: argparse.Namespace) -> None:
    aws.ec2.stop_instances(InstanceIds=[instance_of(aws, a.institucion)])
    print("Servidor detenido. La IP fija y el disco siguen cobrando (≈ USD 4 al mes). «reactivar» lo enciende.")


def cmd_reactivar(aws: Aws, a: argparse.Namespace) -> None:
    aws.ec2.start_instances(InstanceIds=[instance_of(aws, a.institucion)])
    print("Servidor encendido. Aurora arranca sola en un par de minutos.")


def empty_and_delete_bucket(aws: Aws, bucket: str) -> None:
    for page in aws.s3.get_paginator("list_object_versions").paginate(Bucket=bucket):
        objs = [{"Key": v["Key"], "VersionId": v["VersionId"]} for v in page.get("Versions", []) + page.get("DeleteMarkers", [])]
        for i in range(0, len(objs), 1000):
            aws.s3.delete_objects(Bucket=bucket, Delete={"Objects": objs[i : i + 1000], "Quiet": True})
    aws.s3.delete_bucket(Bucket=bucket)


def cmd_baja(aws: Aws, a: argparse.Namespace) -> None:
    inst = a.institucion
    if a.confirmar != inst:
        fail(f"para dar de baja repita el identificador: --confirmar {inst}")
    st = aws.stack(inst)
    bucket = aws.outputs(inst).get("Bucket")
    if st and not a.sin_respaldo and aws.outputs(inst).get("InstanceId"):
        print("Respaldo final…")
        status, out, _ = aws.run(instance_of(aws, inst), as_ec2_user("./deploy/backup_db.sh 2>&1 | tail -2"), timeout=600)
        print(f"  {status}: {out.strip()}")
    if st:
        print(f"Borrando la pila {stack_name(inst)} (servidor, IP, rol y DNS)…")
        aws.cfn.delete_stack(StackName=stack_name(inst))
        aws.cfn.get_waiter("stack_delete_complete").wait(StackName=stack_name(inst), WaiterConfig={"Delay": 15, "MaxAttempts": 80})
    print(f"Parámetros borrados: {aws.delete_params(inst)}")
    if bucket:
        if a.borrar_datos:
            empty_and_delete_bucket(aws, bucket)
            print(f"Bucket {bucket} vaciado y borrado.")
        else:
            print(f"El bucket {bucket} se conserva con las imágenes y los respaldos (borrarlo: --borrar-datos).")
    print("Baja completa.")


def main() -> None:
    ap = argparse.ArgumentParser(prog="aurora-admin", description="Instancias de Aurora Care por institución")
    ap.add_argument("--perfil", default=os.environ.get("AWS_PROFILE", "aurora"), help="perfil de AWS (vacío: variables de entorno)")
    ap.add_argument("--region", default=REGION)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("configurar-clave", help="define o cambia la clave de operador")
    p.set_defaults(fn=cmd_configurar_clave)

    p = sub.add_parser("inscribir", help="crea la instancia de una institución")
    p.add_argument("institucion")
    p.add_argument("--version", required=True, help="tag de imagen publicado (sha-<commit> o vX.Y.Z)")
    p.add_argument("--admin-rut", required=True)
    p.add_argument("--admin-email", required=True)
    p.add_argument("--admin-nombre", required=True)
    p.add_argument("--dominio", help=f"por defecto <institución>.{BASE_DOMAIN}")
    p.add_argument("--zona", default=ZONE_ID, help="zona de Route 53 del dominio")
    p.add_argument("--tipo", default="t4g.micro", choices=["t4g.micro", "t4g.small", "t4g.medium"])
    p.add_argument("--ref", default="main", help="rama o commit del repositorio para Compose y scripts")
    p.add_argument("--imagenes", default=IMAGE_PREFIX)
    p.add_argument("--modelo", default="simulated", choices=["simulated", "http"])
    p.add_argument("--modelo-url")
    p.add_argument("--conservar-si-falla", action="store_true", help="no revertir la pila si falla (para diagnosticar)")
    p.set_defaults(fn=cmd_inscribir)

    p = sub.add_parser("listar", help="instituciones con su estado y versión")
    p.set_defaults(fn=cmd_listar)

    p = sub.add_parser("clave-admin", help="muestra la contraseña temporal del primer ADMIN")
    p.add_argument("institucion")
    p.set_defaults(fn=cmd_clave_admin)

    p = sub.add_parser("actualizar", help="cambia la versión de una institución o de todas")
    p.add_argument("institucion", nargs="?")
    p.add_argument("--todas", action="store_true")
    p.add_argument("--version", required=True)
    p.add_argument("--ref", default="main")
    p.set_defaults(fn=cmd_actualizar)

    p = sub.add_parser("respaldar", help="respaldo inmediato de la base al bucket de la institución")
    p.add_argument("institucion")
    p.set_defaults(fn=cmd_respaldar)

    for name, fn, hlp in (("pausar", cmd_pausar, "detiene el servidor"), ("reactivar", cmd_reactivar, "enciende el servidor")):
        p = sub.add_parser(name, help=hlp)
        p.add_argument("institucion")
        p.set_defaults(fn=fn)

    p = sub.add_parser("baja", help="respaldo final y borrado de la instancia")
    p.add_argument("institucion")
    p.add_argument("--confirmar", required=True, help="repita el identificador")
    p.add_argument("--borrar-datos", action="store_true", help="vacía y borra también el bucket (irreversible)")
    p.add_argument("--sin-respaldo", action="store_true")
    p.set_defaults(fn=cmd_baja)

    a = ap.parse_args()
    aws = Aws(a.perfil or None, a.region)
    if a.fn is not cmd_configurar_clave:
        require_operator_key(aws)
    a.fn(aws, a)


if __name__ == "__main__":
    main()
