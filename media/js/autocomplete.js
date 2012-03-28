//the key listener
var searchField = jQuery('#offense_text');
searchField.bind('keyup', autoComplete);

//the event handler
function autoComplete(e){
	//determine if IE is in the mix
	if (e.target){
		var node = e.target;
	}else if (e.srcElement) {
		var node = e.srcElement;
	}
	var val = node.value;
	var jqxhr = jQuery.ajax({
		type: "GET",
		url: "/autocomplete/?q=" + val,
		datatype: "JSON"
    })
    .success(function() {
    	var searchTags = jQuery.parseJSON(jqxhr.responseText);
    	jQuery("#offense_text").autocomplete({
			source: searchTags,
			minLength: 3
		});
    })
    .error(function() { })
    .complete(function() { })
}




