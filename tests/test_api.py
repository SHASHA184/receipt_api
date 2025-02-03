import pytest
import uuid

@pytest.mark.asyncio
async def test_register_and_login(client):
    """Test user registration and login."""
    unique_email = f"testuser_{uuid.uuid4()}@example.com"
    unique_username = f"testuser_{uuid.uuid4()}"

    register_response = await client.post(
        "/users/",
        json={
            "username": unique_username,
            "email": unique_email,
            "password": "testpassword",
        },
    )
    assert register_response.status_code == 200
    assert "id" in register_response.json()

    login_response = await client.post(
        "/token",
        data={"username": unique_username, "password": "testpassword"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert login_response.json()["token_type"] == "bearer"

    return login_response.json()["access_token"], unique_email

@pytest.mark.asyncio
async def test_register_existing_email(client):
    """Test registration with an existing email."""
    _, email = await test_register_and_login(client)

    response = await client.post(
        "/users/",
        json={"username": "anotheruser", "email": email, "password": "newpassword"},
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """Test registration with an invalid email."""
    response = await client.post(
        "/users/",
        json={"username": "invaliduser", "email": "invalid-email", "password": "pass"},
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_with_empty_password(client):
    """Test login with an empty password."""
    response = await client.post(
        "/token",
        data={"username": "testuser", "password": ""},
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_receipt(client):
    """Test creating a new receipt."""
    token, _ = await test_register_and_login(client)

    receipt_response = await client.post(
        "/receipts/",
        json={
            "products": [
                {"name": "MacBook Pro", "price": 2500.00, "quantity": 1},
                {"name": "Magic Mouse", "price": 100.00, "quantity": 2},
            ],
            "payment": {"type": "cash", "amount": 2700.00},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert receipt_response.status_code == 200
    assert "id" in receipt_response.json()
    return receipt_response.json()["id"], token

@pytest.mark.asyncio
async def test_create_receipt_with_zero_amount(client):
    """Test creating a receipt with zero amount."""
    token, _ = await test_register_and_login(client)

    response = await client.post(
        "/receipts/",
        json={
            "products": [{"name": "Free Item", "price": 0.00, "quantity": 1}],
            "payment": {"type": "cash", "amount": 0.00},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_receipt_with_negative_price(client):
    """Test creating a receipt with a negative price."""
    token, _ = await test_register_and_login(client)

    response = await client.post(
        "/receipts/",
        json={
            "products": [{"name": "Negative Item", "price": -10.00, "quantity": 1}],
            "payment": {"type": "cash", "amount": 10.00},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_receipt_by_id(client):
    """Test getting a receipt by its ID."""
    receipt_id, token = await test_create_receipt(client)

    get_receipt_response = await client.get(
        f"/receipts/{receipt_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert get_receipt_response.status_code == 200
    retrieved_receipt = get_receipt_response.json()

    assert retrieved_receipt["id"] == receipt_id
    assert len(retrieved_receipt["products"]) == 2
    assert retrieved_receipt["total"] == 2700.00
    assert retrieved_receipt["rest"] == 0.0

@pytest.mark.asyncio
async def test_get_nonexistent_receipt(client):
    """Test getting a nonexistent receipt."""
    token, _ = await test_register_and_login(client)

    response = await client.get(
        f"/receipts/9999999", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_other_user_receipt(client):
    """Test attempting to get another user's receipt."""
    _, token1 = await test_create_receipt(client)
    _, token2 = await test_create_receipt(client)

    response = await client.get(
        f"/receipts/1", headers={"Authorization": f"Bearer {token2}"}
    )
    print(response.json())
    print(response.status_code)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_receipt_text(client):
    """Test getting the text representation of a receipt."""
    receipt_id, _ = await test_create_receipt(client)

    text_response = await client.get(f"/receipts/{receipt_id}/text")
    assert text_response.status_code == 200
    assert "ФОП Джонсонюк Борис" in text_response.text

@pytest.mark.asyncio
async def test_invalid_receipt_creation(client):
    """Test creating a receipt with invalid data."""
    _, token = await test_create_receipt(client)

    invalid_response = await client.post(
        "/receipts/",
        json={"products": [], "payment": {"type": "cash", "amount": 100.00}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert invalid_response.status_code == 422

@pytest.mark.asyncio
async def test_invalid_login(client):
    """Test login with incorrect credentials."""
    response = await client.post(
        "/token",
        data={"username": "wronguser", "password": "wrongpassword"},
    )
    assert response.status_code == 400
