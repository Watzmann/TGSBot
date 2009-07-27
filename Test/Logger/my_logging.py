#!/usr/bin/env python

# example logging.py

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s %(asctime)s %(levelname)s %(message)s',
                    filename='./log.log',
                    )

logging.debug('A debug message')
logging.info('Some information')
logging.warning('A shot across the bows')
