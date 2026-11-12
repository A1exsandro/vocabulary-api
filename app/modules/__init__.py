"""Feature modules.

Keep this package initializer free of imports. The router aggregation lives in
``app.modules.router``, so that importing a model does not import the routers.
That import chain caused a circular import with the use cases.
"""
