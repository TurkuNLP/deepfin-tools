#!/usr/bin/env python3

# Check log file(s) for potential issues.


import sys
import os
import re


LOSS_RE = re.compile('^INFO:tensorflow:loss = (\S+), step = (\d+).*')


# Warn when increase in loss exceeds threshold
LOSS_INCREASE_THRESHOLD = 2


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Check for issues in log(s)')
    ap.add_argument('-q', '--quiet', default=False, action='store_true',
                    help='Only print out warnings and errors.')
    ap.add_argument('log', nargs='+')
    return ap


def check_losses(fn, loss_step, options):
    prev_loss, max_increase, max_inc_step = None, None, None
    for loss, step in loss_step:
        if prev_loss is not None:
            diff = loss-prev_loss
            if diff > LOSS_INCREASE_THRESHOLD:
                print('Warning: {}: loss increases by {:.1f} at step {}'.format(
                    os.path.basename(fn), diff, step))
            if max_increase is None or diff > max_increase:
                max_increase, max_inc_step = diff, step
        prev_loss = loss
    if not options.quiet:
        print('{}: max increase in loss {} at step {}'.format(
            os.path.basename(fn), max_increase, max_inc_step))


def check_log(fn, options):
    loss_step = []
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip()
            m = LOSS_RE.match(l)
            if m:
                loss, step = m.groups()
                loss_step.append((float(loss), int(step)))
    if not loss_step:
        if not options.quiet:
            print('{}: no losses found'.format(os.path.basename(fn)))
    else:
        check_losses(fn, loss_step, options)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.log:
        check_log(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
