import os
import sys
import pathlib
from configparser import ConfigParser, NoOptionError
from ast import literal_eval

class _Configs():
    """
    * Container object which searchs for configurations in both the environement and the .ini config file.
    * Using configs.FOO_BAR the code will search for the FOO_BAR on the environment, if it is not found, then it will search on the .ini file for a fallback value. The value must be saved as:
    [foo]
    bar=value

    * Example: configs.LOG_LEVEL searches for the LOG_LEVEL env variable. If it is not set it will search for
    [log]
    level='value'

    The .ini file is selected according to either the DEV envirment variable or the environment or on the sys.argv
    example: if you start your main code with 'python code.py dev', the config manager will use the defaul values on the dev.ini. The same will happen if you set a DEV=True environment variable. This last one scenario is usefull for debugging Docker applications. If neither one of these options are set, then the default fallback will be read from production.ini.
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self._configs = ConfigParser()
        SOURCE_DIR = pathlib.Path(__file__).parent
        configs_dir = SOURCE_DIR / 'default_configs'

        IS_DEV = False
        if 'DEV' in os.environ:
            _TRUE = ('true', 'True', '1', 't')
            if os.getenv('DEV', False) in _TRUE:
                IS_DEV=True
        else:
            IS_DEV = 'dev' in sys.argv or 'DEV' in sys.argv

        config_file = configs_dir/'dev.ini' if IS_DEV else configs_dir/'production.ini'
        config_file = str(config_file.absolute())
        try:
            self._configs.read(config_file)
            self._configs['LOG']
        except KeyError:
            self._configs.read(f'../{config_file}')

    def __getattr__(self, key):
        try:
            config = os.getenv(key, self._configs.get(*key.split('_')))
        except (NoOptionError, TypeError):
            raise AttributeError(f'The \'{key}\' variable is not set neither on the env nor on the .ini file.')
        return literal_eval(config)

configs = _Configs()
