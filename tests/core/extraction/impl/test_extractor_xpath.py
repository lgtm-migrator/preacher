from unittest.mock import NonCallableMock

from lxml.etree import XMLParser, fromstring
from pytest import fixture, mark, raises

from preacher.core.extraction.analysis import Analyzer
from preacher.core.extraction.error import ExtractionError
from preacher.core.extraction.impl.xpath import XPathExtractor

VALUE = """
<root>
    <foo id="foo1">foo-text</foo>
    <foo id="foo2">
        <bar>text</bar>
        <baz attr="baz-attr" />
    </foo>
    <number>10</number>
    <numbers>
        <value>1</value>
    </numbers>
    <numbers>
    </numbers>
    <numbers>
        <value>2</value>
    </numbers>
    <namespacing xmlns="default-foo">
        <foo>foo-content</foo>
        <namespacing xmlns="default-bar">
            <bar>bar-content</bar>
        </namespacing>
    </namespacing>
    <ns-baz:namespacing xmlns:ns-baz="explicit-baz">
        <ns-baz:baz>ns-baz:baz-content</ns-baz:baz>
        <baz>baz-content</baz>
    </ns-baz:namespacing>
</root>
"""


@fixture
def analyzer():
    elem = fromstring(VALUE, parser=XMLParser())

    analyzer = NonCallableMock(Analyzer)
    analyzer.for_etree.side_effect = lambda x: x(elem)
    return analyzer


def test_extract_invalid(analyzer):
    extractor = XPathExtractor(".items")
    with raises(ExtractionError) as error_info:
        extractor.extract(analyzer)
    assert str(error_info.value).endswith(": .items")


@mark.parametrize(
    "query, expected",
    (
        ("/root/xxx", None),
        ("/root/foo", "foo-text"),
        ("./foo[1]", "foo-text"),
        ('//foo[@id="foo1"]', "foo-text"),
        (".//foo[2]/bar", "text"),
        ("//baz/@attr", "baz-attr"),
        ("./number", "10"),
        ("./numbers/value", "1"),
        ("/root/ns-foo:namespacing/ns-foo:foo", "foo-content"),
        ("/root/ns-foo:namespacing/ns-bar:namespacing/ns-bar:bar", "bar-content"),
        ("/root/ns-baz:namespacing/baz", "baz-content"),
        ("/root/ns-baz:namespacing/ns-baz:baz", "ns-baz:baz-content"),
    ),
)
def test_extract_default(query, expected, analyzer):
    namespaces = {"ns-foo": "default-foo", "ns-bar": "default-bar", "ns-baz": "explicit-baz"}
    extractor = XPathExtractor(query, namespaces=namespaces)
    assert extractor.extract(analyzer) == expected


@mark.parametrize(
    "query, multiple, cast, expected",
    (
        ("/root/xxx", False, None, None),
        ("/root/foo", False, None, "foo-text"),
        ("./foo[1]", False, None, "foo-text"),
        ('//foo[@id="foo1"]', False, None, "foo-text"),
        (".//foo[2]/bar", False, None, "text"),
        ("//baz/@attr", False, None, "baz-attr"),
        ("/root/xxx", True, None, None),
        ("/root/foo", True, None, ["foo-text", "\n        "]),
        ("./foo/bar", True, None, ["text"]),
        ("./foo/bar", True, None, ["text"]),
        ("./number", False, None, "10"),
        ("./number", False, int, 10),
        ("./numbers/value", True, None, ["1", "2"]),
        ("./numbers/value", True, int, [1, 2]),
    ),
)
def test_extract(query, multiple, cast, expected, analyzer):
    extractor = XPathExtractor(query, multiple=multiple, cast=cast)
    assert extractor.extract(analyzer) == expected
