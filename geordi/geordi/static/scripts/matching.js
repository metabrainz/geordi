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

$('form.match-form input').bind('change keyup input propertychange', function(event) {
    var $this = $(this);
    var mbids = $this.val().match(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/);
    if (mbids !== null) {
        $this.val(mbids.join(', '))
    }
});
