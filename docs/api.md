# REST API Documentation

The Job Intelligence Platform exposes OpenAPI 3.0 compatible endpoints under `/api/v1`.

## Interactive Swagger & ReDoc
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Key Endpoint Categories

### Authentication
- `POST /api/v1/auth/register` - Create new user account
- `POST /api/v1/auth/login` - Obtain JWT access + refresh tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current authenticated user details

### Jobs & Search
- `GET /api/v1/jobs` - Paginated job feed annotated with match scores & saved status
- `GET /api/v1/jobs/search` - Dynamic search (query, company, location, work_mode, employment_type)
- `GET /api/v1/jobs/{id}` - Single job detail view
- `POST /api/v1/jobs/{id}/save` - Bookmark job
- `DELETE /api/v1/jobs/{id}/save` - Remove bookmark

### Preferences
- `GET /api/v1/preferences` - Retrieve current user preference config
- `PUT /api/v1/preferences` - Update keywords, locations, work modes, salary

### Applications Tracking
- `GET /api/v1/applications` - List tracked applications
- `POST /api/v1/applications` - Track new job application
- `PATCH /api/v1/applications/{id}` - Update application status/notes

### Admin Operations
- `GET /api/v1/admin/sources` - List source configurations
- `POST /api/v1/admin/sources/{id}/scrape` - Trigger manual background scrape task
- `GET /api/v1/admin/scraper-runs` - Inspect scraper execution telemetry log
- `GET /api/v1/admin/stats` - High-level system statistics
