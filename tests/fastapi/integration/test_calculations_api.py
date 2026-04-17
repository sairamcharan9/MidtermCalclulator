"""
Integration Tests for Calculation BREAD API
============================================

Tests the Browse, Read, Edit, Add, and Delete calculation endpoints
against an in-memory SQLite database.  In CI these run against the
PostgreSQL service container configured in the GitHub Actions workflow.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.database import Base, get_db
from main import app


# ---------- Test Database Setup ----------

SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"  # shared in-memory DB for this module

_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _override_get_db():
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _db_tables():
    """
    Activate our test engine override, create tables, run test, tear down.
    Using autouse=True so every test in this module gets a fresh schema.
    """
    app.dependency_overrides[get_db] = _override_get_db
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)
    app.dependency_overrides.pop(get_db, None)


client = TestClient(app)


# ---------- Shared Helpers ----------

def _make_user(username="testuser", email="testuser@example.com", password="pass1234"):
    """Register a user and return the response JSON."""
    resp = client.post("/users/register", json={
        "username": username,
        "email": email,
        "password": password,
    })
    assert resp.status_code == 201, resp.text
    return resp.json()


def _make_calc(user_id: int, a=10.0, b=5.0, op="ADD"):
    """POST a calculation and return the response JSON."""
    resp = client.post("/calculations/", json={
        "a": a,
        "b": b,
        "type": op,
        "user_id": user_id,
    })
    assert resp.status_code == 201, resp.text
    return resp.json()


# ==========================================================================
# Browse — GET /calculations
# ==========================================================================

class TestBrowseCalculations:
    """Tests for GET /calculations"""

    def test_browse_empty_returns_list(self):
        """When no calculations exist, the endpoint returns an empty list."""
        response = client.get("/calculations/")
        assert response.status_code == 200
        assert response.json() == []

    def test_browse_returns_all_calculations(self):
        """Browse returns every calculation in the database."""
        user = _make_user()
        _make_calc(user["id"], a=1, b=2, op="ADD")
        _make_calc(user["id"], a=10, b=5, op="SUBTRACT")

        response = client.get("/calculations/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_browse_filter_by_user_id(self):
        """Browse with ?user_id= returns only that user's calculations."""
        user_a = _make_user(username="userabc", email="userabc@example.com")
        user_b = _make_user(username="userdef", email="userdef@example.com")
        _make_calc(user_a["id"], a=1, b=1, op="ADD")
        _make_calc(user_b["id"], a=9, b=3, op="DIVIDE")

        response = client.get(f"/calculations/?user_id={user_a['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == user_a["id"]

    def test_browse_response_shape(self):
        """Each calculation in the list has the expected fields."""
        user = _make_user()
        _make_calc(user["id"])

        response = client.get("/calculations/")
        calc = response.json()[0]
        for field in ("id", "a", "b", "type", "result", "user_id", "created_at"):
            assert field in calc, f"Missing field: {field}"


# ==========================================================================
# Read — GET /calculations/{id}
# ==========================================================================

class TestReadCalculation:
    """Tests for GET /calculations/{id}"""

    def test_read_existing_calculation(self):
        """Reading an existing calculation returns the correct record."""
        user = _make_user()
        created = _make_calc(user["id"], a=6, b=2, op="MULTIPLY")

        response = client.get(f"/calculations/{created['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created["id"]
        assert data["a"] == 6.0
        assert data["b"] == 2.0
        assert data["type"] == "MULTIPLY"
        assert data["result"] == 12.0

    def test_read_nonexistent_returns_404(self):
        """Reading a non-existent ID returns 404."""
        response = client.get("/calculations/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_read_result_is_correct_for_add(self):
        """ADD: result = a + b."""
        user = _make_user()
        calc = _make_calc(user["id"], a=3, b=4, op="ADD")
        response = client.get(f"/calculations/{calc['id']}")
        assert response.json()["result"] == 7.0

    def test_read_result_is_correct_for_subtract(self):
        """SUBTRACT: result = a - b."""
        user = _make_user()
        calc = _make_calc(user["id"], a=10, b=4, op="SUBTRACT")
        response = client.get(f"/calculations/{calc['id']}")
        assert response.json()["result"] == 6.0

    def test_read_result_is_correct_for_divide(self):
        """DIVIDE: result = a / b."""
        user = _make_user()
        calc = _make_calc(user["id"], a=10, b=4, op="DIVIDE")
        response = client.get(f"/calculations/{calc['id']}")
        assert response.json()["result"] == 2.5


# ==========================================================================
# Add — POST /calculations
# ==========================================================================

class TestAddCalculation:
    """Tests for POST /calculations"""

    def test_add_calculation_success(self):
        """Creating a valid calculation returns 201 and the saved record."""
        user = _make_user()
        response = client.post("/calculations/", json={
            "a": 8.0,
            "b": 4.0,
            "type": "DIVIDE",
            "user_id": user["id"],
        })
        assert response.status_code == 201
        data = response.json()
        assert data["a"] == 8.0
        assert data["b"] == 4.0
        assert data["type"] == "DIVIDE"
        assert data["result"] == 2.0
        assert data["user_id"] == user["id"]
        assert "id" in data
        assert "created_at" in data

    def test_add_computation_is_server_side(self):
        """Caller does not supply result; server computes it."""
        user = _make_user()
        data = _make_calc(user["id"], a=7, b=3, op="ADD")
        assert data["result"] == 10.0

    def test_add_divide_by_zero_returns_422(self):
        """Division by zero is rejected with 422 before hitting the DB."""
        user = _make_user()
        response = client.post("/calculations/", json={
            "a": 5.0,
            "b": 0.0,
            "type": "DIVIDE",
            "user_id": user["id"],
        })
        assert response.status_code == 422

    def test_add_int_divide_by_zero_returns_422(self):
        """INT_DIVIDE by zero is also rejected with 422."""
        user = _make_user()
        response = client.post("/calculations/", json={
            "a": 5.0,
            "b": 0.0,
            "type": "INT_DIVIDE",
            "user_id": user["id"],
        })
        assert response.status_code == 422

    def test_add_invalid_operation_returns_422(self):
        """An unknown operation type is rejected with 422."""
        user = _make_user()
        response = client.post("/calculations/", json={
            "a": 2.0,
            "b": 3.0,
            "type": "EXPONENTIATE",
            "user_id": user["id"],
        })
        assert response.status_code == 422

    def test_add_nonexistent_user_returns_404(self):
        """Attempting to create a calculation for a missing user returns 404."""
        response = client.post("/calculations/", json={
            "a": 1.0,
            "b": 1.0,
            "type": "ADD",
            "user_id": 99999,
        })
        assert response.status_code == 404

    def test_add_missing_fields_returns_422(self):
        """Missing required fields returns 422."""
        user = _make_user()
        response = client.post("/calculations/", json={
            "a": 5.0,
            "user_id": user["id"],
            # missing b and type
        })
        assert response.status_code == 422

    def test_add_all_operation_types(self):
        """All supported operation types can be stored successfully."""
        user = _make_user()
        ops = [
            ("ADD", 5, 3, 8),
            ("SUBTRACT", 10, 4, 6),
            ("MULTIPLY", 3, 4, 12),
            ("DIVIDE", 9, 3, 3),
            ("INT_DIVIDE", 10, 3, 3),
        ]
        for op, a, b, expected_result in ops:
            resp = client.post("/calculations/", json={
                "a": a, "b": b, "type": op, "user_id": user["id"]
            })
            assert resp.status_code == 201, f"Failed for op={op}: {resp.text}"
            assert resp.json()["result"] == expected_result, f"Wrong result for {op}"


# ==========================================================================
# Edit — PUT /calculations/{id}
# ==========================================================================

class TestEditCalculation:
    """Tests for PUT /calculations/{id}"""

    def test_edit_updates_operands_and_result(self):
        """Editing a calculation updates a, b, type, and recomputes result."""
        user = _make_user()
        calc = _make_calc(user["id"], a=10, b=5, op="ADD")  # result = 15

        response = client.put(f"/calculations/{calc['id']}", json={
            "a": 3.0,
            "b": 4.0,
            "type": "MULTIPLY",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["a"] == 3.0
        assert data["b"] == 4.0
        assert data["type"] == "MULTIPLY"
        assert data["result"] == 12.0
        # ID and user_id must not change
        assert data["id"] == calc["id"]
        assert data["user_id"] == user["id"]

    def test_edit_nonexistent_returns_404(self):
        """Editing a non-existent calculation returns 404."""
        response = client.put("/calculations/99999", json={
            "a": 1.0, "b": 1.0, "type": "ADD",
        })
        assert response.status_code == 404

    def test_edit_divide_by_zero_returns_422(self):
        """Editing to produce a divide-by-zero is rejected with 422."""
        user = _make_user()
        calc = _make_calc(user["id"])

        response = client.put(f"/calculations/{calc['id']}", json={
            "a": 5.0, "b": 0.0, "type": "DIVIDE",
        })
        assert response.status_code == 422

    def test_edit_invalid_type_returns_422(self):
        """Editing with an unsupported operation type returns 422."""
        user = _make_user()
        calc = _make_calc(user["id"])

        response = client.put(f"/calculations/{calc['id']}", json={
            "a": 5.0, "b": 2.0, "type": "POWER",
        })
        assert response.status_code == 422

    def test_edit_missing_fields_returns_422(self):
        """Editing without all required fields returns 422."""
        user = _make_user()
        calc = _make_calc(user["id"])

        response = client.put(f"/calculations/{calc['id']}", json={
            "a": 5.0,
            # missing b and type
        })
        assert response.status_code == 422

    def test_edit_result_is_recomputed(self):
        """After edit, the result reflects the new operands, not the old ones."""
        user = _make_user()
        calc = _make_calc(user["id"], a=100, b=50, op="ADD")  # result = 150

        client.put(f"/calculations/{calc['id']}", json={
            "a": 9.0, "b": 3.0, "type": "DIVIDE",
        })

        # Re-read from API to confirm persistence
        read = client.get(f"/calculations/{calc['id']}")
        assert read.json()["result"] == 3.0


# ==========================================================================
# Delete — DELETE /calculations/{id}
# ==========================================================================

class TestDeleteCalculation:
    """Tests for DELETE /calculations/{id}"""

    def test_delete_existing_returns_204(self):
        """Deleting an existing calculation returns 204 No Content."""
        user = _make_user()
        calc = _make_calc(user["id"])

        response = client.delete(f"/calculations/{calc['id']}")
        assert response.status_code == 204

    def test_delete_then_read_returns_404(self):
        """After deletion, reading the same ID returns 404."""
        user = _make_user()
        calc = _make_calc(user["id"])
        calc_id = calc["id"]

        client.delete(f"/calculations/{calc_id}")

        read = client.get(f"/calculations/{calc_id}")
        assert read.status_code == 404

    def test_delete_nonexistent_returns_404(self):
        """Deleting a calculation that doesn't exist returns 404."""
        response = client.delete("/calculations/99999")
        assert response.status_code == 404

    def test_delete_removes_only_target(self):
        """Deleting one calculation does not affect others."""
        user = _make_user()
        calc_a = _make_calc(user["id"], a=1, b=1, op="ADD")
        calc_b = _make_calc(user["id"], a=2, b=2, op="MULTIPLY")

        client.delete(f"/calculations/{calc_a['id']}")

        # calc_b should still exist
        remaining = client.get("/calculations/")
        ids = [c["id"] for c in remaining.json()]
        assert calc_a["id"] not in ids
        assert calc_b["id"] in ids

    def test_delete_reduces_browse_count(self):
        """After deleting a calculation, browse count decreases by one."""
        user = _make_user()
        _make_calc(user["id"], a=1, b=2, op="ADD")
        _make_calc(user["id"], a=3, b=4, op="SUBTRACT")

        all_calcs = client.get("/calculations/").json()
        assert len(all_calcs) == 2

        client.delete(f"/calculations/{all_calcs[0]['id']}")

        remaining = client.get("/calculations/").json()
        assert len(remaining) == 1

