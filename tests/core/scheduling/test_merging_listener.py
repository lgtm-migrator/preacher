from unittest.mock import NonCallableMock, sentinel

from pytest import fixture

from preacher.core.scheduling.listener import Listener, MergingListener


@fixture
def listeners():
    return [NonCallableMock(Listener), NonCallableMock(Listener)]


@fixture
def merging_listener(listeners) -> MergingListener:
    merging_listener = MergingListener()
    for listener in listeners:
        merging_listener.append(listener)
    return merging_listener


def test_on_response(merging_listener, listeners):
    merging_listener.on_execution(sentinel.execution, sentinel.response)
    for listener in listeners:
        listener.on_execution.assert_called_once_with(sentinel.execution, sentinel.response)


def test_on_scenario(merging_listener, listeners):
    merging_listener.on_scenario(sentinel.scenario)
    for listener in listeners:
        listener.on_scenario.assert_called_once_with(sentinel.scenario)


def test_on_end(merging_listener, listeners):
    merging_listener.on_end(sentinel.status)
    for listener in listeners:
        listener.on_end.assert_called_once_with(sentinel.status)
