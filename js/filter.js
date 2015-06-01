(function (window, $) {

  //Starts building the list from the twitter.BASE_DIR variable
  $.librarian.files.list(twitter.BASE_DIR, get_filter_list);

  //Builds html for the filter
  function build_filter(feeds) {
    var filter_list = [];
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
      twitter.async = [];
      $('#tweets').empty();
      tweet_dir = $(this).attr('id');
      $.librarian.files.list(tweet_dir, twitter.get_tweet_paths);
    });
    $('#all').click(function () {
      twitter.async = [];
      $('#tweets').empty();
      $.librarian.files.list(twitter.BASE_DIR, twitter.gather_folders);
    });
  }

  function get_filter_list(base_dir) {
    var feeds = [];
    var dir;
    var i = 0;
    var l = base_dir.dirs.length;
    if (l > 0) {
      for (; i < l; i++) {
        feeds.push(base_dir.dirs[i]);
      }
      insert_filter(feeds);
    }
  }

}(this, jQuery));
