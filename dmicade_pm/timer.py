import logging
import threading
import time
import datetime
import re
import subprocess

from .helper import DmicEvent


class DmicTimer:
    """Timer class for handling timeouts."""

    def __init__(self):
        self.timer_thread = threading.Timer(0, None)
        self.alert_event = DmicEvent()
        self._current_timer_length = 0

    def set_timer(self, seconds: int, log=True):
        """Starts the timer with given seconds."""

        self.stop(log)
        if log:
            logging.debug(f'[TIMER] Set timer to ({seconds})s.')

        self._current_timer_length = seconds

        self.timer_thread = threading.Timer(seconds, self._timer_callback)
        self.timer_thread.name = 'dmic_timer_thread'
        self.timer_thread.start()

    def _timer_callback(self):
        """Callback function for when the timer runs out.

        Triggers alert event.
        """

        logging.info(f'[TIMER] Timer ran out! ({self._current_timer_length})s')
        self.alert_event.update()

    def reset(self):
        """Resets the timer to previously set seconds."""

        # logging.debug('[TIMER] Reset timer...')
        self.set_timer(self._current_timer_length, False)

    def stop(self, log=True):
        """Stops the timer."""

        if log:
            logging.debug('[TIMER] Stop timer.')
        self.timer_thread.cancel()


class SleepManager():
    """TODO"""

    TIME_REGEX = r'^(?P<hour>(\d{1}|[01]\d|[2][0-4]))\:(?P<min>[0-6]\d)'
    CMD_SLEEP = 'rtcwake -m mem --date "%s"'

    def __init__(self, config):
        self.entered_sleeptime_event = DmicEvent()
        self.exit_sleeptime_event = DmicEvent()
        self.notify_sleep_event = DmicEvent()
        self.woke_up_event = DmicEvent()

        self._is_sleeping_time = False
        self._sleep_thread = None

        self.notification_interval = 60
        if 'sleep_notification_interval' in config:
            self.notification_interval = float(config['sleep_notification_interval'])

        # Get sleep and wake time
        if not ('sleep_time' in config and 'wake_time' in config):
            logging.warning('[SLEEP MANAGER] sleep_time and/or wake_time not set!')
            return

        faulty_time_value = False
        try:
            self._st = datetime.datetime.strptime(config['sleep_time'], '%H:%M')
        except ValueError as ve:
            logging.warning(f'[SLEEP MANAGER] sleep_{ve}')
            faulty_time_value = True

        try:
            self._wt = datetime.datetime.strptime(config['wake_time'], '%H:%M')
        except ValueError as ve:
            logging.warning(f'[SLEEP MANAGER] wake_{ve}')
            faulty_time_value = True

        if faulty_time_value:
            return

        st = re.match(self.TIME_REGEX, config['sleep_time'])
        wt = re.match(self.TIME_REGEX, config['wake_time'])
        if not (st and wt):
            logging.warning('[SLEEP MANAGER] sleep_time and/or wake_time not matching "hh:mm"!')
            return

        self.sleep_time = int(st.group('hour'))%24 * 3600 + int(st.group('min')) * 60
        self.wake_time = int(wt.group('hour'))%24 * 3600 + int(wt.group('min')) * 60
        self._st_values = ( int(st.group('hour'))%24, int(st.group('min')) )
        self._wt_values = ( int(wt.group('hour'))%24, int(wt.group('min')) )
        logging.info(f'[SLEEP MANAGER] sleep_time: {config["sleep_time"]} (={self.sleep_time}s), wake_time: {config["wake_time"]} (={self.wake_time}s)')

        # Start time checking.
        self._time_check_thread = threading.Thread(target=self._time_checking, daemon=True)
        self._time_check_thread.name = 'TimeCheckThread'
        self._time_check_thread.start() # TODO make start after full client init

    def sleep_now(self):
        logging.info('[SLEEP MANAGER] Start sleep mode!')

        if self._sleep_thread and self._sleep_thread.is_alive():
            logging.warning('[SLEEP MANAGER] Started sleep while sleep-thread still running!')

        self._sleep_thread = threading.Thread(target=self._sleep)
        self._sleep_thread.name = 'SleepProcessThread'
        self._sleep_thread.start()

    def _sleep(self):
        logging.debug('[SLEEP MANAGER] Run rtcwake...')
        # TODO set time correctly

        wake_datetime = datetime.datetime.now().replace(hour=self._wt.hour, minute=self._wt.minute, second=0)
        wake_is_today = wake_datetime > datetime.datetime.now()
        if not wake_is_today:
            wake_datetime += datetime.timedelta(days=1)

        wake_datetime_str = wake_datetime.strftime('%Y-%m-%d %H:%M')
        sleep_cmd = self.CMD_SLEEP % wake_datetime_str
        logging.debug(f'[SLEEP MANAGER] Run sleep cmd: {sleep_cmd}')
        sp = subprocess.Popen(sleep_cmd, stdout=subprocess.PIPE, shell=True)
        sp.wait()
        logging.info('[SLEEP MANAGER] Woke up!')
        self.woke_up_event.update()

    def _time_checking(self):
        """Sleep time checking thread function."""

        logging.debug('[SLEEP MANAGER] Start time checking...')

        while True:
            time.sleep(self.notification_interval)

            logging.debug('[SLEEP MANAGER] Check time...')

            t = time.localtime()
            now_s = t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec
            if self._is_sleep_time(self.sleep_time, self.wake_time, now_s):
                self._update_sleeping_time_state(True)
            else:
                self._update_sleeping_time_state(False)

            if self._is_sleeping_time:
                self.notify_sleep_event.update()

    def _is_sleep_time(self, sleep, wake, now, day_s=86400):
        """Checks if given time (now) is between sleep to wake time.

        Values/Timestamps expected to be seconds since midnight.
        Moves time window to 0 with delta time for easy comparison.
        """

        td = day_s - sleep
        return (now+td)%day_s < (wake+td)%day_s

    def _update_sleeping_time_state(self, is_sleeping):

        # Trigger sleep state change events.
        if is_sleeping != self._is_sleeping_time:
            if is_sleeping:
                logging.info('[SLEEP MANAGER] It is sleeping time...')
                self.entered_sleeptime_event.update()
            else:
                logging.info('[SLEEP MANAGER] Wake up time!')
                self.exit_sleeptime_event.update()

        self._is_sleeping_time = is_sleeping
