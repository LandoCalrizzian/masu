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

"""Test the ReportDownloader object."""

from unittest.mock import patch

from masu.config import Config
from masu.exceptions import MasuProviderError
from masu.providers.aws.downloader import AWSReportDownloader
from masu.processor.downloader import ReportDownloader
from tests import MasuTestCase

class FakeDownloader():
    pass


class ReportDownloaderTest(MasuTestCase):
    """Test Cases for the ReportDownloader object."""

    @patch('masu.providers.aws.downloader.AWSReportDownloader.__init__', return_value=None)
    def test_initializer(self, fake_downloader):
        """Test to initializer"""
        downloader = ReportDownloader(customer_name='customer name',
                                      access_credential='mycred',
                                      report_source='hereiam',
                                      report_name='bestreport',
                                      provider_type=Config.AMAZON_WEB_SERVICES)
        self.assertIsNotNone(downloader._downloader)

    @patch('masu.processor.downloader.ReportDownloader._set_downloader',
           side_effect=MasuProviderError)
    def test_initializer_downloader_exception(self, fake_downloader):
        """Test to initializer where _set_downloader throws exception"""
        with self.assertRaises(MasuProviderError):
            ReportDownloader(customer_name='customer name',
                             access_credential='mycred',
                             report_source='hereiam',
                             report_name='bestreport',
                             provider_type=Config.AMAZON_WEB_SERVICES)

    def test_invalid_provider_type(self):
        """Test that error is thrown with invalid account source."""

        with self.assertRaises(MasuProviderError):
            ReportDownloader(customer_name='customer name',
                             access_credential='mycred',
                             report_source='hereiam',
                             report_name='bestreport',
                             provider_type='unknown')
