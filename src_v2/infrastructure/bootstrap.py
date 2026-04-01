import uuid

import bcrypt


def ensure_default_admin(conn) -> None:
    existing = conn.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
    if existing:
        return
    password_hash = bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode("utf-8")
    conn.execute(
        """
        INSERT INTO users (id, username, password_hash, role, is_active)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), "admin", password_hash, "admin", 1),
    )
    conn.commit()
