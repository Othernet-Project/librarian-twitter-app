this.twitter = (function(window) {
  //Variable returned as this.twitter at the end
  var library = {};
  var results = [];

  library.async = []; 
  library.BASE_DIR = "dw-tweets"; 
  library.DEFAULT_FEED = "dw-tweets/dw_english";

  //Retrieves handle directories from base_dir and passes them to
  //get_tweet_paths
  library.gather_folders = function (base_dir) {
    var dir;
    var i = 0;
    var l = base_dir.dirs.length;
    if (l === 0) {
      console.log('No folders found');
      no_tweets();
    } else {
      for (; i < l; i++) {
        $.librarian.files.list(base_dir.dirs[i][0], bugger);
        //$.librarian.files.list(base_dir.dirs[i][0], get_tweet_paths);
      }
    }
  };
  
  //Retrieves tweet paths from a given handle directory and passes to get_tweet
  library.get_tweet_paths = function (tweet_dir) {
    var file;
    var tweet_path;
    var tweet_paths = [];
    var i = 0;
    var l = tweet_dir.files.length;
    for (; i < l; i++) {
      tweet_path = $.librarian.files.url(tweet_dir.files[i].path);
      tweet_paths.push(tweet_path);
    }
    get_tweet(tweet_paths);
    retrieve_tweets();
  };

  function bugger(data) {
    console.log(data);
  }

  emptyTwt = '<li class="tweet">No tweets</li>';
  missingFolder = 'This folder does not exist';

  // Tweet template vars/funcs
  twtTemplate = [
    '<div class="tweet" id="ID">',
    '<p class="header">',
    '<img class="twitter-icon" src="icon.png"> ',
    '<span class="title">@HANDLE</span> - ',
    '<span class="timestamp">DATE at TIME UTC</span></p>',
    '<p class="text">TEXT</p>',
    'IMG',
    '</div>'
  ].join('');

  //Function to be called in the event of no tweets being present
  function no_tweets() {
    $('#tweets').html('<li id="error"><p class="text">No tweets found!</p></li>');
  }

  //Gets tweet from path and passes them to rendering ajax handler
  function get_tweet(tweet_paths) {
    // Execute the AJAX request to fetch the messages and perform appropriate
    // operation depending on the response.
    var path;
    var i = 0;
    var l = tweet_paths.length;
    for (; i <l; i++) {
      var xhr = $.getJSON(tweet_paths[i]);
      library.async.push(xhr);
      xhr.fail(fail);
    }
  }

  //Ajax handler 
  function retrieve_tweets() {
    $.when.apply($, library.async).done(function () { 
      var args = [].slice.call(arguments); 
      if (args[1] === "success") {
        build_feed(args[0]);
        console.log(args);
      } else {
        var i = 0;
        var l = args.length;
        for (; i < l; i++) {
          build_feed(args[i][0]);
        }
      }
      printFeed();
    } );
  }

  function build_feed(chunk) {
    var i = 0;
    var l = chunk.length;
    for (; i < l; i++) {
      if (chunk[i].id) {
        results.push(renderTweet(chunk[i]));
      }
    }
  }

  function renderTweet(message) {
    var imgTag;
    var imgFile;
    if (message.img) {
      imgFile = message.id + message.img;
      imgTag = '<img src="/files/BASEDIR/HANDLE/img/IMG">'
        .replace('BASEDIR', library.BASE_DIR)
        .replace('HANDLE', message.handle.toLowerCase())
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

  function printFeed() {
    if (results.length > 0) {
      results.sort();
      results.reverse();
      $('#tweets').html(results);
      results = [];
    } else {
      no_tweets();
    }
  }

  return library;

}(this));
