// Load subitem linking information
$('span.current-match[data-subitem]').each(function () {
  subitem_id = $(this).attr('data-subitem');
  $.ajax({
       type: "GET",
       url: '/api/subitem/' + geordi.current_index + '/' + subitem_id,
       dataType: 'json',
       context: this
  })
  .done(function(data) {
       topmatch = data.document._source._geordi.matchings.matchings[0];
       type = topmatch.type;
       text = type + ' ';
       $.each(topmatch.mbid, function(index, mbid) {
           text = text + '<a href="https://musicbrainz.org/' + type + '/' + mbid + '">' + mbid.slice(0,4) + '…' + mbid.slice(-4) + '</a>, '
       });
       text = text.slice(0,-2);
       $(this).html(text + ' [' + topmatch.user + ']');
  });
});

// Open modal dialogs
$('.subitem-linker').click(function(e) {
  e.preventDefault();
  subitem_id = $(this).attr('data-subitem');
  $('#subitem-linker-content-' + subitem_id).modal();
});
$('.item-linker').click(function(e) {
  e.preventDefault();
  $('#item-linker-content').modal();
});

// AJAX form submission
$('form.match-form').submit(function (e) {
  e.preventDefault();
  $.ajax({
       type: "GET",
       url: $(this).attr('action'),
       data: $(this).serialize(),
       dataType: 'json',
       context: this
  })
  .done(function() {
       $(this).next('div').text('success!').removeClass('error loading');
  })
  .fail(function(jqXHR) {
       $(this).next('div')
           .text($.parseJSON(jqXHR.responseText).error)
           .addClass('error').removeClass('loading');
  });
  $(this).next('div').addClass('loading').removeClass('error');
});
