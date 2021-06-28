import logging
import re

from .helper import DmicEvent 
from .uds_server import UdsServer
from .tasks import *


class DmicMessageParser:
    """Message parser for dmic process manager.

    Parses messages from the UdsServer to tasks for the dmic
    state machine.
    
    Attributes:
      received_task_event : DmicEvent
        Event updated when a configured message is received by the
        uds server.
    """

    def __init__(self, uds_server: UdsServer):
        self.received_task_event = DmicEvent()

        uds_server.received_event += self.parse_uds_message

    def parse_uds_message(self, message):
        """Parses msgs received from the uds server into dmic tasks.
        
        When a matching massage is received it updates the
        received_task_event with the new task as a payload.

        Args:
          message:
            The message to parse.
        """

        logging.debug(f'[MSG PARSER] {message=}')

        msg_parts = re.match(r'(?P<msg_type>[^\:\s]+)\:?(?P<data>[^\:\s]*)', message)
        msg_type = msg_parts.group('msg_type')
        msg_data = msg_parts.group('data')

        if msg_type == 'start_app':
            task = DmicTask(DmicTaskType.START_APP, msg_data)
            self.received_task_event.update(task)
