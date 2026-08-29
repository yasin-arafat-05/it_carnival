import threading
from typing import Dict, Any


class CriticalSectionLockManager:
    """
    In-Memory Threading Lock Manager.

    Uses Python's `threading.RLock` (Reentrant Lock) to provide strict mutual exclusion
    and prevent race conditions across concurrent threads executing critical sections
    (such as money transfers, user account balance updates, and request acceptances).
    """

    def __init__(self):
        self._master_lock = threading.RLock()
        self._key_locks: Dict[str, threading.RLock] = {}

    def get_lock(self, key: str) -> threading.RLock:
        """
        Retrieves or creates a thread-safe RLock instance for a given resource key.

        Args:
            key (str): Unique resource lock identifier (e.g. 'user_<id>' or 'req_<id>').

        Returns:
            threading.RLock: Threading lock object for context management.
        """
        with self._master_lock:
            if key not in self._key_locks:
                self._key_locks[key] = threading.RLock()
            return self._key_locks[key]


# Global Threading Lock Manager Instance
LOCK_MANAGER = CriticalSectionLockManager()
