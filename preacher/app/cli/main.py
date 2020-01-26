"""Preacher CLI."""

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from preacher.app.cli.option import parse_args
from preacher.compilation.factory import create_compiler
from preacher.compilation.yaml import load
from preacher.core.listener.log import LoggingListener
from preacher.core.listener.merging import MergingListener
from preacher.core.listener.report import ReportingListener
from preacher.core.runner import ScenarioRunner
from preacher.presentation.log import ColoredFormatter

FORMATTER = ColoredFormatter()
HANDLER = logging.StreamHandler()
HANDLER.setFormatter(FORMATTER)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(HANDLER)


def _load(path: str) -> object:
    with open(path) as f:
        return load(f)


def _main() -> None:
    """Main."""
    args = parse_args(environ=os.environ)

    level = args.level
    HANDLER.setLevel(level)
    LOGGER.setLevel(level)

    app = ScenarioRunner(
        base_url=args.url,
        retry=args.retry,
        delay=args.delay,
        timeout=args.timeout,
    )

    compiler = create_compiler()
    scenarios = (
        compiler.compile(obj, arguments=args.argument)
        for obj in (_load(path) for path in args.scenario)
    )

    listener = MergingListener()
    listener.append(LoggingListener.from_logger(LOGGER))
    if args.report:
        listener.append(ReportingListener.from_path(args.report))

    with ThreadPoolExecutor(args.concurrency) as executor:
        status = app.run(executor, scenarios, listener=listener)

    if not status.is_succeeded:
        sys.exit(1)


def main():
    try:
        _main()
    except Exception as error:
        LOGGER.exception('%s', error)
        sys.exit(2)
