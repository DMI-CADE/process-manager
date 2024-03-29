import os
import json
import logging
import re

DEFAULT_CONFIG_FILE_NAME = 'default_pm_config.json'

CONFIG_REQUIREMENTS = {
    "executable": {
        "type": "str",
        "exe": "str"
    },

    "mame_rom": {
        "type": "str",
        "command": "str"  # %%path%% gets replaced with the dmic app location
    }
}


class DmicConfigLoader:

    def __init__(self, cl_args):
        self.global_config = self._load_global_config(cl_args)
        self.apps_path = os.path.expanduser(self.global_config['apps_location'])
        self.configs = self._load_app_configs()
        logging.info(f'[CONFIG LOADER] Registered apps: {list(self.configs.keys())}')

    def _load_global_config(self, user_args: dict):
        """Loads the global process manager config.

        Default config properties get expanded and overwritten by given
        user_args.

        Args:
          user_args:
            A dictonary to expand and overwrite properties of returned
            config.

        Returns:
          Dictonary containing loaded process manager config.
        """

        pm_config = dict()

        default_config_path = re.sub(r'[^/]+$', DEFAULT_CONFIG_FILE_NAME, __file__)
        if os.name == 'nt':
            default_config_path = re.sub(r'[^/\\]+$', DEFAULT_CONFIG_FILE_NAME, __file__)
        logging.debug(f'[CONFIG LOADER] {default_config_path=}')

        try:
            with open(default_config_path) as json_file:
                default_pm_config = json.load(json_file)
                pm_config = default_pm_config
        except:
            logging.warning(f'[CONFIG LOADER] Could not load default config: {default_config_path}')

        pm_config.update(user_args)
        logging.debug(f'[CONFIG LOADER] PM Config: {json.dumps(pm_config, indent=4)}')

        return pm_config

    def _load_app_configs(self):
        """Loads all app configs into the configs member variable.

        An apps config is only loaded when a config.json with required properties existst.
        """

        configs = dict()

        # Load directories
        apps_dir = os.listdir(self.apps_path)
        logging.debug(f'[CONFIG LOADER] {apps_dir=}')
        
        for app in apps_dir:

            app_config_path = os.path.join(self.apps_path, app, 'config.json')
            logging.debug(f'[CONFIG LOADER] {app_config_path=}')

            try:
                with open(app_config_path) as json_file:
                    app_config = json.load(json_file)
                    logging.debug(f'[CONFIG LOADER] {app} config: {json.dumps(app_config, indent=4)}')

            except FileNotFoundError as e:
                logging.warning(f'[CONFIG LOADER] Could not find config.json file for: {app}')
                continue
        
            config_is_valid = self.validate_app_config(app_config)
            if not config_is_valid:
                logging.warning(f'[CONFIG LOADER] Config for "{app}" is invalid.')
                continue

            configs[app] = app_config

        return configs

    def validate_app_config(self, config) -> bool:
        """Validates the given config based on its type property.
        
        TODO make universal and recursive 
        """

        try:
            req_props = [] # required properties

            if config['type'] in ['executable', 'godot', 'unity']:
                req_props = ['type', 'exe']
            elif config['type'] == 'mame_rom':
                req_props = ['type','command']
            else:
                config_type = config['type']
                logging.warning(f'[CONFIG LOADER] Unknown application type "{config_type}"...')
                return False

            for prop in req_props:
                if prop not in config:
                    logging.warning(f'[CONFIG LOADER] Property "{prop}" missing in app config...')
                    return False

            # Make sure apps ID will not close UI.
            if config['type'] == 'unity':
                id_part_match = re.search(r"[a-ce-zA-CE-Z][a-zA-Z]{3,}", config['exe'].replace('.x86_64', ''))
                if id_part_match:
                    term = id_part_match.group() + r'.*\.x86_64'
                    print(term)
                    ui_intersect_match = re.search(term, 'DMI-CADE-UI.x86_64')
                    print(ui_intersect_match)
                    if ui_intersect_match:
                        logging.warning(f'[CONFIG LOADER] Apps file name intersects with UI name ("DMI-CADE-UI.x86_64"): {ui_intersect_match}')
                        return False
                else:
                    return False
                
        except KeyError:
            return False

        return True
