from datetime import date, datetime, timedelta

from pytest import raises, mark

from preacher.compilation.argument import Argument
from preacher.compilation.error import CompilationError, IndexedNode, NamedNode
from preacher.compilation.request.url_param import compile_url_params
from preacher.core.value.impl.datetime import RelativeDatetimeWithFormat

DATE = date(2019, 12, 31)
DATETIME = datetime.fromisoformat('2020-04-01T01:23:45+09:00')
RELATIVE_DATETIME_VALUE = RelativeDatetimeWithFormat(timedelta(seconds=1))


@mark.parametrize(('obj', 'expected_path'), [
    (1, []),
    ([1, 2], []),
    ({1: 2}, []),
    ({'k': complex(1, 2)}, [NamedNode('k')]),
    ({'k': frozenset()}, [NamedNode('k')]),
    ({'k': {}}, [NamedNode('k')]),
    ({'k': [[]]}, [NamedNode('k'), IndexedNode(0)]),
    ({'k': ['a', complex(2, 3)]}, [NamedNode('k'), IndexedNode(1)]),
])
def test_given_invalid_object(obj, expected_path):
    with raises(CompilationError) as error_info:
        compile_url_params(obj)
    assert error_info.value.path == expected_path


@mark.parametrize('obj', [
    'str',
    {},
    {'null': None},
    {'boolean': False},
    {'int': 1},
    {'float': 0.1},
    {'str': 'string'},
    {'date': DATE},
    {'datetime': DATETIME},
    {'relative_datetime_value': RELATIVE_DATETIME_VALUE},
    {'single': 's', 'multiple': [None, DATETIME, RELATIVE_DATETIME_VALUE]},
])
def test_given_valid_params(obj):
    compiled = compile_url_params(Argument('obj'), {'obj': obj})
    assert compiled == obj
