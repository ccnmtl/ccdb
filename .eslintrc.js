module.exports = {
    "env": {
        "browser": true,
        "jquery": true
    },
    "extends": "eslint:recommended",
    "globals": {
        "accesstab": true,
        "addElementClass": true,
        "addLoadEvent": true,
        "evalJSON": true,
        "excerpt": true,
        "forEach": true,
        "getCookie": true,
        "getElementsByTagAndClassName": true,
        "hasElementClass": true,
        "hideElement": true,
        "log": true,
        "removeElementClass": true,
        "serializeJSON": true,
        "setCookie": true,
        "showElement": true,
    },
    "rules": {
        "indent": [
            "error",
            4
        ],
        "linebreak-style": [
            "error",
            "unix"
        ],
        "no-unused-vars": [
            "error",
            {"vars": "all", "args": "none"}
        ],
        "quotes": [
            "error",
            "single"
        ],
        "semi": [
            "error",
            "always"
        ]
    }
};
