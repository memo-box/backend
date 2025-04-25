# MemoBox Project

A smart AI-powered flashcard application using the Leitner System for efficient language learning.

## AI-Powered Features

MemoBox leverages Large Language Models to enhance the language learning experience through several key features:

### Automated Backcard Generation

The application can automatically generate comprehensive flashcard content with a single API call:

- **Intelligent Translations**: Properly handles idiomatic expressions and context-aware translations between languages
- **Detailed Definitions**: Provides dictionary-style definitions in the source language
- **Example Sentences**: Generates contextual example sentences in both source and target languages
- **Pronunciation Guides**: Includes IPA pronunciation transcriptions when available

Example API call:
```bash
curl -X POST http://localhost:8000/api/ai/generate-backcard/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "word_or_phrase": "apple",
    "source_language": "en",
    "target_language": "de"
  }'
```

### Topic-Based Vocabulary Generation

Generate entire sets of topical vocabulary with a single request:

- **Topic Relevance**: Creates vocabulary lists tailored to specific themes or domains
- **Complete Card Content**: Each card includes translations, definitions, example sentences, and pronunciations
- **Customizable Output**: Configure the number of cards to generate (up to 50 per request)

Example API call:
```bash
curl -X POST http://localhost:8000/api/ai/generate-topic-cards/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Food",
    "source_language": "en",
    "target_language": "de",
    "count": 10
  }'
```

### Leitner System Implementation

The application implements the scientifically-proven Leitner spaced repetition system:

- **Adaptive Recall Intervals**: Cards automatically move through spaced repetition intervals based on recall performance
- **Smart Scheduling**: Efficiently schedules reviews to maximize memory retention with minimal time investment
- **Progress Tracking**: Monitors learning progress across different language pairs and vocabulary sets

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

## API Documentation

The API is documented using Swagger and ReDoc:

- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

## Technical Implementation

The AI components leverage:
- LangChain for LLM orchestration
- OpenAI's language models for content generation
- Pydantic schemas for structured output parsing
- Django REST Framework for API endpoints

## Getting Started

1. Clone the repository
2. Configure your `.env` file with your OpenAI API key
3. Install dependencies: `uv sync`
4. Run migrations: `uv run manage.py migrate`
5. Start the server: `uv run manage.py runserver`
