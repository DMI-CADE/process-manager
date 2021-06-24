from pynput import keyboard
from .helper import DmicEvent


class KeyboardListener:
    """Continuous keyboard listener.

    Updates an event every time any keyboard key is pressed.
    
    Attributes:
      keyboard_triggered_event : DmicEvent
        Events that gets updated every time a key is triggered.
    """

    def __init__(self, config):
        self._listener = keyboard.Listener(on_press=self._on_press)
        self.keyboard_triggered_event = DmicEvent()
        self.menu_button_triggered_event = DmicEvent()
        self._menu_button = keyboard.KeyCode.from_char(config['menu_button'])

    def _on_press(self, key):
        """Callback function for when a key is triggered."""
        if key == self._menu_button:
            self.menu_button_triggered_event.update(key)
        else:
            self.keyboard_triggered_event.update(key)

    def start(self):
        """Starts the listening thread."""
        self._listener.start()

    def stop(self):
        """Stops the listening thread."""
        self._listener.stop()
