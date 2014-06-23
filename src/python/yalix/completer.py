#!/usr/bin/env python
# -*- coding: utf-8 -*-

from yalix.interpreter.builtins import __special_forms__


class Completer:
    def __init__(self, env):
        """Create a new completer for the command line."""
        self.env = env

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        This is called successively with state == 0, 1, 2, ... until it
        returns None.  The completion should begin with 'text'.
        """

        if state == 0:
            self.matches = self.global_matches(text)
        try:
            return self.matches[state]
        except IndexError:
            return None

    def global_matches(self, text):
        """Compute matches when text is a simple name.

        Return a list of all keywords, built-in functions and names currently
        defined in self.namespace that match.

        """
        matches = []
        n = len(text)
        for word, _ in list(self.env.items()):
            if word[:n] == text:
                matches.append(word)

        for word in __special_forms__:
            if word[:n] == text:
                matches.append(word)

        return matches
