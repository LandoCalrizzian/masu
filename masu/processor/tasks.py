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
"""Asynchronous tasks."""

# pylint: disable=too-many-arguments, too-many-function-args
# disabled module-wide due to current state of task signature.
# we expect this situation to be temporary as we iterate on these details.

from celery import shared_task
from celery.utils.log import get_task_logger

from masu.database.report_stats_db_accessor import ReportStatsDBAccessor
from masu.exceptions import MasuProcessingError, MasuProviderError
from masu.external.accounts_accessor import AccountsAccessor
from masu.external.report_downloader import ReportDownloader, ReportDownloaderError
from masu.processor.report_processor import ReportProcessor

LOG = get_task_logger(__name__)


@shared_task(name='masu.processor.tasks.get_report_files', queue_name='download')
def get_report_files(customer_name,
                     access_credential,
                     report_source,
                     provider_type,
                     schema_name=None,
                     report_name=None):
    """Shared celery task to download reports asynchronously."""
    reports = _get_report_files(customer_name,
                                access_credential,
                                report_source,
                                provider_type,
                                report_name)

    # initiate chained async task
    for report_dict in reports:
        request = {'schema_name': schema_name,
                   'report_path': report_dict.get('file'),
                   'compression': report_dict.get('compression')}
        process_report_file.delay(**request)


def _get_report_files(customer_name,
                      access_credential,
                      report_source,
                      provider_type,
                      report_name=None):
    """
    Task to download a Cost Usage Report.

    Note that report_name will be not optional once Koku can specify
    what report we should downlad.

    Args:
        customer_name     (String): Name of the customer owning the cost usage report.
        access_credential (String): Credential needed to access cost usage report
                                    in the backend provider.
        report_source     (String): Location of the cost usage report in the backend provider.
        provider_type     (String): Koku defined provider type string.  Example: Amazon = 'AWS'
        report_name       (String): Name of the cost usage report to download.

    Returns:
        files (List) List of filenames with full local path.
               Example: ['/var/tmp/masu/region/aws/catch-clearly.csv',
                         '/var/tmp/masu/base/aws/professor-hour-industry-television.csv']

    """
    stmt = ('Downloading report for'
            ' credential: {},'
            ' source: {},'
            ' customer_name: {},'
            ' provider: {}')
    log_statement = stmt.format(access_credential,
                                report_source,
                                customer_name,
                                provider_type)
    LOG.info(log_statement)

    reports = []
    try:
        downloader = ReportDownloader(customer_name=customer_name,
                                      access_credential=access_credential,
                                      report_source=report_source,
                                      provider_type=provider_type,
                                      report_name=report_name)
        return downloader.get_current_report()
    except (MasuProcessingError, MasuProviderError, ReportDownloaderError) as err:
        LOG.error(str(err))
        return []

    return reports


@shared_task(name='masu.processor.tasks.process_report_file', queue_name='process')
def process_report_file(schema_name, report_path, compression):
    """Shared celery task to process report files asynchronously."""
    _process_report_file(schema_name, report_path, compression)


def _process_report_file(schema_name, report_path, compression):
    """
    Task to process a Cost Usage Report.

    Args:
        schema_name (String) db schema name
        report_path (String) path to downloaded reports
        compression (String) 'PLAIN' or 'GZIP'

    Returns:
        None

    """
    stmt = ('Processing Report:'
            ' schema_name: {},'
            ' report_path: {},'
            ' compression: {}')
    log_statement = stmt.format(schema_name,
                                report_path,
                                compression)
    LOG.info(log_statement)

    file_name = report_path.split('/')[-1]
    stats_recorder = ReportStatsDBAccessor(file_name)
    cursor_position = stats_recorder.get_cursor_position()

    processor = ReportProcessor(schema_name=schema_name,
                                report_path=report_path,
                                compression=compression,
                                cursor_pos=cursor_position)

    stats_recorder.log_last_started_datetime()
    last_cursor_position = processor.process()
    stats_recorder.log_last_completed_datetime()
    stats_recorder.set_cursor_position(last_cursor_position)
    stats_recorder.commit()


@shared_task(name='masu.processor.tasks.check_report_updates', queue_name='celery')
def check_report_updates():
    """Scheduled task to initiate scanning process on a regular interval."""
    reports = []
    for account in AccountsAccessor().get_accounts():
        stmt = 'Download task queued for {}'.format(account.get_customer())
        LOG.info(stmt)

        reports = get_report_files.delay(customer_name=account.get_customer(),
                                         access_credential=account.get_access_credential(),
                                         report_source=account.get_billing_source(),
                                         provider_type=account.get_provider_type(),
                                         schema_name=account.get_schema_name())
    return reports
