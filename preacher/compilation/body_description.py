from collections.abc import Mapping
from typing import Any, Optional

from preacher.core.body_description import BodyDescription
from preacher.core.description import Description
from .description import DescriptionCompiler
from .error import CompilationError
from .util import map_on_key


_KEY_DESCRIPTIONS = 'descriptions'


class BodyDescriptionCompiler:

    def __init__(
        self,
        description_compiler: Optional[DescriptionCompiler] = None,
    ):
        self._description_compiler = (
            description_compiler or DescriptionCompiler()
        )

    def compile(self, obj: Any) -> BodyDescription:
        desc_objs = obj
        if isinstance(obj, Mapping):
            desc_objs = obj.get(_KEY_DESCRIPTIONS, [])

        if not isinstance(desc_objs, list):
            message = f'must be a list or a mapping'
            raise CompilationError(message=message)

        descriptions = list(map_on_key(
            key=_KEY_DESCRIPTIONS,
            func=self._compile_description,
            items=desc_objs,
        ))
        return BodyDescription(descriptions=descriptions)

    def _compile_description(self, obj: Any) -> Description:
        if not isinstance(obj, Mapping):
            raise CompilationError('Description must be a mapping')
        return self._description_compiler.compile(obj)
