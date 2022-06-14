from unittest.mock import NonCallableMock, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.error import CompilationError, NamedNode, IndexedNode
from preacher.compilation.request import RequestCompiler
from preacher.compilation.scenario.case import CaseCompiled, CaseCompiler
from preacher.compilation.verification.description import DescriptionCompiler
from preacher.compilation.verification.response import ResponseDescriptionCompiler

PKG = "preacher.compilation.scenario.case"


@fixture
def compiler(req, res, desc) -> CaseCompiler:
    return CaseCompiler(req, res, desc)


@fixture
def req():
    compiler = NonCallableMock(RequestCompiler)
    compiler.compile.return_value = sentinel.request
    compiler.of_default.return_value = sentinel.default_req_compiler
    return compiler


@fixture
def res():
    compiler = NonCallableMock(ResponseDescriptionCompiler)
    compiler.compile.return_value = sentinel.response
    compiler.of_default.return_value = sentinel.default_res_compiler
    return compiler


@fixture
def desc():
    compiler = NonCallableMock(DescriptionCompiler)
    compiler.compile.return_value = sentinel.description
    return compiler


@mark.parametrize(
    ("value", "expected_path"),
    (
        ("", []),
        ({"label": []}, [NamedNode("label")]),
        ({"enabled": []}, [NamedNode("enabled")]),
        ({"wait": "foo"}, [NamedNode("wait")]),
    ),
)
def test_given_invalid_values(compiler: CaseCompiler, value, expected_path):
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert error_info.value.path == expected_path


def test_conditions_compilation_fails(compiler: CaseCompiler, desc):
    desc.compile.side_effect = CompilationError("msg", node=NamedNode("foo"))
    with raises(CompilationError) as error_info:
        compiler.compile({"when": "xxx"})
    assert error_info.value.path == [NamedNode("when"), IndexedNode(0), NamedNode("foo")]

    desc.compile.assert_called_once_with("xxx")


def test_request_compilation_fails(compiler: CaseCompiler, req):
    req.compile.side_effect = CompilationError("msg", node=NamedNode("foo"))
    with raises(CompilationError) as error_info:
        compiler.compile({"request": "/path"})
    assert error_info.value.path == [NamedNode("request"), NamedNode("foo")]

    req.compile.assert_called_once_with("/path")


def test_response_compilation_fails(compiler: CaseCompiler, res):
    res.compile.side_effect = CompilationError("msg", node=NamedNode("bar"))
    with raises(CompilationError) as error_info:
        compiler.compile({"response": "res"})
    assert error_info.value.path == [NamedNode("response"), NamedNode("bar")]

    res.compile.assert_called_once_with("res")


def test_given_an_empty_object(compiler: CaseCompiler, req, res):
    compiled = compiler.compile({})
    assert compiled.label is None
    assert compiled.enabled is None
    assert compiled.conditions is None
    assert compiled.request is None
    assert compiled.response is None
    assert compiled.wait is None

    req.compile.assert_not_called()
    res.compile.assert_not_called()


def test_creates_a_case(compiler: CaseCompiler, req, res, desc):
    compiled = compiler.compile(
        {
            "label": "label",
            "enabled": False,
            "when": {"k": "v"},
            "request": {"path": "/path"},
            "response": {"key": "value"},
            "wait": "2 minutes",
        }
    )
    assert compiled.label == "label"
    assert not compiled.enabled
    assert compiled.conditions == [sentinel.description]
    assert compiled.request is sentinel.request
    assert compiled.response is sentinel.response
    assert compiled.wait
    assert compiled.wait.total_seconds() == 120.0

    req.compile.assert_called_once_with({"path": "/path"})
    res.compile.assert_called_once_with({"key": "value"})
    desc.compile.assert_called_once_with({"k": "v"})


@fixture
def initial_default():
    initial_default = NonCallableMock(CaseCompiled)
    initial_default.replace.return_value = sentinel.new_default
    return initial_default


def test_given_hollow_default(mocker, req, res, desc, initial_default):
    ctor = mocker.patch(f"{PKG}.CaseCompiler")
    ctor.return_value = sentinel.default_compiler

    compiler = CaseCompiler(req, res, desc, initial_default)

    default = NonCallableMock(CaseCompiled, request=None, response=None)
    compiler_of_default = compiler.of_default(default)
    assert compiler_of_default is sentinel.default_compiler

    req.of_default.assert_not_called()
    res.of_default.assert_not_called()
    ctor.assert_called_once_with(
        request=req,
        response=res,
        description=desc,
        default=sentinel.new_default,
    )


def test_given_filled_default(mocker, req, res, desc, initial_default):
    ctor = mocker.patch(f"{PKG}.CaseCompiler")
    ctor.return_value = sentinel.default_compiler

    compiler = CaseCompiler(req, res, desc, initial_default)

    default = NonCallableMock(
        spec=CaseCompiled,
        request=sentinel.default_req,
        response=sentinel.default_res,
    )
    compiler_of_default = compiler.of_default(default)
    assert compiler_of_default is sentinel.default_compiler

    req.of_default.assert_called_once_with(sentinel.default_req)
    res.of_default.assert_called_once_with(sentinel.default_res)
    ctor.assert_called_once_with(
        request=sentinel.default_req_compiler,
        response=sentinel.default_res_compiler,
        description=desc,
        default=sentinel.new_default,
    )


def test_compile_fixed(compiler: CaseCompiler, mocker):
    compiled = NonCallableMock(spec=CaseCompiled)
    compiled.fix.return_value = sentinel.fixed
    comp = mocker.patch.object(compiler, "compile", return_value=compiled)

    fixed = compiler.compile_fixed(sentinel.obj)
    assert fixed is sentinel.fixed

    comp.assert_called_once_with(sentinel.obj)
    compiled.fix.assert_called_once_with()


def test_compile_default(compiler: CaseCompiler, mocker):
    comp = mocker.patch.object(compiler, "compile")
    comp.return_value = sentinel.compiled

    of_default = mocker.patch.object(compiler, "of_default")
    of_default.return_value = sentinel.compiler_of_default

    compiler_of_default = compiler.compile_default(sentinel.obj)
    assert compiler_of_default is sentinel.compiler_of_default

    comp.assert_called_once_with(sentinel.obj)
    of_default.assert_called_once_with(sentinel.compiled)
