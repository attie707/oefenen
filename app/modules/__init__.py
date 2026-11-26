"""All learning modules. Add a new subject by creating a package here and listing it in ORDER."""
import importlib

ORDER = ["frans", "nederlands", "topografie"]
MODULES = {k: importlib.import_module(f"modules.{k}") for k in ORDER}
