from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    pwd = "SecretPassword123!"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_tokens():
    user_id = 99
    access_token = create_access_token(user_id, is_superuser=True)
    decoded = decode_token(access_token, expected_type="access")

    assert decoded["sub"] == "99"
    assert decoded["is_superuser"] is True
    assert decoded["type"] == "access"

    refresh_token = create_refresh_token(user_id)
    decoded_ref = decode_token(refresh_token, expected_type="refresh")
    assert decoded_ref["type"] == "refresh"
