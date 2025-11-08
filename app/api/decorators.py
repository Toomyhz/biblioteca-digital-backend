from functools import wraps
from flask_restx import abort
from flask import current_app

def rest_endpoint(ns, input_model=None, output_model=None, code=200):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                raise e

        if input_model:
            wrapper = ns.expect(input_model, validate=True)(wrapper)
        if output_model:
            wrapper = ns.marshal_with(output_model, code=code)(wrapper)
        return wrapper
    return decorator


