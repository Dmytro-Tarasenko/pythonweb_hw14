from unittest.mock import AsyncMock


def test_create_contact(client,
                        user,
                        get_access_token,
                        monkeypatch):

    contact = dict(first_name="Vasyl",
                   last_name="Petrenko",
                   phone="0123456789",
                   extra="Some extra info")

    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis",
                        AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier",
                        AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback",
                        AsyncMock())
    headers = {'Authorization': f'Bearer {get_access_token}'}
    response = client.post(
        headers=headers,
        url="/contacts",
        json=contact
    )
    print(response.text)
    assert response.status_code > 0, response.text
