
from app.core.security import create_access_token


if __name__ == "__main__":
    token = create_access_token(user_id=1)
    print(token)