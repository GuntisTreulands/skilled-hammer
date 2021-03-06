import logging.config


def setup():
    logging.getLogger("requests").setLevel(logging.WARNING)

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[%(asctime)s] %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S %z'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
        },
        'loggers': {
            '': {
                'level': 'INFO',
                'handlers': ['console'],
            },
        },
    })
