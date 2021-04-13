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
    def __init__(self, _globals, parent_class, object_class_prefix, *args):
        """Constructor for class ObjectPool.

        Fills a pool with a single instance of every subclass of
        given parent class from given global context. The dictionary
        key/object id for an object is the objects class name without
        the given prefix in lowercase."""

        self._pool = dict()

        for key in _globals:
            # Skip non classes and state parent.
            if not isinstance(_globals[key], type) or _globals[key] == parent_class:
                continue

            if issubclass(_globals[key], parent_class):
                state_id = key
                if state_id.startswith(object_class_prefix):
                    # Cut prefix off.
                    state_id = state_id[len(object_class_prefix):]

                state_id = state_id.lower()
                if state_id in self._pool:
                    raise Exception('[OBJECT POOL] Multiple objects have the same name...')

                # Add instance of state to pool.
                self._pool[state_id] = _globals[key](*args)

    def object_exists(self, object_id: str):
        """Checks if an object ID exists in the pool.

        Args:
          object_id: ID to check for.

        Returns:
          Bool of whether the object ID is in the pool.
        """

        return object_id in self._pool

    def get_object(self, object_id: str):
        """Retrieves an object from the pool by its ID.

        Args:
          object_id: ID of the object to retrieve from the pool.

        Returns:
          The object reference from the object pool.
        """

        if not self.object_exists(object_id):
            raise Exception(f'[OBJECT POOL] Tried to get non existing object: {object_id}')
        return self._pool[object_id]
