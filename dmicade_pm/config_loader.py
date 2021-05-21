import os
import json
import logging


CONFIG_REQUIREMENTS = {
    "executable": {
        "media": {
            "logo": "str"
        },
        "type": "str",
        "exe": "str"
    },

    "mame_rom": {
        "media": {
            "logo": "str"
        },
        "type": "str",
        "command": "str"
    }
}


class DmicConfigLoader:

    def __init__(self, apps_path):
        self.apps_path = apps_path
        self.configs = self.load_configs(self.apps_path)
        logging.debug(f'[CONFIG LOADER] Configured apps: {self.configs.keys()}')

    def load_configs(self, path: str):
        """TODO"""

        configs = dict()

        # Load directories
        apps_dir = os.listdir(path)
        logging.debug(f'[CONFIG LOADER] {apps_dir=}')
        
        for app in apps_dir:

            app_config_path = os.path.join(path, app, 'config.json')
            logging.debug(f'[CONFIG LOADER] {app_config_path=}')

            try:
                with open(app_config_path) as json_file:
                    app_config = json.load(json_file)
                    logging.debug(f'[CONFIG LOADER] {app_config=}')

            except FileNotFoundError as e:
                logging.warning(f'[CONFIG LOADER] Could not find config.json file for: {app}')
                continue
        
            config_is_valid = self.validate_config(app_config)
            if not config_is_valid:
                logging.warning(f'[CONFIG LOADER] Config for "{app}" is invalid...')
                continue

            configs[app] = app_config

        return configs

    def validate_config(self, config) -> bool:
        """TODO
        
        TODO make universal and recursive 
        """

        try:
            req_props = [] # required properties

            if config['type'] == 'executable':
                req_props = ['type', 'media', 'exe']
            elif config['type'] == 'mame_rom':
                req_props = ['type', 'media', 'command']

            for prop in req_props:
                if prop not in config:
                    logging.warning(f'[CONFIG LOADER] Property "{prop}" missing in app config.')
                    return False
                
        except Exception as e:
            return False

        return True
