"""
Prepares the PATH environment variable.
"""
import os
import sys

root_join = lambda *a: os.path.join(ROOT, *a)

ROOT    = os.path.dirname(os.path.abspath(__file__))
ROOTMOM = os.path.abspath(root_join(ROOT, ".."))

paths = [
    ROOTMOM,
    root_join('apps'),
    root_join('lib'),
    root_join('utils'),
]

print "QQQQQQQQQQQQQQQQ"
print paths
# Reverse the paths so they end up in the same order they're listed
paths.reverse()

for path in paths:
    if os.path.exists(path):
        sys.path.insert(0, path)
    else:
        print "Does not exist:" + path
