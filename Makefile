APP=ccdb
JS_FILES=media/js/autocomplete.js media/js/hs.js media/js/disclaimer.js media/js/splitanchor.js
MAX_COMPLEXITY=6

all: eslint jenkins

include *.mk

eslint: $(JS_SENTINAL)
	$(NODE_MODULES)/.bin/eslint $(JS_FILES)

.PHONY: eslint
