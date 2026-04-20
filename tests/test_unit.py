from app.utils.auth import serialize_token, deserialize_token

def test_serialize_token():
    token = serialize_token("heisenberg")
    assert token is not None
    assert isinstance(token, str)

def test_deserialize_token_valid():
    token = serialize_token("heisenberg")
    username = deserialize_token(token)
    assert username == "heisenberg"

def test_deserialize_token_invalid():
    username = deserialize_token("invalid.token.here")
    assert username is None

def test_deserialize_token_empty():
    username = deserialize_token("")
    assert username is None
