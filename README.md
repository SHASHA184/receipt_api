# Receipt API

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:

   ```sh
   git clone https://github.com/SHASHA184/receipt_api.git
   cd receipt_api
   ```
2. Create a `.env` file in the root directory and add the necessary environment variables:

   ```env
   POSTGRES_USER=your_postgres_user
   POSTGRES_PASSWORD=your_postgres_password
   POSTGRES_DB=your_postgres_db

   SECRET_KEY=your_secret_key
   ```
3. Build and start the Docker containers:

   ```sh
   docker-compose up --build
   ```
4. The API will be available at `http://localhost:8000`.

   API Documentation:

   * **Swagger UI:** [http://localhost:8000/docs]()

## Database Migrations

To run database migrations, use this script:

```sh
bash app/scripts/apply_migrations.sh
```

## Running Tests

To run tests, use this script:

```sh
bash app/scripts/run_tests.sh
```

## Stopping the Service

To stop the running containers, use:

```sh
docker-compose down
```

## API Documentation

### Authentication

#### Register a User

- **Create User**
    - **POST** `/users/`
    - **Request Body**: 
        ```json
        {
            "username": "string",
            "email": "string",
            "password": "string"
        }
        ```
    - **Response**: 
        ```json
        {
            "id": "integer",
            "username": "string",
            "email": "string"
        }
        ```

- **Update User**
    - **PATCH** `/users/{id}`
    - **Request Body**: 
        ```json
        {
            "username": "string",
            "email": "string",
            "password": "string"
        }
        ```
    - **Response**: 
        ```json
        {
            "id": "integer",
            "username": "string",
            "email": "string"
        }
        ```

### Receipt Endpoints

- **Create Receipt**
    - **POST** `/receipts/`
    - **Request Body**: 
        ```json
        {
            "total": "decimal",
            "rest": "decimal",
            "payment_type": "enum",
            "payment_amount": "decimal",
            "created_at": "datetime",
            "owner_id": "integer"
        }
        ```
    - **Response**: 
        ```json
        {
            "id": "integer",
            "total": "decimal",
            "rest": "decimal",
            "payment_type": "enum",
            "payment_amount": "decimal",
            "created_at": "datetime",
            "owner_id": "integer"
        }
        ```

- **Get Receipts**
    - **GET** `/receipts/`
    - **Query Parameters**: 
        - `start_date`: `datetime` (optional)
        - `end_date`: `datetime` (optional)
        - `min_total`: `float` (optional)
        - `max_total`: `float` (optional)
        - `payment_type`: `enum` (optional)
        - `limit`: `integer` (default: 10)
        - `offset`: `integer` (default: 0)
    - **Response**: 
        ```json
        [
            {
                "id": "integer",
                "total": "decimal",
                "rest": "decimal",
                "payment_type": "enum",
                "payment_amount": "decimal",
                "created_at": "datetime",
                "owner_id": "integer"
            }
        ]
        ```

- **Get Receipt by ID**
    - **GET** `/receipts/{receipt_id}`
    - **Response**: 
        ```json
        {
            "id": "integer",
            "total": "decimal",
            "rest": "decimal",
            "payment_type": "enum",
            "payment_amount": "decimal",
            "created_at": "datetime",
            "owner_id": "integer"
        }
        ```

- **Get Receipt Text**
    - **GET** `/receipts/{receipt_id}/text`
    - **Query Parameters**: 
        - `line_length`: `integer` (default: 40)
    - **Response**: Plain text receipt

### Authentication Endpoints

- **Login**
    - **POST** `/token`
    - **Request Body**: 
        ```json
        {
            "username": "string",
            "password": "string"
        }
        ```
    - **Response**: 
        ```json
        {
            "access_token": "string",
            "token_type": "bearer"
        }
        ```

## Example Requests and Responses

### Create User

**Request:**
```sh
curl -X POST "http://localhost:8000/users/" -H "Content-Type: application/json" -d '{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword"
}'
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

### Create Receipt

**Request:**
```sh
curl -X POST "http://localhost:8000/receipts/" -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{
  "total": 100.00,
  "rest": 0.00,
  "payment_type": "CASH",
  "payment_amount": 100.00,
  "created_at": "2023-10-01T12:00:00",
  "owner_id": 1
}'
```

**Response:**
```json
{
  "id": 1,
  "total": 100.00,
  "rest": 0.00,
  "payment_type": "CASH",
  "payment_amount": 100.00,
  "created_at": "2023-10-01T12:00:00",
  "owner_id": 1
}
```

### Get Receipts

**Request:**
```sh
curl -X GET "http://localhost:8000/receipts/" -H "Authorization: Bearer <token>"
```

**Response:**
```json
[
  {
    "id": 1,
    "total": 100.00,
    "rest": 0.00,
    "payment_type": "CASH",
    "payment_amount": 100.00,
    "created_at": "2023-10-01T12:00:00",
    "owner_id": 1
  }
]
```


## Technologies Used

This project uses:

- **FastAPI** - API framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM for database management
- **Alembic** - Database migrations
- **Docker** - Containerization
- **Pytest** - Testing