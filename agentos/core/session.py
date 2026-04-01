"""
AgentOS Session Persistence Layer

JSONL session logging with --continue/--resume/--fork-session support.
Every turn is appended as a single JSON line for efficient append-only storage.
Sessions accumulate indefinitely (no auto-pruning).
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any


class SessionManager:
    """Manages session persistence, resumption, and forking."""

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), ".agent-os", "sessions")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_id: Optional[str] = None
        self.current_session_path: Optional[Path] = None
        self.turn_count: int = 0

    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new session and return the session ID."""
        if session_id is None:
            date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
            short_uuid = uuid.uuid4().hex[:8]
            session_id = f"{date_str}-{short_uuid}"

        self.current_session_id = session_id
        self.current_session_path = self.base_dir / f"{session_id}.jsonl"
        self.turn_count = 0

        # Create file if it doesn't exist
        if not self.current_session_path.exists():
            self.current_session_path.touch()

        return session_id

    def append_turn(self, role: str, content: str, **kwargs) -> Dict[str, Any]:
        """Append a turn to the current session JSONL file."""
        if self.current_session_path is None:
            self.create_session()

        self.turn_count += 1
        turn_data = {
            "turn": self.turn_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "content": content,
            **kwargs,
        }

        assert self.current_session_path is not None
        with open(self.current_session_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(turn_data, ensure_ascii=False) + "\n")

        return turn_data

    def get_session_ids(self) -> List[str]:
        """List all available session IDs."""
        sessions = []
        for f in self.base_dir.glob("*.jsonl"):
            sessions.append(f.stem)
        return sorted(sessions)

    def get_last_session_id(self) -> Optional[str]:
        """Get the most recent session ID."""
        sessions = self.get_session_ids()
        return sessions[-1] if sessions else None

    def load_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Load all turns from a session."""
        session_path = self.base_dir / f"{session_id}.jsonl"
        if not session_path.exists():
            return []

        turns = []
        with open(session_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    turns.append(json.loads(line))

        return turns

    def continue_session(self) -> str:
        """Resume the last session."""
        last_id = self.get_last_session_id()
        if last_id is None:
            return self.create_session()

        self.current_session_id = last_id
        self.current_session_path = self.base_dir / f"{last_id}.jsonl"
        self.turn_count = len(self.load_session(last_id))
        return last_id

    def resume_session(self, session_id: str) -> str:
        """Resume a specific session."""
        session_path = self.base_dir / f"{session_id}.jsonl"
        if not session_path.exists():
            raise FileNotFoundError(f"Session {session_id} not found")

        self.current_session_id = session_id
        self.current_session_path = session_path
        self.turn_count = len(self.load_session(session_id))
        return session_id

    def fork_session(self, session_id: str, up_to_turn: Optional[int] = None) -> str:
        """Branch from a past conversation."""
        source_turns = self.load_session(session_id)
        if up_to_turn is not None:
            source_turns = [t for t in source_turns if t["turn"] <= up_to_turn]

        new_id = self.create_session()
        assert self.current_session_path is not None
        with open(self.current_session_path, "w", encoding="utf-8") as f:
            for turn in source_turns:
                f.write(json.dumps(turn, ensure_ascii=False) + "\n")

        self.turn_count = len(source_turns)
        return new_id

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of a session."""
        turns = self.load_session(session_id)
        if not turns:
            return {"session_id": session_id, "turn_count": 0}

        user_turns = sum(1 for t in turns if t["role"] == "user")
        assistant_turns = sum(1 for t in turns if t["role"] == "assistant")
        tool_turns = sum(1 for t in turns if t["role"] == "tool")

        return {
            "session_id": session_id,
            "turn_count": len(turns),
            "user_turns": user_turns,
            "assistant_turns": assistant_turns,
            "tool_turns": tool_turns,
            "first_turn": turns[0].get("timestamp", "unknown"),
            "last_turn": turns[-1].get("timestamp", "unknown"),
        }
