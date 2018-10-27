APP=ccdb
JS_FILES=media/js/autocomplete.js media/js/hs.js media/js/disclaimer.js media/js/splitanchor.js
MAX_COMPLEXITY=6
FLAKE8_IGNORE=W605

all: jenkins

include *.mk
