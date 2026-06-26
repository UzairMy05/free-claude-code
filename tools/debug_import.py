import importlib, traceback, sys, pathlib

# Ensure repository root is on sys.path so imports match pytest environment.
repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

try:
    m = importlib.import_module('messaging.trees')
    print('IMPORT_OK')
    print('attrs:', [a for a in dir(m) if not a.startswith('_')])
except Exception:
    traceback.print_exc()
