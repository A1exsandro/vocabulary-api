import os

import requests


class KeycloakAdminClient:
    def __init__(
        self,
        *,
        base_url: str,
        realm: str,
        client_id: str,
        client_secret: str,
        admin_realm: str,
    ):
        self.base_url = base_url.rstrip("/")
        self.realm = realm
        self.client_id = client_id
        self.client_secret = client_secret
        self.admin_realm = admin_realm

    @classmethod
    def from_env(cls) -> "KeycloakAdminClient":
        base_url = os.getenv("KEYCLOAK_URL") or os.getenv("VITE_KEYCLOAK_URL")
        realm = os.getenv("KEYCLOAK_REALM") or os.getenv("VITE_REALM")
        client_id = os.getenv("KEYCLOAK_ADMIN_CLIENT_ID")
        client_secret = os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET")
        admin_realm = os.getenv("KEYCLOAK_ADMIN_REALM") or realm

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
            raise RuntimeError("Missing Keycloak admin env vars: " + ", ".join(missing))

        return cls(
            base_url=base_url,
            realm=realm,
            client_id=client_id,
            client_secret=client_secret,
            admin_realm=admin_realm,
        )

    def _token_url(self) -> str:
        return f"{self.base_url}/realms/{self.admin_realm}/protocol/openid-connect/token"

    def _users_url(self) -> str:
        return f"{self.base_url}/admin/realms/{self.realm}/users"

    def _get_access_token(self) -> str:
        response = requests.post(
            self._token_url(),
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=15,
        )
        response.raise_for_status()
        access_token = response.json().get("access_token")

        if not access_token:
            raise RuntimeError("Keycloak admin token response did not include access_token.")

        return access_token

    def _normalize_user(self, raw_user: dict) -> dict:
        first_name = (raw_user.get("firstName") or "").strip()
        last_name = (raw_user.get("lastName") or "").strip()
        username = (raw_user.get("username") or "").strip() or None
        email = (raw_user.get("email") or "").strip() or None
        full_name = " ".join(part for part in [first_name, last_name] if part).strip()

        return {
            "id": raw_user.get("id"),
            "name": full_name or username or email or "Usuario",
            "username": username,
            "email": email,
            "enabled": bool(raw_user.get("enabled", True)),
        }

    def list_users(self) -> list[dict]:
        access_token = self._get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        users: list[dict] = []
        first = 0
        page_size = 100

        while True:
            response = requests.get(
                self._users_url(),
                headers=headers,
                params={"first": first, "max": page_size},
                timeout=15,
            )
            response.raise_for_status()
            batch = response.json()

            if not batch:
                break

            users.extend(self._normalize_user(user) for user in batch if user.get("id"))

            if len(batch) < page_size:
                break

            first += len(batch)

        return users

    def get_user_by_id(self, user_id: str) -> dict | None:
        access_token = self._get_access_token()
        response = requests.get(
            f"{self._users_url()}/{user_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return self._normalize_user(response.json())
