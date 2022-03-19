import logging
import re

from .serial_connection import DmicSerialConnector


class DmicButtonController():

    def __init__(self, global_config, serial_connector:DmicSerialConnector):
        self.current_colors = ['000000' for i in range(12)]

        self._color_order = global_config['button_led_order']
        self._clear_queued = False
        self.serial_connector = serial_connector

    def change_colors(self, color_data:any):
        """Connverts give color data and sends it to the connected serial connection."""

        # Special cases
        if 'RAINBOW' in color_data:
            logging.info(f"[BUTTON CONTROLLER] Apply Colors: rainbow")
            str_data = 'rainbow;'
            logging.debug(f"[BUTTON CONTROLLER] Send color data: '{str_data}'")
            self.serial_connector.write_data(str_data)
            return

        # Convert, order and send data.
        self.current_colors = self.convert_color_data(color_data)
        logging.info(f"[BUTTON CONTROLLER] Apply Colors: {self.current_colors}")

        str_data = ';'.join(self.order_color_data(self.current_colors)) + ';'
        logging.debug(f"[BUTTON CONTROLLER] Send color data: '{str_data}'")
        self.serial_connector.write_data(str_data)


    def clear_colors(self):
        """Changes all color data do clear/black."""

        self.change_colors('000000;'*12)


    def queue_clear(self):
        """Queues all clear color data as base for next color change."""

        self._clear_queued = True


    def convert_color_data(self, data: any):
        color_data = None
        if self._clear_queued:
            color_data = ['000000' for i in range(12)]
            self._clear_queued = False
        else:
            color_data = self.current_colors.copy()

        if type(data) is dict:

            # An "ALL" keyword inside a dict sets all color values to the given one as a base.
            if 'ALL' in data:
                c = self.get_hex_str(data['ALL'])
                color_data = [c for i in range(12)]

            for key in data:

                # Skip keywords.
                if key in []:
                    continue

                if not re.match('^P[12][A-F]$', key):
                    logging.warning(f'[BUTTON CONTROLLER] ApplyColorData: "{key}" does not match button descriptor pattern ( ^P[12][A-F]$ ). Color ingnored.')
                    continue

                pos = 6 * (int(key[1]) - 1) + 'ABCDEF'.index(key[2])

                value = self.get_hex_str(data[key])
                if not value:
                    logging.warning(f'[BUTTON CONTROLLER] ApplyColorData: "{key} : {data[key]}" is not a valid hex color value. Color ingnored.')
                    continue

                color_data[pos] = value

            return color_data

        if type(data) is str:

            # Turn into list.
            data = data.split(';')

        if type(data) is list:
            for i in range(len(data[:12])):
                hex_value = self.get_hex_str(data[i])
                if not hex_value:
                    logging.warning(f'[BUTTON CONTROLLER] ApplyColorData: Could not convert "{data[i]}" to hex value.') 
                    continue

                color_data[i] = hex_value

        return color_data


    def get_hex_str(self, data: str):
        result = data.upper()
        
        if re.match('[0-9A-F]{6}$', result):
            return result

        if re.match('[0-9A-F]{3}$', result):
            result = "".join([c*2 for c in result])

        else:
            result = None

        return result

    def order_color_data(self, color_data:list) -> list:
        """Orders color data by led order set in the global config."""

        return [color_data[6 * (int(pos_key[1]) - 1) + 'ABCDEF'.index(pos_key[2])] for pos_key in self._color_order]
