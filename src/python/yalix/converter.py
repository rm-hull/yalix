#!/usr/bin/env python
# -*- coding: utf-8 -*-

def linked_list_to_array(t):
    arr = []
    while t:
        arr.append(t[0])
        t = t[1]
    return arr

def array_to_linked_list(arr):
    t = None
    while arr:
        t = (arr[-1], t)
        arr = arr[:-1]
    return t


# x = (1, (2, (3, (4, (5, None)))))
# linked_list_to_array(x)
# x

# y = [1,2,3,4,5]
# array_to_linked_list(y)
# y