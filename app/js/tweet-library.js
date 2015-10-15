this.twitter = (function(window) {
  var library = {}; //Variable 'library' returned as this.twitter at the end
  var results = []; //Variable 'results' used as list of finished tweet divs

  library.async = []; //Variable 'async' exposed so it may be emptied
  library.BASE_DIR = "tweets"; //Directory used for finding tweets
  library.DEFAULT_FEED = "tweets/breakingnews"; //Initial twitter feed

  library.list_tweets(base_dir=library.BASE_DIR, handle='library.DEFAULT_FEED, page='all') {
    $.librarian.files.list(handle, twitter.get_tweet_paths);
  }

  //Builds list of handle paths from 'BASE_DIR' and calls get_tweet_paths
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
  
  //Retrieves json paths from a handle path and calls get_tweet on the json path
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

  emptyTwt = '<li class="tweet">No tweets</li>';
  missingFolder = 'This folder does not exist';

  // Tweet template
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

  //Populates '#tweets' with no tweet message
  function no_tweets() {
    $('#tweets').html('<li id="error"><p class="text">No tweets found!</p></li>');
  }

  //Takes a list of paths and loads each item into the ajax handler
  function get_tweet(tweet_paths) {
    // Execute the AJAX request to fetch the messages and perform appropriate
    // operation depending on the response.
    var path;
    var i = 0;
    var l = tweet_paths.length;
    for (; i <l; i++) {
      var xhr = $.getJSON(tweet_paths[i]); //Create request object
      library.async.push(xhr); //Put it into async variable for collection
      xhr.fail(fail); //If it failed, do fail
    }
  }

  //Ajax handler: Waits until async is finished then calls build_feed
  function retrieve_tweets() {
    $.when.apply($, library.async).done(function () { 
      var args = [].slice.call(arguments); 
      if (args[1] === "success") { //This check to see if it's one tweet could
        build_feed(args[0]);       //really be improved
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

  //
  function build_feed(json) {
    var i = 0;
    var l = json.length;
    for (; i < l; i++) {
      if (json[i].id) { //This should probably fail noisily
        results.push(renderTweet(json[i]));
      }
    }
  }

  //Takes a tweet and returns it rendered as html
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

  //Generic logging function
  function bugger(data) {
    console.log(data);
  }

  //Generic failure logging function
  function fail(obj, status, err) {
    console.log(status);
    console.log(err);
    console.log(obj.getAllResponseHeaders());
  }

  //Sort results then populate '#tweets' with results or call no_tweets
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
