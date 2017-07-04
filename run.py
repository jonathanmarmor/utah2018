#!/usr/bin/env python

from movement1 import Movement1


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d',
        '--dont-notate',
        help='dont generate notation',
        action="store_true")
    args = parser.parse_args()

    m1 = Movement1()
    if not args.dont_notate:
        m1.notate()
