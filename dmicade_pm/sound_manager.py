import logging
import threading
import time
import math
import subprocess


class VolumeController():

    CHECK_AUDIO_UPDATE_DELAY = 2

    CMD_SET_VOLUME = 'amixer -D pulse sset Master %s'

    def __init__(self):
        self._audio_level = 0
        self._audio_level_goal = 0
        self._fade_time_delta = 0
        
        self._change_volume_thread = threading.Thread(target=self._change_volume, daemon=True)
        self._change_volume_thread.name = 'VolumeControllerThread'
        self._change_volume_thread.start()

    def fade_volume(self, goal_perc, max_fade_duration):
        """Sets values accordingly to move the volume to 'goal_perc'% in max_fade_duration seconds."""

        self._audio_level_goal = goal_perc
        audio_level_steps = abs(goal_perc - self._audio_level)
        self._fade_time_delta = max_fade_duration / audio_level_steps
        logging.info(f'[VOLUME CONTROL] Start Volume fade from {self._audio_level}% to {self._audio_level_goal}% in {max_fade_duration}s')
        logging.debug(f'[VOLUME CONTROL] {self._fade_time_delta=}')

    def _change_volume(self):
        """Waits for new audio level goal to be set. Then starts fading towards that level.
        
        Uses values set in class object.
        Fades in increments of 1%.
        """

        time.sleep(2)
        print('jeff')
        self.fade_volume(100, 20)

        while True:
            if self._audio_level != self._audio_level_goal:

                # Move level thowards the goal.
                self._audio_level += math.copysign(1, self._audio_level_goal - self._audio_level)
                # logging.debug(f'[VOLUME CONTROL] {self._audio_level=}')

                set_volume_cmd = self.CMD_SET_VOLUME % self._audio_level + '%'
                subprocess.run(set_volume_cmd, shell=True, stdout=subprocess.PIPE)
                
                time.sleep(self._fade_time_delta)

            else:
                time.sleep(self.CHECK_AUDIO_UPDATE_DELAY)
