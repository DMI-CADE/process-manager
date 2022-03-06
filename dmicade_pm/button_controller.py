import logging
import re


class DmicButtonController():

    def __init__(self):
        self.current_colors = ['000000' for i in range(12)]
        pass

    def change_colors(self, color_data):
        logging.debug(f"[BUTTON CONTROLLER] Convert Colors: {color_data=}")
        self.current_colors = self.convert_color_data(color_data)
        logging.info(f"[BUTTON CONTROLLER] Apply Colors: {self.current_colors}")

    def convert_color_data(self, data: object):
        color_data = self.current_colors.copy()

        if type(data) is dict:
            for key in data:
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
