import jwt


def make_round_trip():
    secret = "my secret"
    payload = {
        "sub": "something"
    }
    token = jwt.encode(payload, key=secret)
    decoded_token = jwt.decode(token, key=secret)
    assert payload == decoded_token


if __name__ == "__main__":
    make_round_trip()
