async def test_register_user(client):
    response = await client.post(
        "api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "password123!"
        }
    )
    
    assert response.status_code == 201
    
    body = response.json()
    
    assert body["email"] == "new@example.com"
    assert body["is_active"] is True
    
    assert "password" not in body
    assert "password_hash" not in body


async def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "password123!"
    }
    
    first = await client.post(
        "api/v1/auth/register",
        json=payload
    )
    
    second = await client.post(
        "api/v1/auth/register",
        json=payload
    )
    
    assert first.status_code == 201
    
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "USER_ALREADY_EXISTS"
    

async def test_register_invalid_email(client):
    response = await client.post(
        "api/v1/auth/register",
        json={
            "email": "invalid_email@",
            "password": "password123~"
        }
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    

async def test_register_short_password(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "short@example.com",
            "password": "123",
        },
    )

    assert response.status_code == 422