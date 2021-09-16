#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

    Main App
    Detects if a newer file is available, process it

"""
__author__ = "Frederic Laurent"
__version__ = "1.0"
__copyright__ = "Copyright 2021, Frederic Laurent"
__license__ = "MIT"

import argparse
import sys
import logging
from easy_atom import helpers

import publisher


def main():
    """
        Main : process arguments and start App
    """

    logger = logging.getLogger("app")

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="fichier de parametres")
    parser.add_argument("-a", "--action", action="append",
                        choices=['feed', 'tweet'],
                        help="""
                            action disponible : <feed> -> produit un fichiers de syndication ATOM, 
                                               <tweet> -> poste 1 tweet concernant la mise a jour""")
    parser.add_argument("--info", help="Informations", action="store_true")

    args = parser.parse_args()

    if not args.action:
        sys.stderr.write("## Erreur >> Aucune action définie !\n\n")
        parser.print_help(sys.stderr)
        sys.exit(1)


    app = publisher.UpdatesPublisher(args.config)

    if args.info:
        logger.info("\n\n")
    if "feed" in args.action:
        app.feed_update()
    if "tweet" in args.action:
        app.tweet()



if __name__ == '__main__':
    loggers = helpers.stdout_logger(
        [
            "publisher"
        ],
        logging.DEBUG,
    )
    main()
