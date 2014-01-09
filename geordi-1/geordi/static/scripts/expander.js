function changeRegion($region) {
  $region.children('div.li').add($region.next('dd'))
            [$region.hasClass('closed') ? 'removeClass' : 'addClass']('collapse')
         .end().end()

         .toggleClass('closed open');
}

$('.block-expander span.clicker').click(function(event) {
  event.stopPropagation();
  var $this = $(this).parent('.block-expander');
  changeRegion($this);
  if (event.altKey) {
    $this.children('div.li').add($this.next('dd'))
         .find('.block-expander.' + ($this.hasClass('open') ? 'closed' : 'open'))
         .each(function() { changeRegion($(this)) });
  }
});

$('.subitem-opener').click(function() {
  $this = $(this);
  $li = $('#li-subitem-' + $this.attr('data-subitem'));
  if ($li.hasClass('closed')) {
    var e = jQuery.Event("click");
    e.altKey = true;
    $li.find('span.clicker').trigger(e);
  }
});
