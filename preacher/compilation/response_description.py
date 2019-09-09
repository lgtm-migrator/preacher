"""Response description compilations."""

from collections.abc import Mapping
from typing import Any, Optional, Iterator

from preacher.core.description import Description
from preacher.core.response_description import ResponseDescription
from .error import CompilationError
from .description import DescriptionCompiler
from .predicate import PredicateCompiler
from .util import map_on_key


_KEY_STATUS_CODE = 'status_code'
_KEY_BODY = 'body'


class ResponseDescriptionCompiler:

    def __init__(
        self,
        predicate_compiler: Optional[PredicateCompiler] = None,
        description_compiler: Optional[DescriptionCompiler] = None,
    ):
        self._predicate_compiler = predicate_compiler or PredicateCompiler()
        self._description_compiler = (
            description_compiler
            or DescriptionCompiler(
                predicate_compiler=self._predicate_compiler
            )
        )

    def compile(self, obj: Mapping) -> ResponseDescription:
        status_code_predicate_objs = obj.get(_KEY_STATUS_CODE, [])
        if not isinstance(status_code_predicate_objs, list):
            status_code_predicate_objs = [status_code_predicate_objs]
        status_code_predicates = list(map_on_key(
            key=_KEY_STATUS_CODE,
            func=self._predicate_compiler.compile,
            items=status_code_predicate_objs,
        ))

        body_descriptions = list(self._compile_descriptions(_KEY_BODY, obj))

        return ResponseDescription(
            status_code_predicates=status_code_predicates,
            body_descriptions=body_descriptions,
        )

    def _compile_descriptions(
        self,
        key: str,
        obj: Any,
    ) -> Iterator[Description]:
        description_objs = obj.get(_KEY_BODY, [])
        if isinstance(description_objs, Mapping):
            description_objs = [description_objs]
        if not isinstance(description_objs, list):
            message = f'ResponseDescription.{key} must be a list or a mapping'
            raise CompilationError(message=message, path=[key])

        return map_on_key(
            key=key,
            func=self._compile_description,
            items=description_objs,
        )

    def _compile_description(self, obj: Any) -> Description:
        if not isinstance(obj, Mapping):
            raise CompilationError('Description must be a mapping')
        return self._description_compiler.compile(obj)
