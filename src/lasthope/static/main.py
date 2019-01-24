from types import GeneratorType
from uuid import uuid4

# framework-ish stuff

class BeyondException(Exception):
    pass


def generate_unique_key(dictionary):
    key = uuid4().hex
    if key not in dictionary:
        return key
    raise BeyondException('Seems like the dictionary is full')


class Node(object):  # inspired from nevow
    """Python representaiton of html nodes.

    Text nodes are python strings.

    You must not instantiate this class directly. Instead use the
    global instance `h` of the `PythonHTML` class.

    """

    __slots__ = ('_tag', '_children', '_attributes')

    def __init__(self, tag):
        self._tag = tag
        self._children = list()
        self._attributes = dict()

    def __call__(self, **kwargs):
        """Update node's attributes"""
        self._attributes.update(kwargs)
        return self

    def __repr__(self):
        return '<Node: %s %s>' % (self._tag, self._attributes)

    def append(self, node):
        """Append a single node or string as a child"""
        self._children.append(node)

    def extend(self, nodes):
        [self.append(node) for node in nodes]

    def __getitem__(self, nodes):
        """Add nodes as children"""
        # XXX: __getitem__ is implemented in terms of `Node.append`
        # so that widgets can simply inherit from node and override
        # self.append with the bound `Node.append`.
        if isinstance(nodes, (str, float, int)):
            self.append(nodes)
        elif isinstance(nodes, (list, tuple)):
            [self.append(node) for node in nodes]
        else:
            self.append(nodes)
        return self


def serialize(node):
    """Convert a `Node` hierarchy to a json string.

    Returns two values:

    - the dict representation
    - an event dictionary mapping event keys to callbacks

    """

    events = dict()

    def to_html_events(attributes):
        """Filter attributes referencing callbacks"""
        for key, value in attributes.items():
            if key.startswith('on'):
                yield key, value

    def to_dict(node):
        """Recursively convert `node` into a dictionary"""
        if isinstance(node, (str, float, int)):
            return node
        else:
            out = dict(tag=node._tag)
            out['attributes'] = dict(node._attributes)
            for event_name, callback in to_html_events(node._attributes):
                key = generate_unique_key(events)
                events[key] = callback  # XXX: side effect!
                out['attributes'][event_name] = key
            # recurse center
            out['children'] = [to_dict(child) for child in node._children]
            return out

    return to_dict(node), events


class PythonHTML(object):
    """Sugar syntax for creating `Node` instance.

    E.g.

    h.div(id="container", className="minimal thing", For="something")["Héllo World!"]

    container = h.div(id="container", className="minimal thing")
    container.append("Héllo World!")

    """

    # # XXX: Not sure it's useful
    # def form(self, **kwargs):
    #     """form element that prevents default 'submit' behavior"""
    #     node = Node('form')
    #     node._attributes['onSubmit'] = 'return false;'
    #     node._attributes.update(**kwargs)
    #     return node

    # XXX: Not sure it's useful
    # def input(self, **kwargs):
    #     type = kwargs.get('type')
    #     if type == 'text':
    #         try:
    #             kwargs['id']
    #         except KeyError:
    #             pass
    #         else:
    #             log.warning("id attribute on text input node ignored")
    #         node = Node('input#' + uuid4().hex)
    #     else:
    #         node = Node('input')
    #     node._attributes.update(**kwargs)
    #     return node

    def __getattr__(self, attribute_name):
        return Node(attribute_name)


h = PythonHTML()


events = dict()


def get(path, token=None):
    return {
        'type': 'ajax',
        'method': 'get',
        'path': path,
        'token': token,
    }


def post(path, body=None, token=None):
    return {
        'type': 'ajax',
        'method': 'post',
        'path': path,
        'body': body,
        'token': token,
    }


def recv(event):
    # XXX: what happens if the same event is fired multiple
    # times
    callback = events[event['key']]
    # callback is a running generator
    if isinstance(callback, GeneratorType):
        raise Exception()
        try:
            request = generator.send(event)
        except StopIteration:
            return _render()
        else:
            key = generate_unique_key(events)
            events[key] = generator
            request['key'] = key
            return request

    # otherwise
    maybe_generator = callback(event)
    if isinstance(maybe_generator, GeneratorType):  # async callback
        generator = maybe_generator
        request = next(generator)
        key = generate_unique_key(events)
        events[key] = generator
        request['key'] = key
        return request

    out = _render()
    return out


def _render():
    html, new = serialize(render())
    events.update(new)  # XXX: leak
    html['type'] = 'dom'
    return html


# application code


class STATUS:
    DONE = 'done'
    WIP = 'wip'
    ALL = 'all'


class Todo:

    def __init__(self, value):
        self.value = value
        self.status = STATUS.WIP


model = dict(
    todo='',
    filter=STATUS.ALL,
    todos=[Todo('Learn Python')]
)


def on_value_change(event):
    value = event['event']['target.value']
    model['todo'] = value


def on_submit(event):
    out = yield get('/api/status')
    model['todos'].append(Todo(model['todo']))
    model['todo'] = ''


def on_done(todo):
    def on_event(_):
        todo.status = STATUS.DONE
    return on_event


def on_filter(value):
    def on_event(_):
        model['filter'] = value
    return on_event


def filter_button(value):
    if model['filter'] == value:
        return h.input(className='active', type='submit', value=value)
    else:
        return h.input(className='inactive', type='submit', value=value, onClick=on_filter(value))


def render():
    root = h.div(id='root')
    root.append(h.h1()["todos"])
    done = len(filter(lambda x: x.status == 'done', model['todos']))
    count = float(len(model['todos']))
    percent = (done / count) * 100
    msg = "{:.2f}% complete!".format(percent)
    root.append(h.h2()[msg])
    filters = h.div(id='filters')
    filters.append(filter_button('all'))
    filters.append(filter_button('wip'))
    filters.append(filter_button('done'))
    root.append(filters)
    form = h.form(onSubmit=on_submit)
    form.append(h.input(type='text', onChange=on_value_change, value=model['todo']))
    root.append(form)
    if model['filter'] == STATUS.ALL:
        for todo in model['todos']:
            item = h.div(className='item ' + todo.status)
            item.append(h.span()[todo.value])
            item.append(h.input(type='submit', value='done', onClick=on_done(todo)))
            root.append(item)
    else:
        for todo in model['todos']:
            if todo.status == model['filter']:
                item = h.div(className='item ' + todo.status)
                item.append(h.span()[todo.value])
                item.append(h.input(type='submit', value='done', onClick=on_done(todo)))
                root.append(item)
    return root
