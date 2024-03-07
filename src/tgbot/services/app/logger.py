import logging

import betterlogging as bl


# TODO: Удалить эту функцию. Перенести ее функционал в функцию main в bot.py
def setup_logger(level=logging.INFO, ignored=""):
    bl.basic_colorized_config(level=level)
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    for ignore in ignored:
        logging.getLogger(ignore).disabled = True
