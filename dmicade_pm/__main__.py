import sys
import threading
import logging
import json

from .helper import parse_command_line_arguments
from .processmanager import DmicProcessManager
from .statemachine import DmicStateMachine
from .tasks import DmicTask
from .commands import commands_set_pm
from .uds_server import UdsServer
from .message_parser import DmicMessageParser
from .config_loader import DmicConfigLoader
from .logging_manager import DmicLogging

def main():
    parsed_args = parse_command_line_arguments(sys.argv)

    if 'conf' in parsed_args:
        print(json.dumps(DmicConfigLoader(parsed_args).global_config, indent=4))
        return

    print(__import__('os').getcwd())
    logger = DmicLogging(parsed_args)
    logger.setup()

    try:
        client = Client(parsed_args)

        debug_mode = 'debug' in parsed_args

        client.start(debug_mode)

    except Exception as e:
        logging.exception(e)

    logging.info('[MAIN]: Exit...')

class Client:
    SOCKET_PATH = '/tmp/dmicade_socket.s'

    def __init__(self, user_args):
        self._config_loader = DmicConfigLoader(user_args)
        self._uds_server = UdsServer(self.SOCKET_PATH)
        self._message_parser = DmicMessageParser(self._uds_server)
        self._process_manager = DmicProcessManager(self, self._uds_server, self._config_loader)
        commands_set_pm(self._process_manager)
        self._state_machine = DmicStateMachine(self._config_loader.global_config)

        self._message_parser.received_task_event += self.queue_state_task

    def start(self, debug_mode=False):
        logging.debug('[PM CLIENT] Start')

        self._uds_server.connected_event += lambda x: logging.info('[PM CLIENT] UDS server connected!')
        self._uds_server.disconnected_event += lambda x: logging.warning('[PM CLIENT] UDS server disconnected!')

        self._uds_server.start()

        if debug_mode:
            logging.info('[PM CLIENT] Running in Debug mode...')
            t = threading.Thread(target=self._debug, daemon=True)
            t.name = 'DebugThread'
            t.start()

        self._state_machine.run_event_loop_sync()

        logging.debug('[PM CLIENT] Close uds server...')
        self._uds_server.close()
        logging.debug('[PM CLIENT] Done...\n')

    def queue_state_task(self, task: DmicTask):
        self._state_machine.queue_task_for_state(task)

    def _debug(self):

        input_str = ''
        color_quickswitch_active = False
        cqs_field = ''

        while input_str != 'exit':
            input_str = input()

            try:
                if color_quickswitch_active:
                    if input_str == 'q':
                        color_quickswitch_active = False
                        print("EXITED COLOR QUICK SWITCH!")
                        continue

                    color_data = {cqs_field: input_str}
                    self._process_manager.set_button_colors(color_data)

                    continue

                elif input_str.find('btnc_qs') == 0 and len(input_str[8:]) > 0:
                    color_quickswitch_active = True
                    cqs_field = input_str[8:]
                    print("ENTERED COLOR QUICK SWITCH!")
                    continue

                elif input_str.find('btnc_s') == 0:
                    color_data = {input_str[7:10]: input_str[11:]}
                    self._process_manager.set_button_colors(color_data)

                elif input_str.find('btnc_c') == 0 and len(input_str[7:]) > 0:
                    cl = DmicConfigLoader(parse_command_line_arguments(sys.argv))
                    app_config = cl.configs[input_str[7:]]
                    color_data = app_config['buttonColors']
                    self._process_manager.queue_clear_button_colors()
                    self._process_manager.set_button_colors(color_data)

                elif input_str.find('btnc') == 0:
                    color_data = json.loads(input_str[5:])
                    print(color_data)
                    self._process_manager.set_button_colors(color_data)

                elif input_str.find('apps') == 0:
                    print( list(self._config_loader.configs.keys()) )
                    continue

            except Exception as e:
                print(e)

            self._message_parser.parse_uds_message(input_str)

        self._state_machine.stop_event_loop()


main()


def test_udsserver():
    print('[Client] Connecting to unix domain socket')
    server = UdsServer(Client.SOCKET_PATH)

    server.connected_event += lambda x: print('[Client] udsServer: Connected!')
    server.received_event += lambda msg: print('[Client] udsServer: Received: ', msg)
    server.disconnected_event += lambda x: print('[Client] udsServer: Disconnected...')

    server.start()

    while not server.is_connected():
        pass
    print('Connected!')

    # Test
    msg = ''
    while msg != 'exit' and server.is_connected():
        print('Send: ')
        msg = input()
        server.send(msg)

    server.close()

# test_udsserver()
