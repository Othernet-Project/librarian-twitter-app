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

  var emptyTwt = '<li class="tweet">No messages</li>';

  var async = [];

  $.librarian.files.list('tweets', process);

  function process(dir_json) {
    for (t in dir_json['files']) {
      tweet = $.librarian.files.url(dir_json['files'][t]['path'])
      // Execute the AJAX request to fetch the messages and perform appropriate
      // operation depending on the response.
      var xhr = $.getJSON(tweet);
      async.push(xhr);
      xhr.fail(fail);
    }
    $.when.apply($, async).done(function () { 
      var results = [];
      for (json in async) {
        var resp = async[json]['responseJSON']
        results.push(renderTweet(resp))
        };
      results.reverse();
      $('#tweets').html(results)
      } )
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
