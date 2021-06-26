from unittest.mock import Mock, NonCallableMock, sentinel

from pytest import fixture

from preacher.core.value import Value
from preacher.core.verification.matcher import MatcherFactory
from preacher.core.verification.matcher import RecursiveMatcherFactory
from preacher.core.verification.matcher import StaticMatcherFactory
from preacher.core.verification.matcher import ValueMatcherFactory


@fixture
def matcher_func():
    return Mock(return_value=sentinel.matcher)


def test_static_factory():
    matcher = StaticMatcherFactory(sentinel.matcher)
    assert matcher.create() == sentinel.matcher


def test_value_factory(matcher_func):
    value = NonCallableMock(Value)
    value.resolve.return_value = sentinel.resolved

    factory = ValueMatcherFactory(matcher_func, value)
    matcher = factory.create(sentinel.context)

    assert matcher is sentinel.matcher
    value.resolve.assert_called_once_with(sentinel.context)
    matcher_func.assert_called_once_with(sentinel.resolved)


def test_recursive_factory(matcher_func):
    inner_factories = [
        NonCallableMock(MatcherFactory, create=Mock(return_value=sentinel.inner_matcher_0)),
        NonCallableMock(MatcherFactory, create=Mock(return_value=sentinel.inner_matcher_1)),
    ]

    factory = RecursiveMatcherFactory(matcher_func, inner_factories)
    matcher = factory.create(sentinel.context)
    assert matcher is sentinel.matcher
    for inner_matcher in inner_factories:
        inner_matcher.create.assert_called_once_with(sentinel.context)
    matcher_func.assert_called_once_with(sentinel.inner_matcher_0, sentinel.inner_matcher_1)
