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
	//determine if IE is in the mix
	if (e.target){
		var node = e.target;
	}else if (e.srcElement) {
		var node = e.srcElement; 
	}
	//test if the text entered is greater than 2, if so then run the query
	var val = node.value;
	if(val.length > 2){
		var ajax= Xhr_request.createXhrObject();//created from resulting object from xhr.js 
		
		ajax.open("GET","search?q=" + val,true);
		ajax.setRequestHeader("Content-type","application/x-www-form-urlencoded");
		ajax.send(); 
		//create a ready state handler
		ajax.onreadystatechange=function(){
			if (ajax.readyState==4 && ajax.status==200){
			var q = ajax.responseText;
			var list = q.getElementByTag('li');
			console.log(list);
			return ajax.responseText;
    		}
		}
			
	}
}




