"""Request compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Union

from preacher.core.request import Request
from .error import CompilationError


_KEY_PATH = 'path'
_KEY_PARAMS = 'params'


class RequestCompiler:
    """
    When given not a string path, then raises a compiration error.
    >>> RequestCompiler({'path': {'key': 'value'}})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Request.path ...: path
    >>> compiler = RequestCompiler()
    >>> compiler.compile({'path': {'key': 'value'}})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Request.path ...: path

    When given not a mapping parameters, then raises a compilation error.
    >>> RequestCompiler({'params': ''})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Request.params ...: params
    >>> compiler = RequestCompiler()
    >>> compiler.compile({'params': ''})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Request.params ...: params

    When given an empty mapping, then returns the dafault mapping..
    >>> compiler = RequestCompiler()
    >>> request = compiler.compile({})
    >>> request.path
    ''
    >>> request.params
    {}

    When given a string, then returns a request of the path.
    >>> compiler = RequestCompiler('/default-path')
    >>> request = compiler.compile({})
    >>> request.path
    '/default-path'
    >>> request.params
    {}
    >>> request = compiler.compile('/path')
    >>> request.path
    '/path'
    >>> request.params
    {}

    When given a filled mapping, then returns the request of it.
    >>> compiler = RequestCompiler(
    ...     defaults={'path': '/default-path', 'params': {'foo': 'bar'}},
    ... )
    >>> request = compiler.compile({})
    >>> request.path
    '/default-path'
    >>> request.params
    {'foo': 'bar'}
    >>> request = compiler.compile('/path')
    >>> request.path
    '/path'
    >>> request.params
    {'foo': 'bar'}
    >>> request = compiler.compile(
    ...     {'path': '/path', 'params': {'key': 'value'}}
    ... )
    >>> request.path
    '/path'
    >>> request.params
    {'key': 'value'}
    """
    def __init__(
        self: RequestCompiler,
        defaults: Union[Mapping, str, None] = None,
    ) -> None:
        self._default_path: str = ''
        self._default_params: Mapping = {}

        if defaults:
            self.set_defaults(defaults)

    def set_defaults(
        self: RequestCompiler,
        defaults: Union[Mapping, str],
    ) -> None:
        default_request = RequestCompiler().compile(defaults)
        self._default_path = default_request.path
        self._default_params = default_request.params

    def compile(self: RequestCompiler, obj: Union[Mapping, str]) -> Request:
        if isinstance(obj, str):
            return self.compile({_KEY_PATH: obj})

        path = obj.get(_KEY_PATH, self._default_path)
        if not isinstance(path, str):
            raise CompilationError(
                message=f'Request.{_KEY_PATH} must be a string',
                path=[_KEY_PATH],
            )

        params = obj.get(_KEY_PARAMS, self._default_params)
        if not isinstance(params, Mapping):
            raise CompilationError(
                message=f'Request.{_KEY_PARAMS} must be a mapping',
                path=[_KEY_PARAMS],
            )

        return Request(path=path, params=params)
