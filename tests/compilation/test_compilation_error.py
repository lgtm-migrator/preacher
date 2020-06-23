from pytest import mark

from preacher.compilation.error import (
    CompilationError,
    IndexedNode,
    NamedNode,
    render_path,
)


@mark.parametrize('path, expected', [
    ([], ''),
    ([NamedNode('foo')], '.foo'),
    ([IndexedNode(0)], '[0]'),
    (
        [
            NamedNode('foo'),
            IndexedNode(1),
            IndexedNode(2),
            NamedNode('bar'),
        ],
        '.foo[1][2].bar',
    ),
])
def test_render_path(path, expected):
    assert render_path(path) == expected
    assert CompilationError('message', path=path).render_path() == expected
