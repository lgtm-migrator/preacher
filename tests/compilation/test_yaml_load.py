from io import StringIO
from unittest.mock import call

from pytest import mark, raises

from preacher.compilation.error import CompilationError, IndexedNode, NamedNode
from preacher.compilation.yaml import (
    PathLike,
    _Resolvable,
    load,
    load_from_path,
    load_all,
    load_all_from_path,
)


def test_resolvable_interface():
    class _Incomplete(_Resolvable):
        def resolve(self, origin: PathLike) -> object:
            return super().resolve(origin)

    resolvable = _Incomplete()
    with raises(NotImplementedError):
        resolvable.resolve('')


@mark.parametrize(('content', 'expected_path'), (
    ('!invalid', []),
    ('- !argument {}', [IndexedNode(0)]),
    ('{key: !argument []}', [NamedNode('key')]),
    ('{key: [!argument {}]}', [NamedNode('key'), IndexedNode(0)]),
))
def test_load_given_invalid_content(content, expected_path):
    stream = StringIO(content)
    with raises(CompilationError) as error_info:
        load(stream)
    assert error_info.value.path == expected_path


def test_load_all_given_invalid_value():
    stream = StringIO('!invalid')
    with raises(CompilationError):
        next(load_all(stream))


def test_load_from_path_not_found(mocker):
    mocker.patch('builtins.open', side_effect=FileNotFoundError('message'))
    with raises(CompilationError):
        load_from_path('/////foo/bar/baz')


def test_load_from_path(mocker):
    content = StringIO('!include inner/included.yml')
    included_content = StringIO('foo')

    open_mock = mocker.patch('builtins.open')
    open_mock.side_effect = [content, included_content]

    actual = load_from_path('path/to/scenario.yml')
    assert actual == 'foo'

    assert content.closed
    assert included_content.closed
    open_mock.assert_has_calls([
        call('path/to/scenario.yml'),
        call('path/to/inner/included.yml'),
    ])


def test_load_all_from_path_not_found(mocker):
    mocker.patch('builtins.open', side_effect=FileNotFoundError('message'))

    objs = load_all_from_path('/////foo/bar/baz')
    with raises(CompilationError):
        next(objs)


def test_load_all_from_path(mocker):
    open_mock = mocker.patch('builtins.open')
    open_mock.return_value = StringIO('1\n---\n2\n---\n!argument foo')

    actual = load_all_from_path('path/to/foo.yaml')
    assert next(actual) == 1
    assert next(actual) == 2
    assert next(actual).key == 'foo'
    with raises(StopIteration):
        next(actual)

    open_mock.assert_called_once_with('path/to/foo.yaml')
