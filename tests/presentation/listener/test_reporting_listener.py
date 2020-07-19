from unittest.mock import MagicMock, call, patch, sentinel

from pytest import fixture

from preacher.presentation.listener import ReportingListener
from preacher.presentation.report import Reporter

PACKAGE = 'preacher.presentation.listener.report'


@fixture
def reporter():
    return MagicMock(Reporter)


def test_given_no_item(reporter):
    listener = ReportingListener(reporter)
    listener.on_end(sentinel.status)

    reporter.export_response.assert_not_called()
    reporter.export_results.assert_called_once_with([])


def test_given_items(reporter):
    listener = ReportingListener(reporter)
    listener.on_execution(sentinel.execution1, sentinel.response1)
    listener.on_scenario(sentinel.scenario1)
    listener.on_execution(sentinel.execution2, sentinel.response2)
    listener.on_execution(sentinel.execution_none, None)
    listener.on_execution(sentinel.execution3, sentinel.response3)
    listener.on_scenario(sentinel.scenario2)
    listener.on_end(sentinel.status)

    reporter.export_response.assert_has_calls([
        call(sentinel.response1),
        call(sentinel.response2),
        call(sentinel.response3),
    ])
    reporter.export_results.assert_called_once_with([
        sentinel.scenario1,
        sentinel.scenario2,
    ])


@patch(f'{PACKAGE}.ReportingListener', return_value=sentinel.listener)
@patch(f'{PACKAGE}.Reporter', return_value=sentinel.reporter)
def test_from_path(reporter_ctor, listener_ctor):
    listener = ReportingListener.from_path(sentinel.path)
    assert listener is sentinel.listener

    reporter_ctor.assert_called_once_with(sentinel.path)
    listener_ctor.assert_called_once_with(sentinel.reporter)
