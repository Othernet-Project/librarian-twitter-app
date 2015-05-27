(function (window, $) {
  var async = [];

  // List of locales that use right-to-left text direction
  var rtlLocales = ['ar'];

  // We need the current locale (language). We can either parse the URL (the
  // locale is always the first segment of the path) or we can use Librarian's
  // lang API.
  var locale = $.librarian.lang.getLocale();

  var emptyTwt = '<li class="tweet">No tweets</li>';
  var missingFolder = 'This folder does not exist';

  // Tweet template vars/funcs
  var twtTemplate = [
    '<div class="tweet" id="ID">',
    '<p class="header">',
    '<img class="twitter-icon" src="icon.png"> ',
    '<span class="title">@HANDLE</span> - ',
    '<span class="timestamp">DATE at TIME UTC</span></p>',
    '<p class="text">TEXT</p>',
    'IMG',
    '</div>'
  ].join('');

  //Starts the chain by getting the base dir "tweets"
  $.librarian.files.list('tweets', gather_folders);


  //Retrieves handle directories from base_dir and passes them to
  //get_tweet_paths
  function gather_folders(base_dir) {
    var feeds = [];
    var dir;
    var i = 0;
    var l = base_dir.dirs.length;
    for (; i < l; i++) {
      feeds.push(base_dir.dirs[i]);
      $.librarian.files.list(base_dir.dirs[i][0], get_tweet_paths);
    }
    insert_filter(feeds);
  }
  
  //Retrieves tweet paths from a given handle directory and passes to get_tweet
  function get_tweet_paths(tweet_dir) {
    var file;
    var tweet_path;
    var i = 0;
    var l = tweet_dir.files.length;
    for (; i < l; i++) {
      tweet_path = $.librarian.files.url(tweet_dir.files[i].path);
      get_tweet(tweet_path);
    }
    retrieve_tweets();
  }

  //Gets tweet from path and passes them to rendering ajax handler
  function get_tweet(tweet_path) {
    // Execute the AJAX request to fetch the messages and perform appropriate
    // operation depending on the response.
    var xhr = $.getJSON(tweet_path);
    async.push(xhr);
    xhr.fail(fail);
  }

  function renderTweet(message) {
    var imgTag;
    var imgFile;
    if (message.img) {
      imgFile = message.id + '.' + message.img;
      imgTag = '<img src="/files/tweets/HANDLE/img/IMG">'
        .replace('HANDLE', message.handle)
        .replace('IMG', imgFile);
    } else {
      imgTag = "";
    }
    return twtTemplate
      .replace('ID', message.id)
      .replace('HANDLE', message.handle)
      .replace('DATE', message.date)
      .replace('TIME', message.time)
      .replace('TEXT', message.text)
      .replace('IMG', imgTag);
  }

  function fail(obj, status, err) {
    console.log(status);
    console.log(err);
    console.log(obj.getAllResponseHeaders());
  }

  function retrieve_tweets() {
    $.when.apply($, async).done(function () { 
      var results = [];
      var json;
      var args = [].slice.call(arguments); 
      var i = 0;
      var l = args.length;
      for (; i < l; i++) {
        results.push(renderTweet(args[i][0]));
      }
      if (results.length > 0) {
        results.reverse();
        $('#tweets').html(results);
      } else {
        $('#tweets').html('<li id="error"><p class="text">No tweets found!</p></li>');
      }
    } );
    async = [];
  }

  //Builds html for the filter
  function build_filter(feeds) {
    var filter_list = [
      '<a class="feed" id="all" href="#">All Feeds</a>'
    ];
    var i = 0;
    var l = feeds.length;
    for (; i < l; i++) {
      feed = feeds[i][1];
      path = feeds[i][0];
      filter_list.push('<a class="feed" href="#" id="PATH">FEED</a>'
        .replace('FEED', feed)
        .replace('PATH', path)
      );
    }
    return filter_list;
  }

  function insert_filter(feeds) {
    var filter_list = build_filter(feeds);
    if (filter_list.length > 2) {
      $('#feeds').html(filter_list);
    } 
    if (filter_list.length <= 2) {
      $('#feeds').html('<!-- Only one feed is available -->');
    }
    //$('.feed').click(function () {console.log($(this).attr('id'));});
    $('.feed').click(function () {
      $('#tweets').empty();
      tweet_dir = $(this).attr('id');
      $.librarian.files.list(tweet_dir, get_tweet_paths);
    });
    $('#all').click(function () {
      $('#tweets').empty();
      tweet_dir = $(this).attr('id');
      $.librarian.files.list("/tweets", gather_folders);
    });
  }

}(this, jQuery));
