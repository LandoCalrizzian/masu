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

"""Test the Local Report Downloader."""

import os.path
import random
import shutil
import tarfile
import tempfile
from tarfile import TarFile

from faker import Faker

from datetime import datetime
from unittest.mock import patch
from masu.config import Config
from masu.external.date_accessor import DateAccessor
from masu.external.downloader.local.local_report_downloader import LocalReportDownloader
from masu.external import AWS_REGIONS
from tests import MasuTestCase
from tests.external.downloader.aws import fake_arn

DATA_DIR = Config.TMP_DIR
FAKE = Faker()
CUSTOMER_NAME = FAKE.word()
REPORT = FAKE.word()
PREFIX = FAKE.word()

# the cn endpoints aren't supported by moto, so filter them out
AWS_REGIONS = list(filter(lambda reg: not reg.startswith('cn-'), AWS_REGIONS))
REGION = random.choice(AWS_REGIONS)


class LocalReportDownloaderTest(MasuTestCase):
    """Test Cases for the Local Report Downloader."""

    fake = Faker()

    def setUp(self):
        os.makedirs(DATA_DIR, exist_ok=True)

        self.fake_customer_name = CUSTOMER_NAME
        self.fake_report_name = 'koku-local'
        self.fake_bucket_name = tempfile.mkdtemp()
        self.fake_bucket_prefix = PREFIX
        self.selected_region = REGION
        self.fake_auth_credential = fake_arn(service='iam', generate_account_id=True)

        mytar = TarFile.open('./tests/data/test_local_bucket.tar.gz')
        mytar.extractall(path=self.fake_bucket_name)

        self.report_downloader = LocalReportDownloader(**{'customer_name': self.fake_customer_name,
                                                          'auth_credential': self.fake_auth_credential,
                                                          'bucket': self.fake_bucket_name})

    def tearDown(self):
        shutil.rmtree(DATA_DIR, ignore_errors=True)
        shutil.rmtree(self.fake_bucket_name)

    def test_download_bucket(self):
        """Test to verify that basic report downloading works."""
        test_report_date = datetime(year=2018, month=8, day=7)
        with patch.object(DateAccessor, 'today', return_value=test_report_date):
            self.report_downloader.download_current_report()
        expected_path = '{}/{}/{}'.format(DATA_DIR, self.fake_customer_name, 'local')
        self.assertTrue(os.path.isdir(expected_path))
 
    def test_report_name_provided(self):
        """Test initializer when report_name is  provided."""
        report_downloader = LocalReportDownloader(**{'customer_name': self.fake_customer_name,
                                                     'auth_credential': self.fake_auth_credential,
                                                     'bucket': self.fake_bucket_name,
                                                     'report_name': 'awesome-report'})
        self.assertEqual(report_downloader.report_name, 'awesome-report')

    def test_extract_names_no_prefix(self):
        """Test to extract the report and prefix names from a bucket with no prefix."""
        report_downloader = LocalReportDownloader(**{'customer_name': self.fake_customer_name,
                                                     'auth_credential': self.fake_auth_credential,
                                                     'bucket': self.fake_bucket_name})
        self.assertEqual(report_downloader.report_name, self.fake_report_name)
        self.assertIsNone(report_downloader.report_prefix)

    def test_download_bucket_with_prefix(self):
        """Test to verify that basic report downloading works."""
        fake_bucket = tempfile.mkdtemp()
        mytar = TarFile.open('./tests/data/test_local_bucket_prefix.tar.gz')
        mytar.extractall(fake_bucket)
        test_report_date = datetime(year=2018, month=8, day=7)
        with patch.object(DateAccessor, 'today', return_value=test_report_date):
            report_downloader = LocalReportDownloader(**{'customer_name': self.fake_customer_name,
                                                        'auth_credential': self.fake_auth_credential,
                                                        'bucket': fake_bucket})
            # Names from test report .gz file
            self.assertEqual(report_downloader.report_name, 'my-report')
            self.assertEqual(report_downloader.report_prefix, 'my-prefix')
            report_downloader.download_current_report()
        expected_path = '{}/{}/{}'.format(DATA_DIR, self.fake_customer_name, 'local')
        self.assertTrue(os.path.isdir(expected_path))

        shutil.rmtree(fake_bucket)

    def test_extract_names_with_prefix(self):
        """Test to extract the report and prefix names from a bucket with prefix."""
        bucket = tempfile.mkdtemp()
        report_name = 'report-name'
        prefix_name = 'prefix-name'
        full_path = '{}/{}/{}/20180801-20180901/'.format(bucket, prefix_name, report_name)
        os.makedirs(full_path)
        report_downloader = LocalReportDownloader(**{'customer_name': self.fake_customer_name,
                                                     'auth_credential': self.fake_auth_credential,
                                                     'bucket': bucket})
        self.assertEqual(report_downloader.report_name, report_name)
        self.assertEqual(report_downloader.report_prefix, prefix_name)
        shutil.rmtree(full_path)

    def test_extract_names_with_bad_path(self):
        """Test to extract the report and prefix names from a bad path."""
        bucket = tempfile.mkdtemp()
        report_name = 'report-name'
        prefix_name = 'prefix-name'
        full_path = '{}/{}/{}/20180801-aaaaaaa/'.format(bucket, prefix_name, report_name)
        os.makedirs(full_path)

        report_downloader = LocalReportDownloader(**{'customer_name': self.fake_customer_name,
                                                     'auth_credential': self.fake_auth_credential,
                                                     'bucket': bucket})
        self.assertIsNone(report_downloader.report_name)
        self.assertIsNone(report_downloader.report_prefix)

        shutil.rmtree(full_path)

    def test_extract_names_with_incomplete_path(self):
        """Test to extract the report and prefix from a path where a CUR hasn't been generated yet."""
        bucket = tempfile.mkdtemp()
        report_downloader = LocalReportDownloader(**{'customer_name': self.fake_customer_name,
                                                     'auth_credential': self.fake_auth_credential,
                                                     'bucket': bucket})
        self.assertIsNone(report_downloader.report_name)
        self.assertIsNone(report_downloader.report_prefix)

        shutil.rmtree(bucket)