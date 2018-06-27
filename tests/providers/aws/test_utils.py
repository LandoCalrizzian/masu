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

from dateutil.relativedelta import relativedelta

import random
import string
from unittest import TestCase
from datetime import datetime
from unittest.mock import patch


import boto3
from faker import Faker
from moto import mock_sts

from masu.providers.aws.utils import (get_assume_role_session,
                                      month_date_range)

class TestAWSUtils(TestCase):
    fake = Faker()

    report_defs = [{'ReportName': 'stuff',
                    'TimeUnit': 'DAILY',
                    'Format': 'csv',
                    'Compression': 'GZIP',
                    'S3Bucket': 'city',
                    'S3Prefix': 'real',
                    'S3Region': 'sa-east-1'}]

    @mock_sts
    def test_get_assume_role_session(self):
        account = ''.join(random.choices(string.digits, k=12))
        arn = 'arn:aws:iam::{}:{}/{}'.format(account,
                                             self.fake.word(),
                                             self.fake.word())

        session = get_assume_role_session(arn)
        self.assertIsInstance(session, boto3.Session)

    def test_month_date_range(self):
        today = datetime.now()
        out = month_date_range(today)

        start_month = today.replace(day=1, second=1, microsecond=1)
        end_month = start_month + relativedelta(months=+1)
        timeformat = '%Y%m%d'
        expected_string = '{}-{}'.format(start_month.strftime(timeformat),
                                         end_month.strftime(timeformat))

        self.assertEqual(out, expected_string)
