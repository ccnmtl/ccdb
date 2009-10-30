/* ------- This one is for the two tabs ---- */

function splitanchor(a) {
	var boxtoshow = a.href.split("#")[1];
	var box_list = new Array ();
	box_list[0] = document.getElementById('comparelist');
	box_list[1] = document.getElementById('newsearchlist');
	for (i=0; i< 2; i++) {
		box_list[i].style.display = "none";
		if (box_list[i].id == boxtoshow) {
		  document.getElementById('comparelisttab').className = "tabs";
		  document.getElementById('newsearchlisttab').className = "tabs";
		  document.getElementById(boxtoshow+'tab').className = "tabs activetab";
		  box_list[i].style.display = "block";
		}

	}

	if (boxtoshow == 'newsearchlist') {
		showElement('startoveralert');
		hideElement('resultscontentbox');
	}
	if (boxtoshow == 'comparelist') {
		showElement('resultscontentbox');
		hideElement('startoveralert');
	}

}

function initAnchor() {
  var compare = $('comparelink');
  if(compare) {
    splitanchor(compare);
  }
}

addLoadEvent(initAnchor)
