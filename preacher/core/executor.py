"""An executor."""

from functools import partial
from typing import Optional, Tuple

import requests

from preacher.core.request import Request, Response, ExecutionReport
from preacher.core.scenario.util.retry import retry_while_false
from preacher.core.value import ValueContext
from preacher.core.verification import ResponseDescription, ResponseVerification


class ExecutionListener:
    """
    Interface to listen to running cases.
    Default implementations do nothing.
    """

    def on_execution(
        self,
        execution: ExecutionReport,
        response: Optional[Response],
    ) -> None:
        pass


def _predicate(result: Tuple[ExecutionReport, Optional[ResponseVerification]]) -> bool:
    execution, verification = result
    if not execution.status.is_succeeded:
        return False
    if verification is None:
        return True
    return verification.status.is_succeeded


class Executor:

    def __init__(
        self,
        base_url: str = '',
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
        session: Optional[requests.Session] = None,
    ):
        if retry < 0:
            raise ValueError(f'`retry` must be zero or positive, given {retry}')

        self._base_url = base_url
        self._retry = retry
        self._delay = delay
        self._timeout = timeout
        self._session = session

    def execute(
        self,
        request: Request,
        requirements: ResponseDescription,
        listener: Optional[ExecutionListener],
    ) -> Tuple[ExecutionReport, Optional[ResponseVerification]]:
        listener = listener or ExecutionListener()
        return retry_while_false(
            partial(self._execute, request, requirements, listener),
            attempts=self._retry + 1,
            delay=self._delay,
            predicate=_predicate,
        )

    def _execute(
        self,
        request: Request,
        requirements: ResponseDescription,
        listener: ExecutionListener
    ) -> Tuple[ExecutionReport, Optional[ResponseVerification]]:
        execution, response = request.execute(
            self._base_url,
            timeout=self._timeout,
            session=self._session,
        )
        listener.on_execution(execution, response)

        if not response:
            return execution, None

        context = ValueContext(origin_datetime=execution.starts)
        verification = requirements.verify(response, context)
        return execution, verification
