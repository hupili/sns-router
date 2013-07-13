$(function(){
	$('.message_body').map(function(){
		// Extract and truncate link
		$(this).html($(this).html().replace(/https?:\/\/[a-z0-9:\/%\.\-&?=_;~]+/i, function(link){ 
			if (r = /(https?:\/\/([a-z0-9:%\.\-]+)\/[a-z0-9:\/%\.\-&?=_;~]+)/i.exec(link)){
			//if (r=/http:\/\/[a-z0-9:\/%\.\-]+[^a-z0-9:\/%\.\-]/.exec(link)){
				return '<a target="_blank" class="truncated_link" href="' + r[1] 
						+ '" title="' + r[1] 
						+ '" short_href="' + r[2] 
						+'">' + r[2] + '...</a>';
			} else {
				return link;
			}
		}));

		// Collapse long texts
		$(this).css('text-overflow', 'ellipsis');
		$(this).css('line-height', '1.5em');
		//$(this).css('white-space', 'nowrap');
		$(this).css('overflow', 'hidden');
		// Analyze min height
		var _current_h = $(this).css('height').replace('px', '');
		$(this).css('height', '4.5em');
		var _expect_h = $(this).css('height').replace('px', '');
		var _min_h = 0; 
		if (parseInt(_current_h) < parseInt(_expect_h)){
			_min_h = _current_h + 'px';
		} else {
			_min_h = _expect_h + 'px';
		}
		//alert(_min_h + "," + _expect_h + "," + _current_h);
		$(this).attr('_expand', 'false');
		$(this).attr('_min_h', _min_h);
		$(this).css('height', _min_h);
		$(this).css('background', '#f0f0f0');
		$(this).click(function () {
			if ($(this).attr('_expand') == 'false') {
				$(this).attr('_expand', 'true');
				$(this).css('height', 'auto');
				$(this).css('background', '#ffffff');
			} else {
				$(this).attr('_expand', 'false');
				$(this).css('height', $(this).attr('_min_h'));
				$(this).css('background', '#f0f0f0');
			}
		});
	});
	
	// mouse over to expand the link. canceled function
	//$('.truncated_link').map(function(){
	//	$(this).mouseover(function(){
	//		$(this).html($(this).attr('href'));	
	//	});
	//	$(this).mouseout(function(){
	//		$(this).html($(this).attr('short_href'));	
	//	});
	//});
})
