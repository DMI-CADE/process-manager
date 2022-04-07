import logging
import threading
import time
import math
import subprocess
import os


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

    def set_volume(self, volume_perc):
        """Sets system volume to given percentage."""

        logging.info(f'[VOLUME CONTROL] Set volume to {volume_perc}%.')

        self._audio_level = volume_perc
        self._audio_level_goal = volume_perc

        set_volume_cmd = self.CMD_SET_VOLUME % self._audio_level + '%'
        if os.name == 'nt':
            return
        subprocess.run(set_volume_cmd, shell=True, stdout=subprocess.PIPE)

    def fade_volume(self, goal_perc, max_fade_duration):
        """Sets values accordingly to move the volume to 'goal_perc'% in max_fade_duration seconds."""

        if goal_perc == self._audio_level_goal:
            #print(f'{goal_perc} {self._audio_level_goal} {self._audio_level}')
            #logging.debug(
                #f'[VOLUME CONTROL] Tried Volume fade to {goal_perc}% in {max_fade_duration}s ' +
                #f'but volume goal is already at {self._audio_level}%')
            return

        # Assume last level goal as starting point to make fade time relative to the max fade distance.
        audio_level_steps = abs(goal_perc - self._audio_level_goal)
        self._audio_level_goal = goal_perc
        if audio_level_steps == 0:
            logging.warning(f'[VOLUME CONTROL] Something went wrong... {self._audio_level=} {self._audio_level_goal=} {audio_level_steps=}')
            return

        self._fade_time_delta = max_fade_duration / audio_level_steps
        logging.info(f'[VOLUME CONTROL] Start Volume fade from {self._audio_level}% to {self._audio_level_goal}% in {max_fade_duration}s')
        logging.debug(f'[VOLUME CONTROL] {self._fade_time_delta=}\n')

    def _change_volume(self):
        """Waits for new audio level goal to be set. Then starts fading towards that level.
        
        Uses values set in class instance.
        Fades in increments of 1%.
        """

        while True:
            if self._audio_level != self._audio_level_goal:

                # Move volume level towards the goal.
                self._audio_level += math.copysign(1, self._audio_level_goal - self._audio_level)
                # logging.debug(f'[VOLUME CONTROL] {self._audio_level=}')

                set_volume_cmd = self.CMD_SET_VOLUME % self._audio_level + '%'
                if os.name != 'nt':
                    subprocess.Popen(set_volume_cmd, shell=True, stdout=subprocess.PIPE)
                
                time.sleep(self._fade_time_delta)

            else:
                time.sleep(self.CHECK_AUDIO_UPDATE_DELAY)
