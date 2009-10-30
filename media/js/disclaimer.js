function hideDisclaimer() {
      var d = document.getElementById('disclaimer');
      d.style.display = 'none';
      setCookie('disclaimerviewed','true');
          document.getElementById('alloffenses').style.display='block';
          document.getElementById('cckc_disclaimer').style.display='block';
}

function showDisclaimer() {
      var c = getCookie('disclaimerviewed');
      if (c == 'true') {
          // they've already seen the disclaimer
          return
      } else {
          var d = document.getElementById('disclaimer');
          d.style.display = 'block';
          document.getElementById('alloffenses').style.display='none';
          document.getElementById('cckc_disclaimer').style.display='none';
      }
}

addLoadEvent(showDisclaimer);
