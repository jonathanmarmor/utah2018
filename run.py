#!/usr/bin/env python

from experiment1 import Experiment1


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--dont-notate',
        help='dont generate notation',
        action="store_true")
    args = parser.parse_args()

    m1 = Experiment1()
    if not args.dont_notate:
        m1.notate()
