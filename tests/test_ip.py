#! /usr/bin/env python3

import public_ip as ip

import requests_mock

from absl.testing import absltest
from absl.testing import parameterized

class GetPublicIPTest(parameterized.TestCase):
    @parameterized.named_parameters(
        {
            "testcase_name": "All URLs agree on the IP",
            'answers': {
                'https://api.ipify.org': '1.1.1.1',
                'https://checkip.amazonaws.com': '1.1.1.1',
                'https://icanhazip.com': '1.1.1.1',
                'https://ifconfig.co/ip': '1.1.1.1',
                'https://ipecho.net/plain': '1.1.1.1',
                'https://ipinfo.io/ip': '1.1.1.1',
             },
            "want":  '1.1.1.1',
        },
        {
            "testcase_name": "Wrong answer from one of the URLs",
            'answers': {
                'https://api.ipify.org': '1.1.1.1',
                'https://checkip.amazonaws.com': '1.1.1.1',
                'https://icanhazip.com': '1.1.1.1',
                'https://ifconfig.co/ip': '1.1.1.1',
                'https://ipecho.net/plain': '1.1.1.1',
                'https://ipinfo.io/ip': '2.2.2.2',
             },
            "want":  '1.1.1.1',
        },
        {
            "testcase_name": "Wrong answer from a minority of the URLs",
            'answers': {
                'https://api.ipify.org': '1.1.1.1',
                'https://checkip.amazonaws.com': '1.1.1.1',
                'https://icanhazip.com': '1.1.1.1',
                'https://ifconfig.co/ip': '1.1.1.1',
                'https://ipecho.net/plain': '2.2.2.2',
                'https://ipinfo.io/ip': '2.2.2.2',
             },
            "want":  '1.1.1.1',
        },
    )

    @requests_mock.Mocker()
    def test_get(self, mock, answers, want):

        for URL, reply in answers.items():
            mock.get(URL, text=reply)
        got = ip.get()
        self.assertEqual(got, want)


if __name__ == "__main__":
    absltest.main()
