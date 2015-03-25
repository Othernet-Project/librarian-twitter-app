import os
import json
import argparse
from datetime import datetime
from twitter import Twitter, OAuth


TOKEN = '2316526382-tP9Bbs1rMw1ReyqkgAiJdRAwNj58cAMXGT0VtrO'
CON_KEY = 'XlQa2HVvxN4wU2KufRTvBlEy4'



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Downloads feeds later than'
                                     'specified post from specified feed')
    parser.add_argument('handle', metavar='USER', help='User name to get feed'
                        'for, looks like this: @BreakingNews.')
    parser.add_argument('con_secret', metavar='KEY', help='Secret connection'
                        'key, looks something like this: Cwtyb0ftzoxLrMGCKPdFD'
                        '5gIAtgpMwUFCN5LAiaNkQzCbOKhRY')
    parser.add_argument('token_secret', metavar='KEY', help='Secret token, '
                        'looks something like this: XLaAx7XwBSlvOQPmFhAJnMP67r'
                        '4XcQIGmgHQPU84b6n3c')
    parser.add_argument('--out', metavar='DIR', help='Directory to output the '
                        'tweet file to.', default='out')
    args = parser.parse_args()


    t = Twitter(auth=OAuth(TOKEN, args.token_secret, CON_KEY, args.con_secret))

    handle = args.handle[1:]
    json_output = []

    statuses = t.statuses.user_timeline(screen_name=handle)
    for s in statuses:
        time_obj = datetime.strptime(s['created_at'],
                                      '%a %b %d %H:%M:%S +0000 %Y')
        date, time = time_obj.isoformat().split('T')
        id = str(s['id'])
        dump = json.dumps({'id': id, 'text': s['text'], 'date': date, 'time':
                           time, 'handle': handle},
                          sort_keys=True, separators=(',', ': '))
        json_output.append(dump)
    out = 'out'
    with open(os.path.join(out, handle + '.json'), 'w') as f:
        output = '[{}]'.format(', '.join(json_output))
        f.write(output)
