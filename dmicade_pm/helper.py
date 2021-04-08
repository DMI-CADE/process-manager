class DmicEvent:

    def __init__(self):
        self._subs = []

    def __iadd__(self, sub):
        self._subs.append(sub)
        return self

    def update(self, event_args=None):
        for sub in self._subs:
            sub(event_args)


class ObjectPool:
    def __init__(self):
        self._pool = None

    def fill_object_pool(self, _globals, parent_class, object_class_prefix, *args):
        """Returns filled object pool.

        Fills a pool with a single instance of every subclass of
        given parent class from given global context. The dictionary key
        for an object is the objects class name without the given prefix in
        lowercase."""

        object_pool = dict()
        print(f'make object pool:\n{_globals}\n{parent_class}\n{object_class_prefix}\n{args}')

        for key in _globals:
            print(key)
            # Skip non classes and state parent.
            print(not isinstance(_globals[key], type), _globals[key] == parent_class)
            if not isinstance(_globals[key], type) or _globals[key] == parent_class:
                continue

            print(issubclass(_globals[key], parent_class))
            if issubclass(_globals[key], parent_class):
                state_id = key
                if state_id.startswith(object_class_prefix):
                    # Cut prefix off.
                    state_id = state_id[len(object_class_prefix):]

                state_id = state_id.lower()
                print(state_id)

                # Add instance of state to pool.
                object_pool[state_id] = _globals[key](*args)

        self._pool = object_pool

    def object_exists(self, object_id):
        return object_id in self._pool

    def get_object(self, object_id):
        if not self.object_exists(object_id):
            raise Exception(f'[OBJECT POOL] Tried to get non existing object: {object_id}')
        return self._pool[object_id]
