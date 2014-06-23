#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Env(object):

    def __init__(self, local_stack=None, global_frame=None):
        self.local_stack = local_stack if local_stack else []
        self.global_frame = global_frame if global_frame else {}

    def extend(self, name, value):
        """
        Extend the local stack with the given name/value.
        Note 2: global frame is shared across extended environments.
        """
        new_stack = list(self.local_stack)
        new_stack.append((name, value))
        return Env(local_stack=new_stack, global_frame=self.global_frame)

    def set_local(self, name, value):
        """
        Traverses the local stack and sets the first instance of name with value
        """
        stack = self.local_stack
        for i in range(1, len(stack) + 1):
            if self.local_stack[-i][0] == name:
                self.local_stack[-i] = (name, value)
                return

        raise KeyError('Assignment disallowed: \'{0}\' is unbound in local environment'.format(name))

    def __setitem__(self, name, value):
        """
        Adds a new global definition, and evaluates it according to self
        """
        # TODO: not sure this is the right place -> should be pushed out to callers
        self.global_frame[name] = value.eval(self)

    def __getitem__(self, name):
        """
        Look in the local stack first for the named item, then try the global frame
        """
        stack = self.local_stack
        while stack:
            peek = stack[-1]
            if peek[0] == name:
                return peek[1]
            else:
                stack = stack[:-1]

        if name not in self.global_frame:
            raise KeyError('\'{0}\' is unbound in environment'.format(name))

        return self.global_frame[name]

    def items(self):
        return self.global_frame.items()
