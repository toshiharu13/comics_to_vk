import logging
from pathlib import Path



if __name__ == '__main__':
    logging.basicConfig(
        level=logging.info(),
        filename='log.lod',
        filemode='w',
    )
    current_comics_link = 'https://xkcd.com/info.0.json'
