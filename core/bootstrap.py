"""One-time startup tasks that make a deployment self-healing.

Render runs the commands in ``build.sh``/``start.sh`` when they are configured.
If a service still uses an older command, the WSGI entry point calls this module
so migrations and the admin account are created before the first request.
"""

import logging
import os
import time
from pathlib import Path

from django.core.management import call_command

try:
    import fcntl
except ImportError:
    fcntl = None

logger = logging.getLogger(__name__)

DEFAULT_LOCK_PATH = Path("/tmp/olive_pharma_startup.lock")
_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off"}
_MAX_ATTEMPTS = 3
_RETRY_DELAY_SECONDS = 2


def startup_tasks_enabled():
    override = os.environ.get("RUN_STARTUP_TASKS")
    if override is not None:
        return override.strip().lower() not in _FALSY
    return os.environ.get("RENDER", "").strip().lower() in _TRUTHY


def run_startup_tasks(lock_path=None):
    """Run migrations and provision the admin once per container."""
    if not startup_tasks_enabled():
        return False

    lock_path = Path(lock_path or DEFAULT_LOCK_PATH)
    done_path = lock_path.with_name(f"{lock_path.name}.done")
    if done_path.exists():
        return False

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w") as lock_file:
        if fcntl is not None:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            if done_path.exists():
                return False

            if not _apply_migrations_and_superuser():
                logger.critical(
                    "Startup tasks failed; the service is running but login may "
                    "not work until migrations succeed."
                )
                return False

            done_path.write_text("ok\n")
            logger.info("Startup tasks: complete")
            return True
        finally:
            if fcntl is not None:
                fcntl.flock(lock_file, fcntl.LOCK_UN)


def _apply_migrations_and_superuser():
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            logger.info(
                "Startup tasks: applying migrations (attempt %s/%s)",
                attempt,
                _MAX_ATTEMPTS,
            )
            call_command("migrate", interactive=False, verbosity=0)
            call_command("ensure_superuser")
            return True
        except Exception:
            logger.exception("Startup tasks attempt %s failed", attempt)
            if attempt < _MAX_ATTEMPTS:
                time.sleep(_RETRY_DELAY_SECONDS)
    return False
