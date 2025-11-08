# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://app-techpulse-api.azurewebsites.net`

## Authentication

All endpoints (except `/health` and `/`) require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Health Check

#### GET /health

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

### Feed

#### GET /api/feed

Get personalized feed for the current user.

**Headers:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "feed": [
    {
      "id": "content123",
      "title": "Latest AI Trends",
      "type": "article",
      "url": "https://example.com/article",
      "description": "Article description",
      "published_at": "2024-01-15T10:00:00Z",
      "role_tags": ["Data Analyst - Hospitality"],
      "summary": "AI-generated summary",
      "priority_score": 0.85
    }
  ]
}
```

#### GET /api/feed/today

Get today's top content for streak completion.

**Headers:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "content": {
    "id": "content123",
    "title": "Latest AI Trends",
    "type": "article",
    "url": "https://example.com/article",
    "published_at": "2024-01-15T10:00:00Z"
  }
}
```

### Content

#### GET /api/content/{content_id}

Get a specific content item.

**Parameters:**
- `content_id` (path): Content item ID

**Response:**
```json
{
  "id": "content123",
  "title": "Latest AI Trends",
  "type": "article",
  "url": "https://example.com/article",
  "description": "Article description",
  "summary": "AI-generated summary",
  "published_at": "2024-01-15T10:00:00Z",
  "role_tags": ["Data Analyst - Hospitality"],
  "transcript": "Full transcript for videos/podcasts",
  "animated_summary": {
    "storyboard": [
      {
        "step": 1,
        "type": "event",
        "title": "Introduction",
        "description": "Key point description"
      }
    ],
    "audio_url": "https://storage.azure.com/audio-summaries/summary_content123.mp3"
  }
}
```

#### GET /api/content/{content_id}/summary

Get or generate animated summary for content.

**Parameters:**
- `content_id` (path): Content item ID

**Response:**
```json
{
  "storyboard": [
    {
      "step": 1,
      "type": "event",
      "title": "Introduction",
      "description": "Key point description"
    }
  ],
  "audio_url": "https://storage.azure.com/audio-summaries/summary_content123.mp3"
}
```

#### POST /api/content/{content_id}/complete

Mark content as completed by user.

**Parameters:**
- `content_id` (path): Content item ID

**Body:**
```json
{
  "user_id": "user123"
}
```

**Response:**
```json
{
  "status": "completed"
}
```

### Quiz

#### GET /api/quiz/content/{content_id}

Get quiz for a content item.

**Parameters:**
- `content_id` (path): Content item ID
- `version` (query, optional): Quiz version (default: 1)

**Response:**
```json
{
  "id": "quiz123",
  "content_id": "content123",
  "questions": [
    {
      "question": "What is the main topic?",
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "correct_answer": 0,
      "explanation": "Explanation of the correct answer"
    }
  ],
  "version": 1
}
```

#### POST /api/quiz/content/{content_id}/submit

Submit quiz answers.

**Parameters:**
- `content_id` (path): Content item ID

**Body:**
```json
{
  "user_id": "user123",
  "answers": [0, 1, 2, 0, 1]
}
```

**Response (Passed):**
```json
{
  "status": "passed",
  "correct_count": 4,
  "wrong_count": 1,
  "tech_score_change": 10,
  "review_hints": null,
  "next_quiz_id": null
}
```

**Response (Failed - Retry Required):**
```json
{
  "status": "retry",
  "correct_count": 2,
  "wrong_count": 3,
  "tech_score_change": -2,
  "review_hints": {
    "articleHighlights": [
      {"paragraphIndex": 2},
      {"paragraphIndex": 4}
    ],
    "timestamps": ["00:45-01:20", "03:10-03:40"],
    "concepts": ["concept1", "concept2"]
  },
  "next_quiz_id": "quiz456"
}
```

#### GET /api/quiz/content/{content_id}/retry

Get retry quiz after failure.

**Parameters:**
- `content_id` (path): Content item ID
- `user_id` (query): User ID

**Response:**
```json
{
  "id": "quiz456",
  "content_id": "content123",
  "questions": [
    {
      "question": "New question focusing on missed concepts",
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "correct_answer": 1,
      "explanation": "Explanation"
    }
  ],
  "version": 2
}
```

### User

#### GET /api/me/dashboard

Get user dashboard data.

**Parameters:**
- `user_id` (query): User ID

**Response:**
```json
{
  "user": {
    "id": "user123",
    "email": "user@example.com",
    "name": "John Doe",
    "tech_score": 150,
    "current_streak": 5,
    "longest_streak": 10,
    "badges": ["early-adopter", "week-warrior"]
  },
  "recent_completions": [
    {
      "id": "attempt123",
      "content_id": "content123",
      "passed": true,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "stats_by_type": {
    "article": 10,
    "video": 5,
    "podcast": 3
  }
}
```

#### GET /api/me/stats

Get user statistics.

**Parameters:**
- `user_id` (query): User ID

**Response:**
```json
{
  "user": {
    "id": "user123",
    "tech_score": 150,
    "current_streak": 5
  },
  "total_completions": 18,
  "first_try_passes": 15,
  "retry_passes": 3
}
```

### Admin

#### GET /api/admin/organizations

List all organizations.

**Response:**
```json
{
  "organizations": [
    {
      "id": "org123",
      "name": "Acme Corp",
      "domain": "acme.com",
      "sources": ["source1", "source2"],
      "roles": ["Data Analyst - Hospitality"]
    }
  ]
}
```

#### GET /api/admin/analytics

Get organization analytics.

**Parameters:**
- `organization_id` (query): Organization ID

**Response:**
```json
{
  "total_users": 100,
  "active_users": 75,
  "avg_tech_score": 125.5,
  "participation_rate": 0.75
}
```

#### POST /api/admin/sources

Add content source.

**Body:**
```json
{
  "name": "TechCrunch",
  "type": "rss",
  "url": "https://techcrunch.com/feed/",
  "role_tags": ["Data Analyst - Hospitality"],
  "enabled": true,
  "organization_id": "org123"
}
```

**Response:**
```json
{
  "id": "source123",
  "status": "created"
}
```

#### GET /api/admin/reports

Generate organization report.

**Parameters:**
- `organization_id` (query): Organization ID

**Response:**
```json
{
  "organization_id": "org123",
  "period": "last_7_days",
  "total_completions": 150,
  "users": 100
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Unauthorized"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Content Types

- `article`: Web articles from RSS feeds
- `video`: YouTube videos
- `podcast`: Podcast episodes from RSS feeds

## Quiz Scoring

- **First try pass**: +10 points
- **Second try pass**: +6 points
- **Multiple retries**: +3 points
- **Failed attempt**: -2 points

## Rate Limiting

Rate limiting may be implemented in production. Check response headers for rate limit information.

## Pagination

List endpoints may support pagination in the future. Currently, feeds are limited to 20 items.


