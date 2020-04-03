import json
import logging.config
import os


def get_log_config(conf_file):
    """ Load logging configuration from json file """
    with open(conf_file, 'r') as c:
        config = json.load(c)
    if not os.path.exists('log'):
        os.mkdir('log')
    logging.config.dictConfig(config)
