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

$('#id-type').change(function() {
  var $this = $(this);
    if ($this.val() == 'raw') {
      if ($('#id-query').get(0).tagName == 'input') {
          var query = '{"query":\n  {"bool":\n    {"must": [{"query_string": {"query": "' + $('#id-query').val() + '"}}]}\n  }\n }';
      } else {
          var subitem_type = $('#id-subitem_type').val();
          var subitem_key = geordi.link_types[$('#id-subitem_index').val()][subitem_type]['key'];
          var query = '{"query":\n  {"match":\n   {"_geordi.links.links.' + subitem_type + '.' + subitem_key + '": "' + $('#id-query input').val() + '"}\n  }\n}';
      }
      $('#id-query').replaceWith('<textarea name="query" style="width: 60em" id="id-query" placeholder="Query" cols=60 rows=8>' + query + '</textarea>');
    } else if ($this.val() == 'item') {
      if ($('#id-query').get(0).tagName == 'textarea') {
        var jsonquery = $.parseJSON($('#id-query').val());
        var query = jsonquery.query.bool.must[0].query_string ? jsonquery.query.bool.must[0].query_string.query : '';
      } else { var query = '' }
      $('#id-query').replaceWith('<input type="text" style="width: 60em" name="query" id="id-query" placeholder="Query" value="' + query + '" />');
    } else if ($this.val() == 'subitem') {
      $('#id-query').replaceWith('<div id="id-query" style="display: inline-block;">' +
        '<input type="text" name="query" placeholder="ID" style="width: 20em" />' +
        '<select id="id-subitem_type" name="subitem_type" style="width: 20em">' +
        '</select>' +
        geordi.index_options_html +
        '</div>');
      add_subitem_type_listener();
      $('#id-subitem_index').change();
    }
});
