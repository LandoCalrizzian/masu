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

"""Test the Orchestrator object."""

from unittest.mock import patch

from masu.config import Config
from masu.exceptions import MasuProviderError
from masu.processor.orchestrator import Orchestrator

from tests import MasuTestCase

class FakeDownloader():
    def download_current_report():
        return [{'file': '/var/tmp/masu/region/aws/catch-clearly.csv', 'compression': 'GZIP'},
                {'file': '/var/tmp/masu/base/aws/professor-hour-industry-television.csv', 'compression': 'GZIP'}]


class OrchestratorTest(MasuTestCase):
    """Test Cases for the Orchestrator object."""

    def test_initializer(self):
        """Test to init"""
        orchestrator = Orchestrator()

        if len(orchestrator._accounts) != 1:
            self.fail("Unexpected number of test accounts")

        account = orchestrator._accounts.pop()
        self.assertEqual(account.get('authentication'), 'arn:aws:iam::111111111111:role/CostManagement')
        self.assertEqual(account.get('billing_source'), 'test-bucket')
        self.assertEqual(account.get('customer'), 'Test Customer')
        self.assertEqual(account.get('provider'), Config.AMAZON_WEB_SERVICES)

    @patch('masu.downloader.ReportDownloader._set_downloader', return_value=FakeDownloader)
    def test_prepare(self, mock_downloader):
        """Test downloading cost usage reports."""
        orchestrator = Orchestrator()
        reports = orchestrator.prepare()
        self.assertEqual(len(reports), 2)

    @patch('masu.downloader.ReportDownloader._set_downloader', return_value=FakeDownloader)
    @patch('masu.processor.account.Account.all', return_value=[])
    def test_prepare_no_accounts(self, mock_downloader, mock_accounts_accessor):
        """Test downloading cost usage reports."""
        orchestrator = Orchestrator()
        reports = orchestrator.prepare()
        self.assertEqual(len(reports), 0)

    @patch('masu.processor.tasks.process.process_report_file', return_value=None)
    def test_process(self, mock_task):
        """Test downloading cost usage reports."""
        requests = [{'report_path' : '/test/path/file.csv'},
                    {'report_path' : '/test/path/file2.csv'}]
        orchestrator = Orchestrator()
        orchestrator._processing_requests = requests
        orchestrator.process()
        # FIXME: missing assertion

    @patch('masu.processor.tasks.process.process_report_file', return_value=None)
    @patch('masu.processor.account.Account.all', return_value=[])
    def test_process_not_accounts(self, mock_task, mock_accounts_accessor):
        """Test downloading cost usage reports with no pending requests."""
        orchestrator = Orchestrator()
        orchestrator.process()
        # FIXME: missing assertion

    @patch('masu.downloader.ReportDownloader._set_downloader',
           side_effect=MasuProviderError)
    def test_prepare_download_exception(self, mock_downloader):
        """Test downloading cost usage reports."""
        orchestrator = Orchestrator()
        reports = orchestrator.prepare()
        self.assertEqual(len(reports), 0)
