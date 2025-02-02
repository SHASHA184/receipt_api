import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_register_and_login(client):
    """Тест реєстрації та авторизації користувача."""
    # Реєстрація нового користувача
    register_response = await client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
        },
    )
    assert register_response.status_code == 200
    assert "id" in register_response.json()

    # Авторизація
    login_response = await client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert login_response.json()["token_type"] == "bearer"

    return login_response.json()["access_token"]

@pytest.mark.asyncio
async def test_create_receipt(client):
    """Тест створення нового чеку."""
    token = await test_register_and_login(client)

    receipt_response = await client.post(
        "/receipts/",
        json={
            "products": [
                {"name": "Mavic 3T", "price": 298870.00, "quantity": 3},
                {
                    "name": "Дрон FPV з акумулятором 6S чорний",
                    "price": 31000.00,
                    "quantity": 20,
                },
            ],
            "payment": {"type": "cash", "amount": 1516610.00},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert receipt_response.status_code == 200
    assert "id" in receipt_response.json()
    return receipt_response.json()["id"], token

@pytest.mark.asyncio
async def test_get_receipts(client):
    """Тест отримання списку чеків з фільтрацією."""
    _, token = await test_create_receipt(client)

    receipts_response = await client.get(
        "/receipts/", headers={"Authorization": f"Bearer {token}"}
    )
    assert receipts_response.status_code == 200
    assert isinstance(receipts_response.json(), list)

@pytest.mark.asyncio
async def test_get_receipt_text(client):
    """Тест отримання текстового представлення чеку."""
    receipt_id, _ = await test_create_receipt(client)

    text_response = await client.get(f"/receipts/{receipt_id}/text")
    assert text_response.status_code == 200
    assert "ФОП Джонсонюк Борис" in text_response.text


@pytest.mark.asyncio
async def test_get_receipt_by_id(client):
    """Тест отримання чеку за його ID."""
    receipt_id, token = await test_create_receipt(client)

    get_receipt_response = await client.get(
        f"/receipts/{receipt_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert get_receipt_response.status_code == 200
    retrieved_receipt = get_receipt_response.json()

    assert retrieved_receipt["id"] == receipt_id
    assert len(retrieved_receipt["products"]) == 2
    assert retrieved_receipt["total"] == 1516610.00
    assert retrieved_receipt["rest"] == 0.0


@pytest.mark.asyncio
async def test_invalid_receipt_creation(client):
    """Тест створення чеку з некоректними даними."""
    _, token = await test_create_receipt(client)

    invalid_response = await client.post(
        "/receipts/",
        json={"products": [], "payment": {"type": "cash", "amount": 100.00}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert invalid_response.status_code == 422  # Unprocessable Entity

@pytest.mark.asyncio
async def test_invalid_login(client):
    """Тест авторизації з невірними обліковими даними."""
    response = await client.post(
        "/token",
        data={"username": "wronguser", "password": "wrongpassword"},
    )
    assert response.status_code == 400  # Bad Request
