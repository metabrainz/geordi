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

function get_mbid_type(mbid) {
    return $.ajax({
        type: "GET",
        url: '/internal/mbidtype/' + mbid,
        dataType: 'json'
    })
}

// AJAX form submission
$('form.match-form').submit(function (e) {
  $(this).siblings('div.response').addClass('loading').removeClass('error');

  e.preventDefault();

  var promise = $.ajax({
       type: "GET",
       url: $(this).attr('action'),
       data: $(this).serialize(),
       dataType: 'json',
       context: this
  });

  promise.done(function() {
       $(this).siblings('div.response').text('Successfully matched. Please refresh the page to see this change.').removeClass('error loading');
  })
  .fail(function(jqXHR) {
       $(this).siblings('div.response')
           .text('Error matching: ' + $.parseJSON(jqXHR.responseText).error)
           .addClass('error').removeClass('loading');
  });
});

$('form.unmatch-form').submit(function (e) {
  $(this).parent('div').siblings('div.response').addClass('loading').removeClass('error');

  e.preventDefault();

  var promise = $.ajax({
       type: "GET",
       url: $(this).attr('action'),
       data: $(this).serialize(),
       dataType: 'json',
       context: this
  });

  promise.done(function() {
       $(this).parent('div').siblings('div.response').text('Successfully unmatched. Please refresh the page to see this change.').removeClass('error loading');
  })
  .fail(function(jqXHR) {
       $(this).parent('div').siblings('div.response')
           .text('Error unmatching: ' + $.parseJSON(jqXHR.responseText).error)
           .addClass('error').removeClass('loading');
  });
});

$('form.match-form textarea').bind('change keyup input propertychange', function(event) {
    var $this = $(this);
    if ($this.data('content') == $this.val()) { return }

    var matches = $this.val().match(/^(.*?),?\s*([^,]*)$/);

    var rewrite = null;
    var lastmbid = matches[2].match(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/);
    var last = false;
    if (lastmbid === null) {
        rewrite = matches[2];
    } else {
        rewrite = lastmbid;
        last = true;
    }

    var mbids = matches[1].match(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/g);
    if (mbids !== null) {
        rewrite = mbids.join(', ') + ', ' + rewrite;
    }

    var type = null;
    var types = [];
    var error = [];
    if (mbids !== null || last) {
        $this.parent('form').siblings('div.response').addClass('loading').removeClass('error');

        var all_mbids = [];
        if (mbids !== null) {
            $.each(mbids, function(idx, elem) {
                all_mbids.push(elem);
            });
        }
        if (last) {
            all_mbids.push(lastmbid);
        }
        $.each(all_mbids, function(index, elem) {
            get_mbid_type(elem).done(function(data) {
                types.push([elem, data.type]);
                if (type === null) {
                    type = data.type;
                } else if (type !== data.type) {
                    error.push([elem, data.type]);
                }
            }).fail(function() {
                types.push([elem, null]);
                error.push([elem, null]);
            });
        });

        set_when_done = function () {
            if (types.length != all_mbids.length) {
                 window.setTimeout(set_when_done, 200)
            } else if (error.length == 0 && type !== null) {
                 $this.siblings('input[name="type"]').val(type);
                 $this.siblings('span.match-type').text(type).removeClass('artist label release release-group work recording').addClass(type);
                 $this.parent('form').siblings('div.response').removeClass('error loading').text('')
                 $this.siblings('input[type="submit"]').removeAttr('disabled');
            } else {
                 var text;
                 if (type === null) {
                     text = 'Could not find an entity type'
                 } else {
                     text = 'Not all MBIDs are entities of the same type';
                 }
                 $this.parent('form').siblings('div.response').addClass('error').removeClass('loading').text('Error: ' + text)
            }
        }
        window.setTimeout(set_when_done, 200);
    }

    if (rewrite) {
        $this.val(rewrite)
        $this.data('content', rewrite);
    }
});
