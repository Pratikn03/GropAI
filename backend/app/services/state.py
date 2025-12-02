from typing import TypedDict

class AppState(TypedDict):
    consent_enabled: bool

STATE: AppState = {"consent_enabled": False}
