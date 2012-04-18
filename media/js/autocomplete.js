
jQuery("#offense_text").autocomplete({
	source: "/autocomplete/",
	minLength: 3
});

if (document.getElementById('compare_auto_complete') !== null){ 
    var charges = jQuery('.compare');
    var list = jQuery('#list');
    var compare = jQuery('#compare_btn input') 
    charges.each(function(){
        var option = jQuery(this).text();
        var val = jQuery(this).attr('href');
        list.append('<option value="'+ val +'">' + option + '</option>');
    })
    
    compare.click(function(){
        var compare_val = jQuery('#list').val();        
        window.location = compare_val;
    })
    
}
