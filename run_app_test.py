import importlib, traceback
try:
    m = importlib.import_module('app.main')
    app = m.create_app()
    print('APP_CREATED')
except Exception:
    traceback.print_exc()
    print('APP_CREATE_FAILED')
