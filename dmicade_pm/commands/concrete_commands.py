import time
import logging

from ..processmanager import DmicProcessManager
from ..tasks import DmicTask, DmicTaskType


_PM = None

def commands_set_pm(process_manager: DmicProcessManager):
    global _PM
    _PM = process_manager


def c_test(data):
    print(f"""[COMMAND: TEST] Execute:
        |- data: {data}
        |- process manager: {_PM}""")


def c_change_state(state: DmicTask):
    change_state_task = DmicTask(DmicTaskType.CHANGE_STATE, state)
    _PM.queue_state_task(change_state_task)


def c_start_game(app_id: str):
    START_TRIES = 3
    RETRY_START_APP_DELAY = 1
    RETRY_VERIFIY_DELAY = 2 # Not lower then 2 for Godot games to be started-verified...

    logging.debug(f'[COMMAND: StartGame] Execute: {app_id=}')
    is_running = False

    if not _PM.verify_closed(app_id):
        logging.debug('[COMMAND: StartGame] Game already running... Closing game...')
        _PM.close_app(app_id)

    for retry in range(START_TRIES):
        logging.debug(f'[COMMAND: StartGame] {retry=}')

        _PM.close_app(app_id)

        _PM.start_app(app_id)
        is_running = _PM.verify_running(app_id)

        if not is_running:
            logging.debug(f'[COMMAND: StartGame] Verifiy: {is_running=}; Wait {RETRY_VERIFIY_DELAY}s and retry verify...')
            time.sleep(RETRY_VERIFIY_DELAY)
            is_running = _PM.verify_running(app_id)

        logging.debug(f'[COMMAND: StartGame] {is_running=}')

        if is_running:
            break

        time.sleep(RETRY_START_APP_DELAY)

    return is_running


def c_set_active_app(app_id: str):
    logging.debug(f'[COMMAND: SetActiveApp] Execute: {app_id=}')
    _PM.queue_state_task(DmicTask(DmicTaskType.SET_ACTIVE_APP, app_id))


def c_focus_app(app_id: str):
    FOCUS_REPS = 3
    FOCUS_REP_DELAY = 0.1

    logging.debug(f'[COMMAND: FocusApp] Execute: {app_id=}')
    _PM.focus_app(app_id)
    app_is_focused = False

    for rep in range(FOCUS_REPS):
        app_is_focused = _PM.verify_focus(app_id)
        if app_is_focused:
            break

        logging.debug(f'[COMMAND: FocusApp] app {app_id} not focused. Try: {rep+1}')
        time.sleep(FOCUS_REP_DELAY)

    return app_is_focused


def c_close_game(app_id: str):
    logging.debug(f'[COMMAND: CloseGame] Execute: {app_id=}')
    app_id = app_id

    _PM.close_app(app_id)

    is_closed = _PM.verify_closed(app_id)
    return is_closed


def c_send_to_ui(msg: str):
    logging.debug(f'[COMMAND: SendToUI] Execute: {msg=}')
    bytes_sent = _PM.send_to_ui(msg)

    send_success = bytes_sent and bytes_sent > 0

    return send_success


def c_verify_app_is_configured(app_id: str):
    return app_id in _PM.config_loader.configs


def c_set_interaction_feedback(is_on: bool):
    _PM.set_interaction_feedback(is_on)


def c_set_timer(seconds: int):
    logging.debug(f'[COMMAND: SetTimer] Execute: {seconds=}')
    _PM.set_timer(seconds)


def c_set_timer_game():
    logging.debug(f'[COMMAND: SetTimerGame] Execute.')
    c_set_timer(int(_PM.config_loader.global_config['game_timeout']))


def c_set_timer_menu():
    logging.debug(f'[COMMAND: SetTimerMenu] Execute.')
    c_set_timer(int(_PM.config_loader.global_config['menu_timeout']))


def c_stop_timer():
    _PM.stop_timer()


def c_set_volume(to: str):
    if to == 'min':
        _PM.set_volume(int(_PM.config_loader.global_config['volume_perc_low']))
    elif to == 'max':
        _PM.set_volume(int(_PM.config_loader.global_config['volume_perc_high']))


def c_enter_sleep():
    _PM.enter_sleep()


def c_get_color_config(app_id):
    app_config = _PM.config_loader.configs[app_id]
    color_config = None
    if 'buttonColors' in app_config:
        color_config = app_config['buttonColors']

    return color_config


def c_change_button_colors(color_data):
    logging.debug(f'[COMMAND: ChangeButtonColors] {color_data}')
    _PM.set_button_colors(color_data)


def c_button_colors_queue_clear():
    _PM.queue_clear_button_colors()


def c_set_app_button_colors(app_id):
    color_data = c_get_color_config(app_id)

    # If nothing is configured, set clear
    c_button_colors_queue_clear()

    if not color_data and 'button_colors_app_default' in _PM.config_loader.global_config:
        color_data = _PM.config_loader.global_config['button_colors_app_default']

    c_change_button_colors(color_data)


def c_set_menu_button_colors():
    color_config = _PM.config_loader.global_config['button_colors_menu']
    c_button_colors_queue_clear()
    c_change_button_colors(color_config)
