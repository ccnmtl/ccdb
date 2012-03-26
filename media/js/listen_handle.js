/*
* The idea here is to add an event listener to the search field, grab that data and pass it via
* ajax as an object/url variable to the python page and return the results in a UI friendly way
*/

function addEventHandler( node, eventName, eventHandler ){
    var CAPTURING_PHASE = true, BUBBLING_PHASE = false;
    if( node.addEventListener )
    {
        node.addEventListener( eventName, eventHandler, BUBBLING_PHASE );
    }
    else if( node.attachEvent )
    {
        node.attachEvent( 'on' + eventName, eventHandler );
    }
}

function autoComplete(e){
	var dropDiv = document.getElementById('dropdown');
	var pageBody = document.getElementById('pagebody');
	//determine if IE is in the mix
	if (e.target){
		var node = e.target;
	}else if (e.srcElement) {
		var node = e.srcElement; 
	}
	//test if the text entered is greater than 2, if so then run the query
	var val = node.value;
		var ajax= Xhr_request.createXhrObject();//created from resulting object from xhr.js 
		ajax.open("GET","/autocomplete?q=" + val,true);
		ajax.setRequestHeader("Content-type","application/x-www-form-urlencoded");
		ajax.send(); 
		//create a ready state handler
		ajax.onreadystatechange=function(){
			if (ajax.readyState==4 && ajax.status==200){
				var q = ajax.responseText;
				var evaluate = new Function(q);
				evaluate();
				console.log(searchTags);
				jQuery("#offense_text").autocomplete({
					source: searchTags
				});
    		}
		}//end ajax ready state
}




