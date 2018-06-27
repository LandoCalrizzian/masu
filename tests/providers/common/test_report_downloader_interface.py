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
"""Test the report downloader base class."""

import os.path
from unittest.mock import patch

from faker import Faker
from pyfakefs.fake_filesystem_unittest import TestCaseMixin

from masu.providers.common.downloader import ReportDownloaderInterface
from tests import MasuTestCase

class FakeDownloader(ReportDownloaderInterface):
    def download_current_report(self, dt):
        return []

    def download_report(self):
        return []


class ReportDownloaderInterfaceTest(MasuTestCase, TestCaseMixin):
    """Test Cases for ReportDownloaderBase."""

    fake = Faker()
    patch_path = True

    def setUp(self):
        self.setUpPyfakefs()

    def test_report_downloader_base_no_path(self):
        downloader = FakeDownloader()
        self.assertIsInstance(downloader, ReportDownloaderInterface)
        self.assertIsNotNone(downloader.download_path)
        self.assertTrue(os.path.exists(downloader.download_path))

    def test_report_downloader_interface(self):
        dl_path = '/{}/{}/{}'.format(self.fake.word().lower(),
                                     self.fake.word().lower(),
                                     self.fake.word().lower())
        downloader = FakeDownloader(download_path=dl_path)
        self.assertEqual(downloader.download_path, dl_path)
