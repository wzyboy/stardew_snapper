#!/usr/bin/env python

import os
import time
import shutil
import logging
import argparse
from xml.etree import ElementTree
from collections import namedtuple


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

StardewDate = namedtuple('StardewDate', 'year season day')


class StardewSnapper:

    def __init__(self, save_file, snap_dir=None, interval=60):
        self.save_file = save_file
        self.save_dir = os.path.dirname(save_file)
        self.snap_dir = snap_dir or self.save_dir
        self.interval = interval

        tree = ElementTree.parse(self.save_file)
        self.name = tree.find('./player/farmName').text
        self.uid = tree.find('./uniqueIDForThisGame').text
        self.date = None

        logger.info(
            f'I will poke {self.save_file} for changes every {interval} second(s). '
            f'If I detect one, I will take a snapshot of it and save it under {self.snap_dir}.'
        )

    def get_date(self):
        tree = ElementTree.parse(self.save_file)
        year = tree.find('./year').text
        season = tree.find('./currentSeason').text
        day = tree.find('./dayOfMonth').text

        return StardewDate(year, season, day)

    def take_snapshot(self, date):
        filename = f'{self.name}_{self.uid}_Y{date.year}_{date.season}_{date.day}'
        path = os.path.join(self.snap_dir, filename)
        shutil.copy2(self.save_file, path)
        self.date = date
        logger.info(f'Snapshot taken: {path}')

    def start(self):
        while True:
            date = self.get_date()
            if date != self.date:
                self.take_snapshot(date)
            time.sleep(self.interval)


def main():

    ap = argparse.ArgumentParser()
    ap.add_argument('save_file', help='the XML file of your game save')
    ap.add_argument('--snap-dir', help='optional snapshot dir, instead of the default (save dir)')
    ap.add_argument('--interval', type=int, default=60, help='seconds to detect changes')
    args = ap.parse_args()

    snapper = StardewSnapper(args.save_file, args.snap_dir, args.interval)
    snapper.start()


if __name__ == '__main__':
    main()
