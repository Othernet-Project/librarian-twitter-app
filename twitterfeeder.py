import os
import json
import argparse
from datetime import datetime
from twitter import Twitter, OAuth


TOKEN = '2316526382-tP9Bbs1rMw1ReyqkgAiJdRAwNj58cAMXGT0VtrO'
TOKEN_SEC = 'XLaAx7XwBSlvOQPmFhAJnMP67r4XcQIGmgHQPU84b6n3c'
CON_KEY = 'SwFXhcGg6ElNvMJsGKl7h3QCy'
CON_KEY_SEC = 'Cwtyb0ftzoxLrMGCKPdFD5gIAtgpMwUFCN5LAiaNkQzCbOKhRY'

t = Twitter(auth=OAuth(TOKEN, TOKEN_SEC, CON_KEY, CON_KEY_SEC))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Downloads feeds later than'
                                     'specified post from specified feed')
    parser.add_argument('feed', metavar='USER', help='User name to get feed'
                        'for.')
    parser.add_argument('--since', metavar='POSTID', help='Post ID to retrieve'
                        'posts since, not including this ID.')
    args = parser.parse_args()

    statuses = t.statuses.user_timeline(screen_name=args.feed, since=args.since)
    for s in statuses:
        time_obj = datetime.strptime(s['created_at'],
                                      '%a %b %d %H:%M:%S +0000 %Y')
        date, time = time_obj.isoformat().split('T')
        id = str(s['id'])
        dump = json.dumps({'id': id, 'text': s['text'], 'date': date, 'time':
                           time},
                          sort_keys=True, separators=(',', ': '), indent=4)
        out = 'out'
        with open(os.path.join(out, id + '.json'), 'w') as f:
            f.write(dump)
