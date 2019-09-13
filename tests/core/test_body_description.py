from unittest.mock import MagicMock, sentinel

from preacher.core.body_description import BodyDescription
from preacher.core.status import Status
from preacher.core.verification import Verification


def test_given_no_descriptions():
    description = BodyDescription()
    verification = description.verify('')
    assert verification.status == Status.SKIPPED


def test_given_invalid_body():
    descriptions = [MagicMock(return_value=Verification.succeed())]
    analyze = MagicMock(side_effect=RuntimeError('parse error'))

    description = BodyDescription(descriptions=descriptions, analyze=analyze)
    verification = description.verify('body')
    assert verification.status == Status.FAILURE
    assert verification.message.endswith('parse error')

    analyze.assert_called_once_with('body')
    descriptions[0].assert_not_called()


def test_given_descriptions():
    descriptions = [
        MagicMock(return_value=Verification(status=Status.UNSTABLE)),
        MagicMock(return_value=Verification.succeed()),
    ]
    analyze = MagicMock(return_value=sentinel.body)
    description = BodyDescription(descriptions=descriptions, analyze=analyze)
    verification = description.verify('body', k='v')
    assert verification.status == Status.UNSTABLE
    assert verification.children[0].status == Status.UNSTABLE
    assert verification.children[1].status == Status.SUCCESS

    analyze.assert_called_once_with('body')
    descriptions[0].assert_called_once_with(sentinel.body, k='v')
    descriptions[1].assert_called_once_with(sentinel.body, k='v')
