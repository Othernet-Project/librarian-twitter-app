import os
import json
import argparse
import ftplib
from datetime import datetime
from twitter import Twitter, OAuth


TOKEN = '2316526382-tP9Bbs1rMw1ReyqkgAiJdRAwNj58cAMXGT0VtrO'
CON_KEY = 'XlQa2HVvxN4wU2KufRTvBlEy4'


def push_to_ftp(json, name):
    now = datetime.now()
    ftp = ftplib.FTP()
    with open(args.ip_list) as f:
        for line in f:
            u, p, i = line.split(':')
            user = u.strip()
            pass_key = p.strip()
            ip = i.strip()
            ftp.connect(ip)
            print('%s | Connected | %s' % (now, ip))
            ftp.login(user, pass_key)
            print('%s | Logged in | %s' % (now, user))
            try:
                ftp.cwd('/files/tweets')
            except ftplib.error_perm:
                ftp.cwd('/files/')
                ftp.mkd('tweets')
                ftp.cwd('/files/tweets')
            print('%s | Navigated | tweets' % now)
            with open(json, 'rb') as file:
                ftp.storbinary('STOR ' + name, file)
            print('%s | Wrote | %s' % (now, name))


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
    parser.add_argument('--ip_list', metavar='FILE', help='List of ips in a '
                        'user:pass:IP format, one item per line.',
                        default='ips.lst')
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
    name = handle + '.json'
    json_file = os.path.join(args.out, name)
    with open(json_file, 'w') as f:
        output = '[{}]'.format(', '.join(json_output))
        f.write(output)
    push_to_ftp(json_file, name)
