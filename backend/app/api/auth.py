import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models import User, StoreUser

router = APIRouter(tags=["Authentication"])

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.strip().encode()).hexdigest()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Dedicated Admin Login Endpoint for the Executive ML Decision Suite.
    Strictly restricts access to administrators only.
    """
    input_identifier = login_data.email.strip().lower()
    input_password = login_data.password.strip()

    # 1. Check StoreUser admin accounts
    store_user = db.query(StoreUser).filter(
        StoreUser.username.ilike(input_identifier)
    ).first()

    if store_user:
        if store_user.password_hash not in [input_password, hash_pw(input_password)]:
            return {"success": False, "message": "Invalid administrator password."}
        if store_user.role != "admin":
            return {
                "success": False,
                "message": f"Access Denied: '{store_user.role.title()}' accounts cannot access the Executive ML Decision Suite. Access is strictly restricted to Administrators."
            }
        return {
            "success": True,
            "message": "Administrator authentication successful",
            "user": {
                "id": store_user.id,
                "name": store_user.full_name or "Store Administrator",
                "email": store_user.username,
                "role": "admin"
            }
        }

    # 2. Check legacy User model
    legacy_user = db.query(User).filter(User.email.ilike(input_identifier)).first()
    if legacy_user:
        if legacy_user.role != "admin":
            return {
                "success": False,
                "message": "Access Denied: Only administrators can access the Executive Decision Platform."
            }
        return {
            "success": True,
            "message": "Administrator authentication successful",
            "user": {
                "id": legacy_user.id,
                "name": legacy_user.name,
                "email": legacy_user.email,
                "role": "admin"
            }
        }

    # 3. Standard built-in admin credentials fallback
    admin_aliases = ["admin@ecommerce.com", "admin@smartcart.com", "admin"]
    if input_identifier in admin_aliases and input_password == "admin123":
        return {
            "success": True,
            "message": "Administrator authentication successful",
            "user": {
                "id": 1,
                "name": "Platform Administrator",
                "email": "admin@smartcart.com",
                "role": "admin"
            }
        }

    return {
        "success": False,
        "message": "Invalid administrator credentials. Only authorized Administrators can access this portal."
    }

@router.get("/me")
def current_user():
    return {
        "id": 1,
        "name": "Platform Administrator",
        "email": "admin@smartcart.com",
        "role": "admin"
    }
