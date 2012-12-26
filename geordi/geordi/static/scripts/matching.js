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
  e.preventDefault();
  var promise = $.ajax({
       type: "GET",
       url: $(this).attr('action'),
       data: $(this).serialize(),
       dataType: 'json',
       context: this
  });

  $(this).next('div').addClass('loading').removeClass('error');

  promise.done(function() {
       $(this).next('div').text('Successfully matched. Please refresh the page to see this change.').removeClass('error loading');
  })
  .fail(function(jqXHR) {
       $(this).next('div')
           .text('Error matching: ' + $.parseJSON(jqXHR.responseText).error)
           .addClass('error').removeClass('loading');
  });
});

$('form.match-form textarea').bind('change keyup input propertychange', function(event) {
    var $this = $(this);
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
                 $this.siblings('select').val(type);
            }
        }
        window.setTimeout(set_when_done, 200);
    }

    if (rewrite) {
        $this.val(rewrite)
    }
});
