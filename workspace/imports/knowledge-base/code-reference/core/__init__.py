# ==== Auto-fixed: lazy imports ====
import importlib

def __getattr__(name):
    try:
        return importlib.import_module("." + name, __package__)
    except:
        return None
