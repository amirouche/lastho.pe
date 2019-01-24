let ReactDOM = helpers.default.ReactDOM;
let h = helpers.default.h;
let Input = helpers.default.Input;


var container = document.getElementById('container');

let get = function(path, body, token) {
    let request = new Request(path);
    if (token) {
        request.headers.set('X-AUTH-TOKEN', token)
    }
    return fetch(request);
}

let post = function(path, body, token) {
    let request = new Request(path, {method: 'POST', body: JSON.stringify(body)});
    if (token) {
        request.headers.set('X-AUTH-TOKEN', token);
    }
    return fetch(request, {headers: {'Content-Type': 'application/json'}});
}

var recv = function(json) {
    console.debug(json);
    if (json.type === 'ajax') {  // XXX: race condition
        if (json.method === 'get') {
            get(json.path, json.body, json.token).then(function(response) {
                response.json().then(function(body) {
s                    send(json.key, {event: {target: {value: {status: response.status, body: body}}}});
                });
            });
        } else if (json.method === 'post') {

        }
    } else if (json.type == 'dom') {
        ReactDOM.render(
            translate(json),
            container,
        );
    } else {
        console.log('recv: unknown type', json.type);
    }
}

var send = function(key, event) {
    if (event.preventDefault) {
        event.preventDefault();
    }
    var msg = {
        path: location.pathname,
        key: key,
        event: {'target.value': event.target.value},
    };

    pypyjs.eval('recv(' + JSON.stringify(msg) + ')')
          .then(recv)
          .then(null, console.error);
}

let makeCallback = function(identifier) {
    return function(event) {
        return send(identifier, event);
    };
}

/* Translate json to `vnode` using `h` helper */
var translate = function(json) {
    for (let key in json.attributes) {
        if(key.startsWith('on')) {
            json.attributes[key] = makeCallback(json.attributes[key]);
        }
    }

    // recurse to translate children
    var children = json.children.map(function(child) {  // TODO: optimize with a for-loop
        if (child instanceof Object) {
            return translate(child);
        } else { // it's a string or a number
            return child;
        }
    });

    // XXX: HACK
    if (json.tag === 'input') {
        json.tag = Input;
    }

    return h(json.tag, json.attributes, children);
}


pypyjs.ready().then(function() {
    fetch('/static/main.py').then(function(xhr) {
        xhr.text()
           .then(function(main) {
               pypyjs.exec(main)
                     .then(function() {
                         console.log('main.py loaded')
                         pypyjs.eval('_render()')
                                .then(null, console.error)
                                .then(recv);
                      })
                      .then(null, console.error);
            });
    });
});
