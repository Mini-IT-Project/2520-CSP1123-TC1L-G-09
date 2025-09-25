import getpass
from extensions import db
from login import Users
from werkzeug.security import generate_password_hash
from app import create_app  

app=create_app()

with app.app_context():
    email = input("please enter your admin email (exp:xxx@student.mmu.edu.my): ").strip()
    password = getpass.getpass("Please enter your password: ").strip() 

    if not email or not password:
        print(" Email and password cannot be empty")
        exit()

    elif not email.endswith("@student.mmu.edu.my"):
        print("Invalid email. Must end with @student.mmu.edu.my")
        exit()

    else:
        existing = Users.query.filter_by(email=email).first()
        if existing:
            if existing.is_admin:
                print(f"The admin account already exists: {email}")
            else:
                existing.is_admin = True
                db.session.commit()
                print(f" User {email} promoted to administrator")
        else:
            admin_user = Users(
                email=email,
                password=generate_password_hash(password),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"✅ Admin account create successfully: {email}")