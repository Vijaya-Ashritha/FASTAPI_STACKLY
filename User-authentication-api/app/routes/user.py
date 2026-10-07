
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from passlib.context import CryptContext

from app.database import get_connection
from app.schemas import (
    PasswordUpdate,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)


router = APIRouter(tags=["Users"])


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# REGISTER USER
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register_user(user: UserCreate):

    connection = get_connection()

    # Check whether email already exists
    existing_user = connection.execute(
        "SELECT * FROM users WHERE email = ?",
        (user.email,),
    ).fetchone()

    if existing_user:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    # Hash the password before storing it
    hashed_password = password_context.hash(user.password)

    # Get current date and time
    created_date = datetime.now(timezone.utc).isoformat()

    # Insert user into database
    cursor = connection.execute(
        """
        INSERT INTO users
        (full_name, email, phone_number, password, role, created_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user.full_name,
            user.email,
            user.phone_number,
            hashed_password,
            user.role.value,
            created_date,
        ),
    )

    connection.commit()

    # Get generated user ID
    user_id = cursor.lastrowid

    # Get newly created user
    new_user = connection.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    connection.close()

    # Convert SQLite Row to dictionary
    return dict(new_user)


# LOGIN USER
@router.post("/login")
def login_user(user: UserLogin):

    connection = get_connection()

    # Find user using email
    existing_user = connection.execute(
        "SELECT * FROM users WHERE email = ?",
        (user.email,),
    ).fetchone()

    connection.close()

    # Check whether email exists
    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # Verify password
    password_is_correct = password_context.verify(
        user.password,
        existing_user["password"],
    )

    if not password_is_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return {
        "message": "Login successful",
        "user_id": existing_user["user_id"],
        "full_name": existing_user["full_name"],
        "email": existing_user["email"],
        "role": existing_user["role"],
    }


# GET ALL USERS
@router.get(
    "/users",
    response_model=list[UserResponse],
)
def get_users(
    role: str | None = Query(default=None),
    name: str | None = Query(default=None),
):

    connection = get_connection()

    query = "SELECT * FROM users"
    parameters = []

    # Filter by role
    if role:

        if role not in ["Admin", "User"]:
            connection.close()

            raise HTTPException(
                status_code=400,
                detail="Role must be Admin or User",
            )

        query = query + " WHERE role = ?"
        parameters.append(role)

    # Search by name
    if name:

        if "WHERE" in query:
            query = query + " AND full_name LIKE ?"
        else:
            query = query + " WHERE full_name LIKE ?"

        parameters.append("%" + name + "%")

    users = connection.execute(
        query,
        parameters,
    ).fetchall()

    connection.close()

    # Convert SQLite Rows to dictionaries
    return [dict(user) for user in users]


# GET USER BY ID
@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
)
def get_user(user_id: int):

    connection = get_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    connection.close()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Convert SQLite Row to dictionary
    return dict(user)


# UPDATE USER
@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    user: UserUpdate,
):

    connection = get_connection()

    # Check whether user exists
    existing_user = connection.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    if not existing_user:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Check whether email is already used
    email_user = connection.execute(
        """
        SELECT * FROM users
        WHERE email = ? AND user_id != ?
        """,
        (
            user.email,
            user_id,
        ),
    ).fetchone()

    if email_user:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    # Update user
    connection.execute(
        """
        UPDATE users
        SET full_name = ?,
            email = ?,
            phone_number = ?,
            role = ?
        WHERE user_id = ?
        """,
        (
            user.full_name,
            user.email,
            user.phone_number,
            user.role.value,
            user_id,
        ),
    )

    connection.commit()

    # Get updated user
    updated_user = connection.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    connection.close()

    # Convert SQLite Row to dictionary
    return dict(updated_user)


# DELETE USER
@router.delete(
    "/users/{user_id}",
    status_code=204,
)
def delete_user(user_id: int):

    connection = get_connection()

    # Check whether user exists
    existing_user = connection.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    if not existing_user:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Delete user
    connection.execute(
        "DELETE FROM users WHERE user_id = ?",
        (user_id,),
    )

    connection.commit()
    connection.close()

    return None


# CHANGE PASSWORD
@router.put(
    "/users/{user_id}/password",
)
def change_password(
    user_id: int,
    password_data: PasswordUpdate,
):

    connection = get_connection()

    # Check whether user exists
    existing_user = connection.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    if not existing_user:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Hash new password
    hashed_password = password_context.hash(
        password_data.password
    )

    # Update password
    connection.execute(
        """
        UPDATE users
        SET password = ?
        WHERE user_id = ?
        """,
        (
            hashed_password,
            user_id,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "message": "Password updated successfully"
    }