"""Arguments shared by the runners."""

import argparse


def add_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tag", default="main", help="run label stored with each record, e.g. pilot or main")
    parser.add_argument("--categories", type=lambda s: s.split(","), default=None)
    parser.add_argument("--replicates", type=int, default=None, help="keep replicates r0..r{n-1}")
    parser.add_argument("--variants", type=lambda s: s.split(","), default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--conditions", type=lambda s: s.split(","), default=None, help="clear and/or close")
