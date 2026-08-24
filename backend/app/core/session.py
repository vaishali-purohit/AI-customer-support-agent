from typing import List, Optional


# Tracks the state of an individual customer conversation session
class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.turn_count = 0
        self.tool_call_count = 0
        self.state = "new"
        self.verification_attempts = 0
        self.pending_order_id: Optional[str] = None
        self.pending_email: Optional[str] = None
        self.history: List[dict] = []
