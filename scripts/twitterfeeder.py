import os
import json
import ftplib
import urllib
import argparse
from datetime import datetime
from twitter import Twitter, OAuth


TOKEN = '2316526382-tP9Bbs1rMw1ReyqkgAiJdRAwNj58cAMXGT0VtrO'
CON_KEY = 'XlQa2HVvxN4wU2KufRTvBlEy4'


def push_to_ftp(json, name, ip_list):
    now = datetime.now()
    ftp = ftplib.FTP()
    with open(ip_list) as f:
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


def get_image(tweet):
    """ Checks if an image is linked in the tweet data and returns url """
    try:
        media = tweet['entities']['media']
        if media[0]['type'] == "photo":
            link = media[0]['media_url_https']
            return link

    except KeyError:
        return False


def get_tweets(out, handle, stoken, scon_key):
    """ Retrieves tweets from Twitter API """
    t = Twitter(auth=OAuth(TOKEN, stoken, CON_KEY, scon_key))

    last_id = get_last_id(out, handle)
    if last_id:
        tweets = t.statuses.user_timeline(screen_name=handle, since_id=last_id)
    else:
        tweets = t.statuses.user_timeline(screen_name=handle)
    return tweets


def get_last_id(out, handle):
    try:
        with open(os.path.join(out, handle, 'last.txt'), 'r') as last_file:
            last = last_file.readline()
            print(last)
            return last
    except IOError:
        return False


def parse_tweet(tweet):
    """ Removes unnecessary data from tweet and returns """
    # Simple line to print tweets nicely
    #print(json.dumps(tweet, sort_keys=False, indent=4, separators=(',', ': ')))

    time_obj = datetime.strptime(tweet['created_at'],
                                 '%a %b %d %H:%M:%S +0000 %Y')
    date, time = time_obj.isoformat().split('T')
    id = str(tweet['id'])
    print(type(tweet['text']))
    parsed = {'id': id, 'text': tweet['text'].encode('utf8'), 'date': date, 'time': time,
            'handle': tweet['user']['screen_name']}
    return parsed


def write_tweet(out, tweet, ip_list):
    """ Writes each tweet to a file named ID.json, with relevant image """
    image = get_image(tweet)

    # No longer a full tweet after next line
    tweet = parse_tweet(tweet)
    handle = tweet['handle']
    dir = os.path.join(out, handle)
    name = tweet['id'] + '.json'
    json_file = os.path.join(dir, name)
    if image:
        ext = image[-4:]
        tweet['img'] = ext
        image_name = tweet['id'] + ext
        image_out = os.path.join(dir, 'img', image_name)
        if not os.path.exists(os.path.join(dir, 'img')):
            os.makedirs(os.path.join(dir, 'img'))
        urllib.urlretrieve(image, image_out)
    try:
        with open(json_file, 'w') as f:
            f.write(json.dumps(tweet, ensure_ascii=True, sort_keys=False, indent=4, separators=(',', ': ')))
    except IOError:
        try:
            os.mkdir(dir)
        except OSError:
            os.mkdir(out)
            os.mkdir(dir)
        with open(json_file, 'w') as f:
            f.write(json.dumps(tweet, sort_keys=False, indent=4, separators=(',', ': ')))
    #push_to_ftp(json_file, name, ip_list)


def write_last(id, out, handle):
    try:
        with open(os.path.join(out, handle, 'last.txt'), 'w') as last_file:
            last_file.write(id)
    except IOError:
        pass


def main():
    parser = argparse.ArgumentParser(
        description='Downloads tweets later than an optionally specified tweet'
        ' from a specified twitter handle')
    parser.add_argument('handle', metavar='USER', help='User name to get feed'
                        'for, looks like this: @BreakingNews.')
    parser.add_argument('con_secret', metavar='CON-SECRET', help='Secret '
                        'connection key, looks something like this: '
                        'Cwtyb0ftzoxLrMGCKPdFD5gIAtgpMwUFCN5LAiaNkQzCbOKhRY')
    parser.add_argument('token_secret', metavar='TOKEN-SECRET',
                        help='Secret token, looks something like this: '
                        'XLaAx7XwBSlvOQPmFhAJnMP67r 4XcQIGmgHQPU84b6n3c')
    parser.add_argument('--ip_list', metavar='FILE', help='List of ips in a '
                        'user:pass:IP format, one item per line.',
                        default='ips.lst')
    parser.add_argument('--out', metavar='DIR', help='Directory to output the '
                        'tweet files to.', default='out')
    parser.add_argument('--last-tweet', metavar='LAST-TWEET', help='Last tweet'
                        'downloaded, for retrieving only new tweets')
    args = parser.parse_args()

    out = args.out
    handle = args.handle[1:]
    stoken = args.token_secret
    scon_key = args.con_secret
    ip_list = args.ip_list

    raw_tweets = get_tweets(out, handle, stoken, scon_key)

    for raw_tweet in raw_tweets:
        # Writes the first (most recent) id to last.txt in a given directory.
        if raw_tweet == raw_tweets[0]:
            write_last(str(raw_tweet['id']), out, handle)
        write_tweet(out, raw_tweet, ip_list)


if __name__ == "__main__":
    main()
