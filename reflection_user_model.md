# Reflection — Secure User Model & CI/CD Pipeline

## Overview

This module extended the existing FastAPI Calculator application with a secure user authentication model using SQLAlchemy and Pydantic, integrated bcrypt password hashing, comprehensive testing, and a full CI/CD pipeline with GitHub Actions and Docker Hub deployment.

---

## Key Experiences

### 1. SQLAlchemy User Model Design

Designing the User model required careful consideration of database constraints. I implemented unique constraints on both `username` and `email` to prevent duplicate accounts, along with indexing for query performance. The `password_hash` column stores bcrypt hashes rather than plain-text passwords, following security best practices.

The use of SQLAlchemy's declarative base made it straightforward to define the schema in Python while maintaining compatibility with both SQLite (for local development and testing) and PostgreSQL (for CI and production).

### 2. Pydantic Schema Separation

One of the most important design decisions was separating the request and response schemas:

- **`UserCreate`** — Accepts `username`, `email`, and raw `password` for user registration.
- **`UserRead`** — Returns user details but explicitly **excludes** the `password_hash` field.

This separation ensures that sensitive data never leaks through API responses, a critical security principle. Using Pydantic's `EmailStr` validator also provided built-in email format validation without writing custom regex.

### 3. Password Hashing with Bcrypt

I chose bcrypt via `passlib` for password hashing because:
- It automatically generates a unique salt for each hash, preventing rainbow table attacks.
- It uses a configurable work factor that makes brute-force attacks computationally expensive.
- It's the industry standard for password storage in web applications.

The `verify_password` function cleanly abstracts the comparison logic, making it easy to authenticate users in future login endpoints.

---

## Challenges Faced

### Challenge 1: Database Session Management in Tests

The biggest challenge was ensuring test isolation. Each integration test needs a clean database state to avoid cross-contamination between tests. I solved this by:
- Using `autouse=True` fixtures to create and drop all tables before and after each test.
- Using SQLite in-memory databases (`sqlite://`) for fast local testing.
- Overriding FastAPI's `get_db` dependency to inject the test session.

### Challenge 2: Handling Duplicate Constraint Errors

When a user tries to register with an existing username or email, the database raises an `IntegrityError`. I had to catch this exception properly in the route handler, roll back the session to prevent corruption, and return a meaningful 409 Conflict response.

### Challenge 3: CI/CD Pipeline with Postgres Service Container

Setting up the GitHub Actions workflow with a PostgreSQL service container required:
- Configuring health checks to ensure Postgres was ready before tests ran.
- Setting the `DATABASE_URL` environment variable correctly to point to the service container.
- Ensuring the deploy job only runs on the `main` branch and only after all tests pass.

### Challenge 4: Docker Hub Integration

Configuring the Docker Hub deployment required:
- Creating GitHub repository secrets (`DOCKER_USERNAME` and `DOCKER_TOKEN`) for authentication.
- Using the `docker/build-push-action` to build and push in a single step.
- Tagging images with both `latest` and the commit SHA for version traceability.

---

## Lessons Learned

1. **Never store plain-text passwords** — Always use a well-tested hashing library like `passlib` with bcrypt.
2. **Separate input and output schemas** — This prevents accidental data exposure in API responses.
3. **Test with real databases in CI** — Unit tests with mocks are insufficient; integration tests against a real Postgres instance catch constraint and driver-level issues.
4. **CI/CD pipelines reduce human error** — Automating testing and deployment ensures consistent quality across every code change.

---

## What I Would Improve

- Add JWT-based authentication on top of the user model for secure login sessions.
- Implement rate limiting on the user creation endpoint to prevent abuse.
- Add database migrations with Alembic instead of `create_all()` for production-grade schema management.
