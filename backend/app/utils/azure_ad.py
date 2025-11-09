import time
from typing import Any, Dict, List, Optional

import requests
from jose import jwk, jwt
from jose.utils import base64url_decode


class AzureADVerificationError(Exception):
    """Raised when an Azure AD token fails validation."""


class AzureADVerifier:
    """Validates Azure AD issued JWT access tokens."""

    def __init__(self, tenant_id: str, audiences: List[str]) -> None:
        if not tenant_id:
            raise ValueError("Azure AD tenant ID is required")
        if not audiences:
            raise ValueError("At least one allowed audience is required")

        self._tenant_id = tenant_id
        self._audiences = audiences
        self._issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        self._openid_config_url = f"{self._issuer}/.well-known/openid-configuration"

        self._jwks_uri: Optional[str] = None
        self._signing_keys: Dict[str, Dict[str, Any]] = {}
        self._signing_keys_expires_at = 0.0

    def _load_openid_configuration(self) -> None:
        response = requests.get(self._openid_config_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        self._jwks_uri = data.get("jwks_uri")
        if not self._jwks_uri:
            raise AzureADVerificationError("JWKS URI not found in OpenID configuration")

    def _refresh_signing_keys(self, force: bool = False) -> None:
        now = time.time()
        if not force and now < self._signing_keys_expires_at and self._signing_keys:
            return

        if not self._jwks_uri:
            self._load_openid_configuration()

        if not self._jwks_uri:
            raise AzureADVerificationError("JWKS URI unavailable")

        response = requests.get(self._jwks_uri, timeout=5)
        response.raise_for_status()
        jwks = response.json()
        keys = jwks.get("keys", [])
        self._signing_keys = {key["kid"]: key for key in keys if "kid" in key}
        # cache keys for one hour by default
        self._signing_keys_expires_at = now + 3600

    def _get_signing_key(self, kid: str) -> Dict[str, Any]:
        self._refresh_signing_keys()
        key = self._signing_keys.get(kid)
        if key:
            return key
        # Refresh once more in case of rollover
        self._refresh_signing_keys(force=True)
        key = self._signing_keys.get(kid)
        if not key:
            raise AzureADVerificationError("Signing key not found for token")
        return key

    def validate(self, token: str) -> Dict[str, Any]:
        if not token:
            raise AzureADVerificationError("Token missing")

        try:
            header = jwt.get_unverified_header(token)
        except Exception as exc:
            raise AzureADVerificationError("Invalid token header") from exc

        kid = header.get("kid")
        if not kid:
            raise AzureADVerificationError("Token missing key identifier (kid)")

        key_data = self._get_signing_key(kid)
        signing_key = jwk.construct(key_data)

        message, encoded_signature = token.rsplit(".", 1)
        decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

        if not signing_key.verify(message.encode("utf-8"), decoded_signature):
            raise AzureADVerificationError("Token signature validation failed")

        try:
            claims = jwt.get_unverified_claims(token)
        except Exception as exc:
            raise AzureADVerificationError("Unable to parse token claims") from exc

        now = time.time()
        exp = claims.get("exp")
        if exp and now > float(exp):
            raise AzureADVerificationError("Token has expired")

        nbf = claims.get("nbf")
        if nbf and now < float(nbf):
            raise AzureADVerificationError("Token not yet valid")

        aud = claims.get("aud")
        audiences = [aud] if isinstance(aud, str) else aud or []
        if not any(audience in self._audiences for audience in audiences):
            raise AzureADVerificationError("Token audience not allowed")

        issuer = claims.get("iss")
        if issuer != self._issuer:
            raise AzureADVerificationError("Token issuer mismatch")

        return claims


