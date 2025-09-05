## backend/src/db/init_db.py
from .base_class import Base
from .session import engine
from ..auth import models as auth_models
from ..farmer import models as farmer_models
from ..auditor import models as auditor_models
from ..uploads import models as uploads_models
from ..iot import models as iot_models
from ..mrv import models as mrv_models

def init_db():
    Base.metadata.create_all(bind=engine)
    _seed_roles_and_users()


def _seed_roles_and_users():
    from .session import SessionLocal
    db = SessionLocal()
    try:
        # Seed roles
        role_names = ["admin", "auditor", "farmer", "fpo"]
        existing = {r.name for r in db.query(auth_models.Role).all()}
        for rn in role_names:
            if rn not in existing:
                db.add(auth_models.Role(name=rn, description=f"{rn} role"))
        db.commit()

        # Seed default admin/auditor if none
        admin_role = db.query(auth_models.Role).filter(auth_models.Role.name == "admin").first()
        auditor_role = db.query(auth_models.Role).filter(auth_models.Role.name == "auditor").first()
        if db.query(auth_models.User).count() == 0 and admin_role:
            from src.utils.hashing import hash_password
            db.add(auth_models.User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                is_active=True,
                is_superuser=True,
                role_id=admin_role.id,
            ))
        if auditor_role and not db.query(auth_models.User).filter(auth_models.User.email == "auditor@example.com").first():
            from src.utils.hashing import hash_password
            db.add(auth_models.User(
                username="auditor",
                email="auditor@example.com",
                hashed_password=hash_password("auditor123"),
                is_active=True,
                is_superuser=False,
                role_id=auditor_role.id,
            ))
        db.commit()
    finally:
        db.close()
