#!/usr/bin/env python

import yaml
import argparse
import logging
from collections import defaultdict

from bioblend import toolshed

DEFAULT_TOOL_SHED_URL = 'https://toolshed.g2.bx.psu.edu'


class ToolSheds(defaultdict):
    default_factory = toolshed.ToolShedInstance

    def __missing__(self, key):
        logging.debug('Creating new ToolShedInstance for URL: %s', key)
        return self.default_factory(url=key)


tool_sheds = ToolSheds()


def update_file(fn, owner=None, name=None, without=False):
    with open(fn + '.lock', 'r') as handle:
        locked = yaml.safe_load(handle)

    # Update any locked tools.
    for tool in locked['tools']:
        # If without, then if it is lacking, we should exec.
        logging.debug("Examining {owner}/{name}".format(**tool))

        if without:
            if 'revisions' in tool and not len(tool.get('revisions', [])) == 0:
                continue

        if not without and owner and tool['owner'] not in owner:
            continue

        if not without and name and tool['name'] != name:
            continue

        ts_url = tool.get('tool_shed_url', DEFAULT_TOOL_SHED_URL)
        if ts_url != DEFAULT_TOOL_SHED_URL:
            logging.warning('Non-default Tool Shed URL for %s/%s: %s', tool['owner'], tool['name'], ts_url)
        ts = tool_sheds[ts_url]

        logging.info("Fetching updates for {owner}/{name}".format(**tool))

        try:
            revs = ts.repositories.get_ordered_installable_revisions(tool['name'], tool['owner'])
        except Exception as e:
            print(e)
            continue

        logging.debug('TS revisions: %s' % ','.join(revs))
        latest_rev = revs[-1]
        if latest_rev in tool.get('revisions', []):
            # The rev is already known, don't add again.
            continue

        logging.info("Found newer revision of {owner}/{name} ({rev})".format(rev=latest_rev, **tool))

        # Get latest rev, if not already added, add it.
        if 'revisions' not in tool:
            tool['revisions'] = []

        if latest_rev not in tool['revisions']:
            # TS doesn't support utf8 and we don't want to either.
            tool['revisions'].append(str(latest_rev))
            tool['revisions'] = sorted(list(set(map(str, tool['revisions']))))

    with open(fn + '.lock', 'w') as handle:
        yaml.dump(locked, handle, default_flow_style=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fn', type=argparse.FileType('r'), help="Tool.yaml file")
    parser.add_argument('--owner', action='append', help="Repository owner to filter on, anything matching this will be updated. Can be specified multiple times")
    parser.add_argument('--name', help="Repository name to filter on, anything matching this will be updated")
    parser.add_argument('--without', action='store_true', help="If supplied will ignore any owner/name and just automatically add the latest hash for any repo that has no revision present.")
    parser.add_argument('--log', choices=('critical', 'error', 'warning', 'info', 'debug'), default='info')
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log.upper()))
    update_file(args.fn.name, owner=args.owner, name=args.name, without=args.without)
