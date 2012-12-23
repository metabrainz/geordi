function add_subitem_type_listener() {
  $('#id-subitem_index').change(function () {
    var new_html = '';
    $.each(geordi.subtype_options[$(this).val()], function(idx, option) {
      new_html = new_html + '<option value="' + option[0] + '">' + option[1] + '</option>'
    });
    $('#id-subitem_type').html(new_html);
  });
}
add_subitem_type_listener()

function raw_query(type, query) {
    return '<textarea name="query" data-searchtype="' + type + '" style="width: 60em" id="id-query" placeholder="Query" cols=60 rows=8>' + query + '</textarea>'
}
function text_query(type, query) {
   return '<input type="text" data-searchtype="' + type + '" style="width: 60em" name="query" id="id-query" placeholder="Query" value="' + query + '" />'
}

$('#id-type').change(function() {
  var $this = $(this);
  var $query = $('#id-query');
    if ($this.val() == 'raw') {
      if ($query.attr('data-searchtype') == 'item') {
          var query = '{"query":\n  {"query_string": {"query": "' + $('#id-query').val() + '"}}\n}';
      } else if ($query.attr('data-searchtype') == 'sub') {
          var subitem_type = $('#id-subitem_type').val();
          var subitem_key = geordi.link_types[$('#id-subitem_index').val()][subitem_type]['key'];
          var query = '{"query":\n  {"match":\n   {"_geordi.links.links.' + subitem_type + '.' + subitem_key + '": "' + $('#id-query input').val() + '"}\n  }\n}';
      } else if ($query.attr('data-searchtype') == 'raw-subitem') {
          var query = $('#id-query').val();
      } else {
          var query = '{"query":\n  {}\n}';
      }
      $('#id-query').replaceWith(raw_query('raw', query));
    }

    else if ($this.val() == 'item') {
      if ($query.attr('data-searchtype') == 'raw') {
          var jsonquery = $.parseJSON($('#id-query').val());
          var query = jsonquery.query.query_string ? jsonquery.query.query_string.query : '';
      } else if ($query.attr('data-searchtype') == 'subitem') {
          var query = $('#id-query').val();
      } else {
          var query = ''
      }
      $('#id-query').replaceWith(text_query('item', query));
    }

    else if ($this.val() == 'sub') {
      $('#id-query').replaceWith('<div id="id-query" data-searchtype="sub" style="display: inline-block;">' +
        '<input type="text" name="query" placeholder="ID" style="width: 20em" />' +
        '<select id="id-subitem_type" name="subitem_type" style="width: 20em">' +
        '</select>' +
        geordi.index_options_html +
        '</div>');
      add_subitem_type_listener();
      $('#id-subitem_index').change();
    }

    else if ($this.val() == 'subitem') {
      if ($query.attr('data-searchtype') == 'raw-subitem') {
          var jsonquery = $.parseJSON($('#id-query').val());
          var query = jsonquery.query.query_string ? jsonquery.query.query_string.query : '';
      } else if ($query.attr('data-searchtype') == 'item') {
          var query = $('#id-query').val();
      } else {
          var query = ''
      }
      $('#id-query').replaceWith(text_query('subitem', query));
    }

    else if ($this.val() == 'raw-subitem') {
      if ($query.attr('data-searchtype') == 'subitem') {
          var query = '{"query":\n  {"query_string": {"query": "' + $('#id-query').val() + '"}}\n}';
      } else if ($query.attr('data-searchtype') == 'raw') {
          var query = $('#id-query').val();
      } else {
          var query = '{"query":\n  {}\n}';
      }
      $('#id-query').replaceWith(raw_query('raw-subitem', query));
    }
});
