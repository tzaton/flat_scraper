"""Load logging configuration
"""

import json
import logging.config
import os


def get_log_config(conf_file: str):
    """Configure logging based on config file

    Parameters
    ----------
    conf_file : str
        logging configuration file (.json)
    """
    with open(conf_file, 'r') as c:
        config = json.load(c)
    if not os.path.exists('log'):
        os.mkdir('log')
    logging.config.dictConfig(config)
    # disable urllib3 DEBUG messages
    logging.getLogger("urllib3").setLevel(logging.WARNING)
