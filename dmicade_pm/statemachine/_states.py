class DmicState:
    """Informal interface for states."""

    def enter(self): -> None
        """Runs when entering the state."""
        pass

    def handle(self, task: dict): -> None
        """Handles occurring tasks."""
        pass

    def exit(self): -> None
        """Runs when exiting the state."""
        pass
