from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

engine = create_engine(settings.DB_DSN, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pool aparte, pequeño y con espera corta, para las escrituras auxiliares del middleware (métricas y errores).
# Cada solicitud retiene su conexión del pool principal hasta enviar la respuesta; si el middleware pidiera
# otra conexión a ese mismo pool, con el pool agotado todas las solicitudes esperarían entre sí (interbloqueo).
# Si este pool se satura, la métrica se descarta y queda en el log: nunca afecta la respuesta.
aux_engine = create_engine(settings.DB_DSN, pool_pre_ping=True, pool_size=2, max_overflow=3, pool_timeout=5)
AuxSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=aux_engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
