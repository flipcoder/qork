python -m cProfile -o qork.pyprof qork.py "$@"
pyprof2calltree -i qork.pyprof -k
