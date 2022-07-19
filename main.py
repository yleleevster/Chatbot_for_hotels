import heandlers
from config_data.config import bot
from loguru import logger

if __name__ == '__main__':
    logger.add('logs/logs_{time}.log', level='DEBUG', format="{time} {level} {message}", rotation="06:00",
               compression="zip")
    logger.debug('Error')
    logger.info('Information message')
    logger.warning('Warning')
    try:
        bot.infinity_polling()
    except Exception as exc:
        logger.error(f'Occurred {exc}')
