#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

    Updates


"""
__author__ = "Frederic Laurent"
__version__ = "1.0"
__copyright__ = "Copyright 2021, Frederic Laurent"
__license__ = "MIT"

import logging
import datetime
import sys
from hashlib import blake2b

from easy_atom import action
from easy_atom import atom
from easy_atom import helpers

import pprint

pp = pprint.PrettyPrinter(indent=4)


class UpdatesPublisher:
    def __init__(self, config_filename):
        self.logger = logging.getLogger("publisher")
        self.config = helpers.load_json(config_filename)

        self.docmap = {}
        if 'docmap' in self.config:
            self.docmap = helpers.load_json(self.config['docmap'])
            self.logger.debug(f'Documentation : {len(self.docmap)} documents')

        self.feed_data = {}
        self.feed = None
        if self.config['feed_config']:
            self.feed = atom.Feed('domain', selfhref=self.config['feed_base'],
                                  config_filename=self.config['feed_config'])

    def summary140(self, data):
        self.logger.info("Texte du Tweet ")
        txt = self.makesummary(data)
        return f"CI-SIS @esante_gouv_fr: {txt} #esanté"

    def tweet(self):
        self.logger.info("MAJ Tweet")
        if not self.config['twitter_config']:
            self.logger.warning("Aucune configuration pour twitter.")
            return

        act = action.TweetAction(conf_filename=self.config['twitter_config'])

        for key, data in self.docmap.items():
            if "status" in data and data["status"] == "new":
                txt = self.summary140(data)
                self.logger.debug(txt)
                url_tweet = act.process(txt)
                self.logger.info(f"URL {url_tweet}")
                sys.exit(0)

    def makesummary(self, data):
        txt = "Mise à jour"
        if data["category"] == "Annexe":
            txt += " de l'annexe"
        elif data["category"] == "Volet":
            txt += f" du volet"
        txt += f" {data['category_title']} [{data['family']}]"
        if len(data['date']) > 0:
            txt += f" date {data['date']}"
        if len(data['version']) > 0:
            txt += f", version {data['version']}"
        return txt

    def makefeedentry(self, key, data):
        self.logger.debug(f"make entry feed {data['category_title']}")
        h = blake2b(digest_size=10)
        h.update(key.encode())

        d = {'type': 'CI-SIS',
             'id': f'urn:ans:cisis:{h.hexdigest()}',
             'version': data['version'],
             'date': datetime.datetime.now(datetime.timezone.utc).isoformat(sep='T'),
             'url': None,
             'title': data["title"],
             'summary': self.makesummary(data),
             'files': [data['url']],
             'files_props': [{
                 "size": data['size'],
                 "url": data['url'],
                 "type": 'data',
                 "http_status": 200
             }],
             'html': None,
             'available': True}
        return d

    def feed_update(self):
        self.logger.info(f"Feed update : [{self.config['feed_data']}] ")
        self.feed_data = helpers.load_json(self.config['feed_data'])
        if 'doc' not in self.feed_data:
            self.feed_data['doc'] = []

        self.logger.debug(f"Nb entry avant ajout : {len(self.feed_data)}")

        for key, data in self.docmap.items():
            if "status" in data and data["status"] == "new":
                entry = self.makefeedentry(key, data)
                self.feed_data['doc'].insert(0, entry)

        self.logger.debug(f"Nb entry apres ajout : {len(self.feed_data)}")
        feed = self.feed.generate(self.feed_data['doc'])

        helpers.save_json(self.config['feed_data'], self.feed_data)
        self.feed.save(feed)
        self.feed.rss2()

        if 'feed_ftp' in self.config:
            act = action.UploadAction(conf_filename=self.config['feed_ftp'])
            act.process([self.feed.feed_filename, self.feed.rss2_filename])
