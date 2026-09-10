import bcrypt
from database import SessionLocal, Admin

def create_admin():
    db = SessionLocal()
    
    username = "admin"
    password = "architekt2026"  # ← Ändere das später!
    
    # Prüfen, ob Admin schon existiert
    existing = db.query(Admin).filter(Admin.username == username).first()
    if existing:
        print(f"❌ Admin '{username}' existiert bereits.")
        db.close()
        return
    
    # Passwort hashen (bcrypt direkt)
    password_bytes = password.encode('utf-8')
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    # Admin anlegen
    admin = Admin(username=username, password_hash=password_hash)
    db.add(admin)
    db.commit()
    db.close()
    
    print(f"✅ Admin '{username}' erfolgreich angelegt!")
    print(f"   Passwort: {password}")

if __name__ == "__main__":
    create_admin()