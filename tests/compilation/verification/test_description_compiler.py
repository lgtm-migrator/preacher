from unittest.mock import NonCallableMock, call, sentinel

from pytest import fixture, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.extraction import ExtractionCompiler
from preacher.compilation.verification.description import DescriptionCompiler
from preacher.compilation.verification.predicate import PredicateCompiler

PKG = "preacher.compilation.verification.description"


@fixture
def compiler(extraction, predicate) -> DescriptionCompiler:
    return DescriptionCompiler(extraction, predicate)


@fixture
def extraction():
    extraction = NonCallableMock(ExtractionCompiler)
    extraction.compile.return_value = sentinel.extractor
    return extraction


@fixture
def predicate():
    predicate = NonCallableMock(PredicateCompiler)
    predicate.compile.return_value = sentinel.predicate
    return predicate


def test_given_not_a_mapping(compiler):
    with raises(CompilationError):
        compiler.compile([])


def test_given_a_string_predicate(mocker, compiler, extraction, predicate):
    ctor = mocker.patch(f"{PKG}.Description", return_value=sentinel.description)

    description = compiler.compile(
        {
            "describe": "foo",
            "should": "string",
        }
    )
    assert description is sentinel.description

    extraction.compile.assert_called_with("foo")
    predicate.compile.assert_called_once_with("string")
    ctor.assert_called_once_with(
        extractor=sentinel.extractor,
        predicates=[sentinel.predicate],
        value_name=None,
    )


def test_given_a_mapping_predicate(mocker, compiler, extraction, predicate):
    ctor = mocker.patch(f"{PKG}.Description", return_value=sentinel.description)

    description = compiler.compile({"describe": "foo", "should": {"key": "value"}})
    assert description is sentinel.description

    extraction.compile.assert_called_once_with("foo")
    predicate.compile.assert_called_once_with({"key": "value"})
    ctor.assert_called_once_with(
        extractor=sentinel.extractor,
        predicates=[sentinel.predicate],
        value_name=None,
    )


def test_given_a_list_of_mapping_predicates(mocker, compiler, extraction, predicate):
    ctor = mocker.patch(f"{PKG}.Description", return_value=sentinel.description)

    description = compiler.compile(
        {
            "describe": {"key": "value"},
            "as": "foo",
            "should": [{"key1": "value1"}, {"key2": "value2"}],
        }
    )
    assert description is sentinel.description

    extraction.compile.assert_called_once_with({"key": "value"})
    predicate.compile.assert_has_calls([call({"key1": "value1"}), call({"key2": "value2"})])
    ctor.assert_called_once_with(
        extractor=sentinel.extractor,
        predicates=[sentinel.predicate, sentinel.predicate],
        value_name="foo",
    )
