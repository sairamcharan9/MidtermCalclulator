"""
Playwright E2E Tests
====================

Browser end-to-end tests for the Advanced Web Calculator.
Requires the server to be running at TEST_URL (default: http://localhost:8000).

Run with:
    TEST_URL=http://localhost:8000 pytest tests/fastapi/e2e -v
"""

import os
import time
import uuid

import httpx
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("TEST_URL", "http://localhost:8000")


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def _register_user_via_api(username: str, email: str, password: str) -> dict:
    """Register a user directly via API (no browser) for test setup."""
    resp = httpx.post(
        f"{BASE_URL}/users/register",
        json={"username": username, "email": email, "password": password},
    )
    return resp


# ─────────────────────────────────────────────────────────────────────────────
# Calculator UI tests (existing)
# ─────────────────────────────────────────────────────────────────────────────

def test_addition_e2e():
    """Test basic addition and memory through the UI"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(BASE_URL)

            page.fill("#a", "5")
            page.fill("#b", "5")
            page.click("button:has-text('Add (+)')")

            page.wait_for_selector('.success')
            result = page.inner_text("#result-text")
            assert "10" in result

            # Store in Memory
            page.fill("#a", "999")
            page.click("button:has-text('Store \\'A\\' to Memory')")
            time.sleep(1)

            # Recall Memory
            page.click("button:has-text('Recall Memory')")
            time.sleep(1)

            text = page.inner_text("#result-text")
            assert "999" in text

        finally:
            browser.close()


def test_subtraction_e2e():
    """Test subtraction through the UI"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(BASE_URL)
            page.fill("#a", "10")
            page.fill("#b", "3")
            page.click("button:has-text('Subtract (-)')")

            page.wait_for_selector('.success')
            result = page.inner_text("#result-text")
            assert "7" in result
        finally:
            browser.close()


def test_divide_by_zero_e2e():
    """Test that dividing by zero shows an error in status/display"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(BASE_URL)
            page.fill("#a", "10")
            page.fill("#b", "0")
            page.click("button:has-text('Divide')")

            page.wait_for_selector('.error')
            result = page.inner_text("#result-text")
            assert "Error" in result or "zero" in result.lower()
        finally:
            browser.close()


def test_history_e2e():
    """Test viewing and clearing history in the side drawer"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Perform a calculation first
            page.goto(BASE_URL)
            page.fill("#a", "8")
            page.fill("#b", "2")
            page.click("button:has-text('Multiply')")
            page.wait_for_selector('.success')

            # View History
            page.click("button:has-text('Reload')")
            time.sleep(1)
            history_text = page.inner_text("#history-container")
            assert "16" in history_text or "8" in history_text

            # Clear Server History
            page.click("button:has-text('Clear')")
            time.sleep(1)
            history_text = page.inner_text("#history-container")
            assert "History empty." in history_text or "No calculations yet." in history_text
        finally:
            browser.close()


# ─────────────────────────────────────────────────────────────────────────────
# Auth E2E tests — NEW (Module 13)
# ─────────────────────────────────────────────────────────────────────────────

def test_register_valid_user_e2e():
    """
    POSITIVE — Register with valid data via the /register page.

    Steps:
      1. Navigate to /register.
      2. Fill in a unique email, username, and a ≥8-char password.
      3. Submit the form.
      4. Verify the success alert is displayed.
    """
    unique_id = uuid.uuid4().hex[:8]
    email = f"testuser_{unique_id}@example.com"
    username = f"user_{unique_id}"
    password = "SecurePass123!"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(f"{BASE_URL}/register")

            # Fill form fields
            page.fill("#reg-email", email)
            page.fill("#reg-username", username)
            page.fill("#reg-password", password)
            page.fill("#reg-confirm", password)

            # Submit
            page.click("#register-btn")

            # Verify success alert is visible
            page.wait_for_selector("#alert-success.visible", timeout=8000)
            success_text = page.inner_text("#alert-success")
            assert "Account created" in success_text or "Welcome" in success_text, \
                f"Expected success message, got: '{success_text}'"

        finally:
            browser.close()


def test_login_valid_credentials_e2e():
    """
    POSITIVE — Login with correct credentials via the /login page.

    Steps:
      1. Register a user via API (setup).
      2. Navigate to /login.
      3. Fill username and password.
      4. Submit and verify the success alert appears.
      5. Verify JWT is stored in localStorage under 'auth_token'.
    """
    unique_id = uuid.uuid4().hex[:8]
    username = f"logintest_{unique_id}"
    email = f"{username}@example.com"
    password = "ValidPass456!"

    # Setup: register user via API
    resp = _register_user_via_api(username, email, password)
    assert resp.status_code == 201, f"Setup registration failed: {resp.text}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(f"{BASE_URL}/login")

            # Fill login form
            page.fill("#login-username", username)
            page.fill("#login-password", password)

            # Submit
            page.click("#login-btn")

            # Verify success alert appears
            page.wait_for_selector("#alert-success.visible", timeout=8000)
            success_text = page.inner_text("#alert-success")
            assert "Signed in" in success_text or "session" in success_text.lower(), \
                f"Expected success message, got: '{success_text}'"

            # Verify JWT was stored in localStorage
            token = page.evaluate("() => localStorage.getItem('auth_token')")
            assert token is not None, "JWT was not stored in localStorage"
            assert len(token) > 20, f"JWT looks invalid (too short): '{token}'"

        finally:
            browser.close()


def test_register_short_password_e2e():
    """
    NEGATIVE — Register with a password shorter than 8 characters.

    Steps:
      1. Navigate to /register.
      2. Fill a valid email & username, but only a 4-char password.
      3. Attempt to submit.
      4. Verify the client-side password error is shown (no server call needed).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(f"{BASE_URL}/register")

            page.fill("#reg-email", "short@example.com")
            page.fill("#reg-username", "shortpwuser")
            page.fill("#reg-password", "abc")          # 3 chars — too short
            page.fill("#reg-confirm", "abc")

            page.click("#register-btn")

            # The client-side error for password should appear
            page.wait_for_selector("#password-error.visible", timeout=5000)
            error_text = page.inner_text("#password-error")
            assert "8" in error_text or "least" in error_text.lower(), \
                f"Expected password length error, got: '{error_text}'"

            # Success alert must NOT be shown
            success_visible = page.is_visible("#alert-success.visible")
            assert not success_visible, "Success alert should NOT appear for short password"

        finally:
            browser.close()


def test_login_wrong_password_e2e():
    """
    NEGATIVE — Login with a wrong password; server must return 401 and UI shows error.

    Steps:
      1. Register a user via API (setup).
      2. Navigate to /login.
      3. Fill correct username but wrong password.
      4. Submit and verify the error alert is displayed (401 feedback).
    """
    unique_id = uuid.uuid4().hex[:8]
    username = f"wrongpw_{unique_id}"
    email = f"{username}@example.com"
    correct_password = "CorrectPass789!"

    # Setup: register user via API
    resp = _register_user_via_api(username, email, correct_password)
    assert resp.status_code == 201, f"Setup registration failed: {resp.text}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(f"{BASE_URL}/login")

            page.fill("#login-username", username)
            page.fill("#login-password", "WrongPassword!")   # deliberately wrong

            page.click("#login-btn")

            # Error alert should appear
            page.wait_for_selector("#alert-error.visible", timeout=8000)
            error_text = page.inner_text("#alert-error")
            assert (
                "Invalid" in error_text
                or "credentials" in error_text.lower()
                or "401" in error_text
            ), f"Expected invalid credentials message, got: '{error_text}'"

            # Success alert must NOT appear
            success_visible = page.is_visible("#alert-success.visible")
            assert not success_visible, "Success alert should NOT appear for wrong password"

            # JWT must NOT be in localStorage
            token = page.evaluate("() => localStorage.getItem('auth_token')")
            assert token is None or token == "", "JWT should not be stored on failed login"

        finally:
            browser.close()
