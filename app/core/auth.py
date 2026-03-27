import asyncio
import os
from dataclasses import dataclass

import requests
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    sub: str
    username: str | None = None
    email: str | None = None
    name: str | None = None


class KeycloakTokenVerifier:
    def __init__(self, *, base_url: str, realm: str, client_id: str, client_secret: str):
        self.base_url = base_url.rstrip("/")
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret

    @classmethod
    def from_env(cls) -> "KeycloakTokenVerifier":
        base_url = os.getenv("KEYCLOAK_URL") or os.getenv("VITE_KEYCLOAK_URL")
        realm = os.getenv("KEYCLOAK_REALM") or os.getenv("VITE_REALM")
        client_id = os.getenv("KEYCLOAK_ADMIN_CLIENT_ID")
        client_secret = os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET")

        missing = [
            name
            for name, value in [
                ("KEYCLOAK_URL", base_url),
                ("KEYCLOAK_REALM", realm),
                ("KEYCLOAK_ADMIN_CLIENT_ID", client_id),
                ("KEYCLOAK_ADMIN_CLIENT_SECRET", client_secret),
            ]
            if not value
        ]

        if missing:
            raise RuntimeError("Missing Keycloak auth env vars: " + ", ".join(missing))

        return cls(
            base_url=base_url,
            realm=realm,
            client_id=client_id,
            client_secret=client_secret,
        )

    def _introspection_url(self) -> str:
        return f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/token/introspect"

    def introspect_token(self, token: str) -> AuthenticatedUser:
        response = requests.post(
            self._introspection_url(),
            data={
                "token": token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()

        if not payload.get("active"):
            raise HTTPException(status_code=401, detail="Token invalido ou expirado.")

        subject = payload.get("sub")
        if not subject:
            raise HTTPException(status_code=401, detail="Token sem sujeito valido.")

        return AuthenticatedUser(
            sub=subject,
            username=payload.get("preferred_username"),
            email=payload.get("email"),
            name=payload.get("name"),
        )


async def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None,
) -> AuthenticatedUser:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authorization bearer token is required.")

    verifier = KeycloakTokenVerifier.from_env()
    return await asyncio.to_thread(verifier.introspect_token, credentials.credentials)


async def require_authenticated_request(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser:
    return await require_authenticated_user(credentials)


def ensure_same_user(authenticated_user: AuthenticatedUser, user_id: str) -> None:
    if authenticated_user.sub != user_id:
        raise HTTPException(status_code=403, detail="Voce nao pode modificar dados de outro usuario.")
