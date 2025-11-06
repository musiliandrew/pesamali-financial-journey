import jwt
from datetime import datetime, timedelta, timezone
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from django.conf import settings
from .models import Users


def generate_jwt(user: Users, expires_minutes: int = 60 * 24 * 7) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def verify_jwt(token: str) -> Users:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        return Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        raise exceptions.AuthenticationFailed("user not found")
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed("token expired")
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed("invalid token")


class JWTAuthentication(BaseAuthentication):
    keyword = b"Bearer"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower():
            return None
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed("Invalid Authorization header")
        token = auth[1].decode()
        user = verify_jwt(token)
        return (user, None)
