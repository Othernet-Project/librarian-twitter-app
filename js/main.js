//Starts the chain by getting the base dir "tweets"
//$.librarian.files.list(twitter.BASE_DIR, gather_folders);
$.librarian.files.list(twitter.DEFAULT_FEED, twitter.get_tweet_paths);
