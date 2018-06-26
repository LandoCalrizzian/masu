#
# Copyright 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Celery task definitions."""

import datetime
import logging
from unittest import mock

from celery.task import periodic_task
from celery.utils.log import get_task_logger

from masu.processor.tasks.download import get_report_files
from masu.processor.tasks.process import process_report_file
from masu.processor.orchestrator import Orchestrator

LOG = get_task_logger(__name__)


# TODO: Get periodic test to work
@periodic_task(run_every=datetime.timedelta(hours=1))
def check_for_report_updates():
    orchestrator = Orchestrator()
    orchestrator.prepare_curs()
