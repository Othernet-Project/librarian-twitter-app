import os
import json
import ftplib
import urllib
import argparse
from datetime import datetime
from twitter import Twitter, OAuth


TOKEN = '2316526382-tP9Bbs1rMw1ReyqkgAiJdRAwNj58cAMXGT0VtrO'
CON_KEY = 'XlQa2HVvxN4wU2KufRTvBlEy4'
NOW = datetime.now()
TODAY = NOW.strftime('%m%d')


def ftp_login(line):
    ftp = ftplib.FTP()
    u, p, i = line.split(':')
    user = u.strip()
    pass_key = p.strip()
    ip = i.strip()
    ftp.connect(ip)
    print('%s | Connected | %s' % (NOW, ip))
    ftp.login(user, pass_key)
    print('%s | Logged in | %s' % (NOW, user))
    return ftp


def ftp_chdir(base_dir, ftp, dir):
    ftp.cwd('/')
    ftp.cwd(base_dir)
    try:
        ftp.cwd(dir)
    except ftplib.error_temp:
        ftp.mkd(dir)
        ftp.cwd(dir)
    print('%s | Navigated | %s/%s' % (NOW, base_dir, dir))


def ftp_rem_old(ftp):
    """ Removes files older than 3 days in the current directory """
    for f in ftp.nlst():
        #try:
            modifiedTime = ftp.sendcmd('MDTM ' + f)
            time = datetime.strptime(modifiedTime[4:], "%Y%m%d%H%M%S")
            delta = NOW - time
            if delta.days > 3:
                ftp.delete(f)
                print('%s | Removed Old | %s' % (NOW, ftp.pwd() + '/' + f))
            else:
                print('%s | Confirmed New | %s' % (NOW, ftp.pwd() + '/' + f))
        #except ftplib.error_perm:
            #print('%s | Found a Directory | %s' % (NOW, ftp.pwd() + '/' + f))
            #pass


def push_to_ftp(ftp, in_file, out_file):
    """
    Puts a local file (with path) to specified remote path.
    Takes the following arguments:
        ftp = ftp object on which to transfer
        in_file = local file to upload, format: /path/to/file.ext
        out_file = path to upload to, format: /path/to/file.ext
    """
    with open(in_file, 'rb') as file:
        try:
            ftp.storbinary('STOR ' + out_file, file)
            print('%s | Wrote | %s' % (NOW, ftp.pwd() + out_file))
        except ftplib.error_perm:
            print('%s | Already exists! | %s' % (NOW, ftp.pwd() + '/' + out_file))


def get_image_url(tweet):
    """ Checks if an image is linked in the tweet data and returns url """
    try:
        media = tweet['entities']['media']
        if media[0]['type'] == "photo":
            link = media[0]['media_url_https']
            return link

    except KeyError:
        return False


def get_image(tweet, dir):
    url = get_image_url(tweet)
    if url:
        ext = url[-4:]
        tweet['img'] = ext
        image_name = str(tweet['id']) + ext
        image_out = os.path.join(dir, image_name)
        urllib.urlretrieve(url, image_out)
        return [ext, image_out, image_name]


def get_last_id(out):
    try:
        with open(os.path.join(out, 'last.txt'), 'r') as last_file:
            last = last_file.readline()
            return last
    except IOError:
        return False


def get_tweets(dir, handle, stoken, scon_key):
    """ Retrieves tweets from Twitter API """
    t = Twitter(auth=OAuth(TOKEN, stoken, CON_KEY, scon_key))

    last_id = get_last_id(dir)
    if last_id:
        tweets = t.statuses.user_timeline(screen_name=handle, since_id=last_id)
    else:
        tweets = t.statuses.user_timeline(screen_name=handle)
    return tweets


def parse_tweet(tweet):
    """ Removes unnecessary data from tweet and returns """
    # Simple line to print tweets nicely
    #print(json.dumps(tweet, sort_keys=False, indent=4, separators=(',', ': ')))

    time_obj = datetime.strptime(tweet['created_at'],
                                 '%a %b %d %H:%M:%S +0000 %Y')
    date, time = time_obj.isoformat().split('T')
    id = str(tweet['id'])
    parsed = {'id': id, 'text': tweet['text'].encode('utf8'), 'date': date, 'time': time,
            'handle': tweet['user']['screen_name']}
    return parsed


def write_last(id, out):
    with open(os.path.join(out, 'last.txt'), 'w') as last_file:
        last_file.write(id)


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
    parser.add_argument('--updir', metavar='REMDIR', help='Directory to upload'
                        ' tweets to.', default='/files/unicef/')
    args = parser.parse_args()

    handle = args.handle[1:]
    stoken = args.token_secret
    scon_key = args.con_secret
    ip_list = open(args.ip_list, 'r')

    dir = os.path.join(args.out, handle)
    image_dir = os.path.join(dir, 'img')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    raw_tweets = get_tweets(dir, handle, stoken, scon_key)

    tweet_group = []
    image_list = []
    for raw_tweet in raw_tweets:
        tweet = parse_tweet(raw_tweet)
        img = get_image(raw_tweet, image_dir)
        if img:
            tweet['img'] = img[0]
            print("%s | Retrieved image | %s" % (NOW, img[1]))
            image_list.append([img[1], img[2]])
        tweet_group.append(json.dumps(tweet, sort_keys=False, indent=4,
                                      separators=(',', ': ')))
        if raw_tweet == raw_tweets[0]:
            last = str(tweet['id'])
            write_last(last, dir)

    for line in ip_list.readlines():
        ftp = ftp_login(line)
        ftp_chdir(args.updir, ftp, handle)

        name = '%s-%s.json' % (handle, TODAY)
        json_file = os.path.join(dir, name)
        content = '[\n' + ',\n'.join(tweet_group) + '\n]'
        with open(json_file, 'wb') as f:
            f.write(content.encode('utf8'))
        push_to_ftp(ftp, json_file, name)

        ftp_rem_old(ftp)

        ftp_chdir(args.updir, ftp, '%s/img' % handle)

        for img in image_list:
            push_to_ftp(ftp, img[0], img[1])

        ftp_rem_old(ftp)


if __name__ == "__main__":
    main()
