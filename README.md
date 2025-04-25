# MemoBox Project

A smart flashcard application using the Leitner System for efficient language learning.

## Authentication

The application uses JWT (JSON Web Token) authentication. Here's how to use it:

### Getting Tokens

To authenticate and get a token, send a POST request to `/api/token/` with your email and password:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your_password"}'
```

The response will include:
- `access`: The access token (valid for 1 hour)
- `refresh`: The refresh token (valid for 1 day)
- User details: `user_id`, `email`, `name`, and `is_staff`

### Using the Token

Include the access token in the Authorization header for protected API requests:

```bash
curl -X GET http://localhost:8000/api/leitner/boxes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refreshing Tokens

When the access token expires, use the refresh token to get a new one:

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

### Verifying Tokens

To verify that a token is valid:

```bash
curl -X POST http://localhost:8000/api/token/verify/ \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN"}'
```

## API Endpoints

The API is documented using Swagger and ReDoc:

- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`
