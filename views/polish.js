$(function(){
	$('.message_body').map(function(){
		//$(this).html($(this).html().replace(/http:\/\/[a-z0-9:\/%\.\-]+[^a-z0-9:\/%\.\-]/i, function(link){ 
		//	if (r = /(http:\/\/([a-z0-9:%\.\-]+)\/[a-z0-9:\/%\.\-]+)([^a-z0-9:\/%\.\-])/i.exec(link)){
		//	//if (r=/http:\/\/[a-z0-9:\/%\.\-]+[^a-z0-9:\/%\.\-]/.exec(link)){
		$(this).html($(this).html().replace(/http:\/\/[a-z0-9:\/%\.\-&?=]+/i, function(link){ 
			if (r = /(http:\/\/([a-z0-9:%\.\-]+)\/[a-z0-9:\/%\.\-&?=]+)/i.exec(link)){
			//if (r=/http:\/\/[a-z0-9:\/%\.\-]+[^a-z0-9:\/%\.\-]/.exec(link)){
				return '<a class="truncated_link" href="' + r[1] 
						+ '" title="' + r[1] 
						+ '" short_href="' + r[2] 
						+'">' + r[2] + '...</a>';
			} else {
				return link;
			}
		}));
	});
	$('.truncated_link').map(function(){
		$(this).mouseover(function(){
			$(this).html($(this).attr('href'));	
		});
		$(this).mouseout(function(){
			$(this).html($(this).attr('short_href'));	
		});
	});
})
