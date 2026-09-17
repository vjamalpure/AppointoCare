from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

def generate_access_token(user_id, role, extra_claims=None, expires_delta=None):
    """
    Generate an access token with user identity and role.
    """
    additional_claims = {"role": role}
    if extra_claims:
        additional_claims.update(extra_claims)

    return create_access_token(
        identity=str(user_id),
        additional_claims=additional_claims,
        expires_delta=expires_delta or timedelta(hours=1)
    )


def generate_refresh_token(user_id, role, extra_claims=None):
    """
    Generate a refresh token for the user.
    """
    additional_claims = {"role": role}
    if extra_claims:
        additional_claims.update(extra_claims)

    return create_refresh_token(
        identity=str(user_id),
        additional_claims=additional_claims
    )
