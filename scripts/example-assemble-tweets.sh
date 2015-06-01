
#!/bin/bash

## Confidential keys for use with twitter API
CSEC=Secret connection key
TSEC=Secret app token

## Misc variables
SCRIPTDIR=$(dirname "$BASH_SOURCE")
PYTHON=/usr/bin/python2
SCRIPT="$SCRIPTDIR/twitterfeeder.py"

## Args to pass to feeder script

# IPs files format; one item per line, example item:
#    USERNAME:PASSWORD:127.0.0.1
IPSFILE="$SCRIPTDIR/ips.lst"

# Directory to log to
LOG=$OUT/twitterfeeder.log

# Feeds to upload, format:
# FEEDS="@HANDLE @HANDLE..."
FEEDS="@unicef @dw_english"

# Output directory
OUT=out/

# Directory to upload to on the remote server; no trailing slash on directory
UPLOADDIR="/files/unicef-tweets"

mkdir -p $OUT

process_feed() {
  $PYTHON $SCRIPT --out=$OUT --updir $UPLOADDIR --ip_list=$IPSFILE $1 $TSEC $CSEC
}

for feed in $FEEDS; do
  process_feed "$feed"
done
