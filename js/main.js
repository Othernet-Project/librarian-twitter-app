(function (window, $) {
  // List of locales that use right-to-left text direction
  var rtlLocales = ['ar'];

  // We need the current locale (language). We can either parse the URL (the
  // locale is always the first segment of the path) or we can use Librarian's
  // lang API.
  var locale = $.librarian.lang.getLocale();

  var twtTemplate = [
    '<li class="tweet" id="ID">',
    '<p class="header">',
    '<img class="twitter-icon" src="icon.png"> ',
    '<span class="title">@HANDLE</span> - ',
    '<span class="timestamp">DATE at TIME UTC</span></p>',
    '<p class="text">TEXT</p>',
    '</li>'
  ].join('');

  var emptyTwt = '<li class="tweet">No tweets</li>';
  var async = [];
  var missingFolder = 'This folder does not exist';

  $.librarian.files.list('tweets', process);

  function process(dir_json) {
    if (!dir_json.files.length && dir_json.readme === missingFolder) {
      var output = '<li class="tweet"><p class="text">Tweets directory does not yet exist. It will be created automatically when you get a new data file. Please wait until a data file has been downloaded to use this app.</p></li>';
      $('#tweets').html(output);
      return;
    }
    if (!dir_json.files.length) {
      var output = '<li class="tweet"><p class="text">No tweets in directory. Please wait until a data file has been downloaded to use this app.</p></li>';
      $('#tweets').html(output);
      return;
    }
    var t;
    for (t in dir_json.files) {
      tweet = $.librarian.files.url(dir_json['files'][t]['path']);
      // Execute the AJAX request to fetch the messages and perform appropriate
      // operation depending on the response.
      var xhr = $.getJSON(tweet);
      async.push(xhr);
      xhr.fail(fail);
    }
    $.when.apply($, async).done(function () { 
      var results = [];
      var json;
      for (json in async) {
        var tweet_json = async[json]['responseJSON'];
        var tweet;
        for (tweet in tweet_json) {
          results.push(renderTweet(tweet_json[tweet]));
          }
        }
      results.reverse();
      $('#tweets').html(results);
      } );
    }

  function fail() {
    console.log('Failed to load');
  }

  function renderTweet(message) {
    return twtTemplate
      .replace('ID', message['id'])
      .replace('HANDLE', message['handle'])
      .replace('DATE', message['date'])
      .replace('TIME', message['time'])
      .replace('TEXT', message['text']);
  }
}(this, jQuery));
