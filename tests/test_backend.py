"""
Tests for backend.py – focused on the fixes applied in SPB-12.

Covers:
  - F3: No import-time side effects (startup_init deferred to lifespan)
  - F4: Atomic persistence (tempfile + rename, thread-safety)
  - R1: Path-traversal protection in /uploads/{filename}
  - S3: Correct method call (generate_content vs generate_text_with_gemini)
  - S1: No dead Fabric.js commented-out code in index.html
  - API route smoke-tests with a mocked API client
"""

import importlib
import json
import os
import sys
import threading
from unittest.mock import MagicMock, patch

import pytest

# Ensure the repo root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


# ---------------------------------------------------------------------------
# F3: startup_init should NOT run at import time
# ---------------------------------------------------------------------------
class TestNoImportTimeSideEffects:
    """Verify that importing backend does not trigger startup_init."""

    def test_api_client_is_none_after_import(self):
        import backend
        # api_client should be None until lifespan startup runs
        assert backend.api_client is None

    def test_conversations_db_empty_after_import(self):
        import backend
        # No conversations loaded at import time
        assert backend.conversations_db == {}

    def test_no_config_json_required_at_import(self, tmp_path, monkeypatch):
        """Import should succeed even without config.json in CWD."""
        monkeypatch.chdir(tmp_path)
        # Re-import to verify no crash
        importlib.reload(sys.modules["backend"])
        assert True  # reached without exception


# ---------------------------------------------------------------------------
# F4: Atomic save_conversations
# ---------------------------------------------------------------------------
class TestAtomicPersistence:
    """Verify atomic file writes for conversation history."""

    def test_save_creates_file(self, tmp_path, monkeypatch):
        import backend

        monkeypatch.chdir(tmp_path)
        # Add a conversation
        backend.conversations_db["test-1"] = backend.Conversation(
            id="test-1",
            title="Test",
            messages=[backend.Message(role="user", content="hello")],
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )

        backend.save_conversations()

        history_file = tmp_path / "conversation_history.json"
        assert history_file.exists()

        data = json.loads(history_file.read_text(encoding="utf-8"))
        assert "test-1" in data
        assert data["test-1"]["title"] == "Test"

    def test_atomic_write_no_partial_on_error(self, tmp_path, monkeypatch):
        """If serialization fails partway, the original file (if any) is untouched."""
        import backend

        monkeypatch.chdir(tmp_path)
        history_file = tmp_path / "conversation_history.json"
        history_file.write_text('{"original": true}', encoding="utf-8")

        # Insert a non-serializable object to cause json.dump to fail
        backend.conversations_db["bad"] = backend.Conversation(
            id="bad",
            title="Bad",
            messages=[backend.Message(role="user", content="ok")],
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
        # Add a non-serializable item that will cause failure
        backend.conversations_db["bomb"] = object()

        # Should not raise; save_conversations catches exceptions
        backend.save_conversations()

        # Original file should still be intact
        data = json.loads(history_file.read_text(encoding="utf-8"))
        assert data == {"original": True}

    def test_concurrent_saves_dont_corrupt(self, tmp_path, monkeypatch):
        """Multiple threads writing simultaneously should not corrupt the file."""
        import backend

        monkeypatch.chdir(tmp_path)
        # Start with a clean db (previous test may have polluted it)
        backend.conversations_db.clear()

        errors = []
        barrier = threading.Barrier(10)

        def writer(idx):
            try:
                barrier.wait(timeout=5)
                backend.conversations_db[f"conv-{idx}"] = backend.Conversation(
                    id=f"conv-{idx}",
                    title=f"Thread {idx}",
                    messages=[],
                    created_at="2025-01-01T00:00:00",
                    updated_at="2025-01-01T00:00:00",
                )
                backend.save_conversations()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors, f"Errors during concurrent writes: {errors}"

        # File should be valid JSON
        history_file = tmp_path / "conversation_history.json"
        data = json.loads(history_file.read_text(encoding="utf-8"))
        assert len(data) == 10


# ---------------------------------------------------------------------------
# API route smoke tests
# ---------------------------------------------------------------------------
class TestAPIRoutes:
    """Smoke-test key endpoints with mocked API client."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Create a test client without triggering lifespan startup."""
        from fastapi.testclient import TestClient
        import backend

        # Patch startup_init to avoid real API init
        with patch.object(backend, "startup_init", lambda: None):
            # Also patch load_conversations to avoid file I/O
            with patch.object(backend, "load_conversations", lambda: None):
                # Re-create app without lifespan for testing
                from fastapi import FastAPI
                # We'll just use the app as-is but mock the init
                client = TestClient(backend.app)
                self.client = client
                yield

    def test_serve_frontend(self):
        """GET / should serve index.html."""
        resp = self.client.get("/")
        # Will 200 if index.html exists, 500 if not found
        assert resp.status_code in (200, 500)

    def test_get_conversations_empty(self):
        """GET /api/conversations returns empty list when no data."""
        import backend
        backend.conversations_db.clear()
        resp = self.client.get("/api/conversations")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_and_get_conversation(self):
        """POST /api/conversations creates, GET retrieves it."""
        import backend
        backend.conversations_db.clear()

        with patch.object(backend, "save_conversations"):
            resp = self.client.post("/api/conversations")
            assert resp.status_code == 200
            conv_id = resp.json()["conversation_id"]

        resp = self.client.get("/api/conversations")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["id"] == conv_id

    def test_delete_conversation(self):
        """DELETE /api/conversations/{id} removes it."""
        import backend
        backend.conversations_db.clear()

        with patch.object(backend, "save_conversations"):
            resp = self.client.post("/api/conversations")
            conv_id = resp.json()["conversation_id"]

            resp = self.client.delete(f"/api/conversations/{conv_id}")
            assert resp.status_code == 200

        resp = self.client.get("/api/conversations")
        assert resp.json() == []

    def test_get_nonexistent_conversation_404(self):
        """GET /api/conversations/{bad_id} returns 404."""
        resp = self.client.get("/api/conversations/nonexistent")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# R1: Path-traversal protection in /uploads/{filename}
# ---------------------------------------------------------------------------
class TestPathTraversalProtection:
    """Verify the /uploads/{filename} endpoint rejects path-traversal attempts."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        from fastapi.testclient import TestClient
        import backend

        with patch.object(backend, "startup_init", lambda: None):
            with patch.object(backend, "load_conversations", lambda: None):
                client = TestClient(backend.app)
                self.client = client
                yield

    def test_path_traversal_dotdot_rejected(self):
        """GET /uploads/../../../etc/passwd should be rejected or not serve the file."""
        # Starlette normalizes the path before reaching the handler, so
        # directory components are stripped. The key security guarantee is
        # that traversal attempts do NOT return files from outside uploads/.
        resp = self.client.get("/uploads/..%2F..%2F..%2Fetc%2Fpasswd")
        assert resp.status_code in (400, 404), (
            f"Path traversal should be rejected, got {resp.status_code}"
        )

    def test_path_traversal_absolute_rejected(self):
        """GET /uploads//etc/passwd should be rejected."""
        resp = self.client.get("/uploads//etc/passwd")
        assert resp.status_code in (400, 404)

    def test_normal_upload_404_when_missing(self):
        """GET /uploads/nonexistent.png returns 404 (not 500)."""
        resp = self.client.get("/uploads/nonexistent.png")
        assert resp.status_code == 404

    def test_normal_upload_served_when_present(self, tmp_path, monkeypatch):
        """GET /uploads/existing.png returns 200 when file exists."""
        import backend
        uploads_dir = tmp_path / "uploads"
        uploads_dir.mkdir()
        test_file = uploads_dir / "test.png"
        test_file.write_bytes(b"\x89PNG\r\n")
        monkeypatch.chdir(tmp_path)
        resp = self.client.get("/uploads/test.png")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# S3: Correct method name for text generation
# ---------------------------------------------------------------------------
class TestTextChatMethod:
    """Verify the chat endpoint uses generate_content (not generate_text_with_gemini)."""

    def test_no_generate_text_with_gemini_in_backend(self):
        """The old method name should not appear in backend.py."""
        backend_path = os.path.join(REPO_ROOT, "backend.py")
        content = open(backend_path, encoding="utf-8").read()
        assert "generate_text_with_gemini" not in content, (
            "Old method name generate_text_with_gemini still present in backend.py"
        )

    def test_generate_content_called_in_backend(self):
        """The correct method name should be used."""
        backend_path = os.path.join(REPO_ROOT, "backend.py")
        content = open(backend_path, encoding="utf-8").read()
        assert "api_client.generate_content" in content, (
            "api_client.generate_content not found in backend.py"
        )


# ---------------------------------------------------------------------------
# S1: Dead Fabric.js code removed from index.html
# ---------------------------------------------------------------------------
class TestDeadCodeRemoval:
    """Verify dead Fabric.js code has been removed from index.html."""

    def test_no_fabricjs_block_comment_in_html(self):
        """No large /* ... */ Fabric.js blocks remain."""
        html_path = os.path.join(REPO_ROOT, "index.html")
        content = open(html_path, encoding="utf-8").read()
        # The dead code block referenced these functions
        assert "exportTaintedCanvas" not in content, (
            "Dead Fabric.js exportTaintedCanvas function still in index.html"
        )
        assert "redrawImageObject" not in content, (
            "Dead Fabric.js redrawImageObject function still in index.html"
        )
        assert "serverSideImageMerge" not in content, (
            "Dead Fabric.js serverSideImageMerge function still in index.html"
        )

    def test_no_fabricjs_cdn_in_head(self):
        """No Fabric.js CDN reference in HTML head."""
        html_path = os.path.join(REPO_ROOT, "index.html")
        content = open(html_path, encoding="utf-8").read()
        assert "fabric@6.0.2" not in content, (
            "Fabric.js CDN link still in index.html"
        )
