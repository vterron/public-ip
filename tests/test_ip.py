#! /usr/bin/env python3

import public_ip as ip

import requests
import requests_mock

from absl.testing import absltest
from absl.testing import parameterized


class GetPublicIPTest(parameterized.TestCase):
    @parameterized.named_parameters(
        {
            "testcase_name": "All URLs agree on the IP",
            "answers": {
                "https://api.ipify.org": "1.1.1.1",
                "https://checkip.amazonaws.com": "1.1.1.1",
                "https://icanhazip.com": "1.1.1.1",
                "https://ifconfig.co/ip": "1.1.1.1",
                "https://ipecho.net/plain": "1.1.1.1",
                "https://ipinfo.io/ip": "1.1.1.1",
            },
            "want": "1.1.1.1",
        },
        {
            "testcase_name": "Wrong answer from one of the URLs",
            "answers": {
                "https://api.ipify.org": "1.1.1.1",
                "https://checkip.amazonaws.com": "1.1.1.1",
                "https://icanhazip.com": "1.1.1.1",
                "https://ifconfig.co/ip": "1.1.1.1",
                "https://ipecho.net/plain": "1.1.1.1",
                "https://ipinfo.io/ip": "2.2.2.2",
            },
            "want": "1.1.1.1",
        },
        {
            "testcase_name": "Wrong answer from a minority of the URLs",
            "answers": {
                "https://api.ipify.org": "1.1.1.1",
                "https://checkip.amazonaws.com": "1.1.1.1",
                "https://icanhazip.com": "1.1.1.1",
                "https://ifconfig.co/ip": "1.1.1.1",
                "https://ipecho.net/plain": "2.2.2.2",
                "https://ipinfo.io/ip": "2.2.2.2",
            },
            "want": "1.1.1.1",
        },
        {
            "testcase_name": "One of the servers times out",
            "answers": {
                "https://api.ipify.org": "1.1.1.1",
                "https://checkip.amazonaws.com": "1.1.1.1",
                "https://icanhazip.com": "1.1.1.1",
                "https://ifconfig.co/ip": "1.1.1.1",
                "https://ipecho.net/plain": "2.2.2.2",
                "https://ipinfo.io/ip": None,
            },
            "want": "1.1.1.1",
        },
    )
    @requests_mock.Mocker()
    def test_get(self, mock, answers, want):

        for URL, reply in answers.items():
            if reply is None:
                mock.get(URL, exc=requests.exceptions.ConnectTimeout)
            else:
                mock.get(URL, text=reply)

        got = ip.get()
        self.assertEqual(got, want)


class GetPublicIPTestError(parameterized.TestCase):
    @parameterized.named_parameters(
        {
            "testcase_name": "No IP has a majority of votes",
            "answers": {
                "https://api.ipify.org": "1.1.1.1",
                "https://checkip.amazonaws.com": "2.2.2.2",
                "https://icanhazip.com": "3.3.3.3",
                "https://ifconfig.co/ip": "4.4.4.4",
                "https://ipecho.net/plain": "5.5.5.5",
                "https://ipinfo.io/ip": "6.6.6.6",
            },
            "want": ValueError,
            "regex": "tie",
        },
        {
            "testcase_name": "Tie in the returned IPs",
            "answers": {
                "https://api.ipify.org": "1.1.1.1",
                "https://checkip.amazonaws.com": "1.1.1.1",
                "https://icanhazip.com": "1.1.1.1",
                "https://ifconfig.co/ip": "2.2.2.2",
                "https://ipecho.net/plain": "2.2.2.2",
                "https://ipinfo.io/ip": "2.2.2.2",
            },
            "want": ValueError,
            "regex": "tie",
        },
        {
            "testcase_name": "Tie in the returned IPs after some servers time out",
            "answers": {
                "https://api.ipify.org": "1.1.1.1",
                "https://checkip.amazonaws.com": "2.2.2.2",
                "https://icanhazip.com": None,
                "https://ifconfig.co/ip": None,
                "https://ipecho.net/plain": None,
                "https://ipinfo.io/ip": None,
            },
            "want": ValueError,
            "regex": "tie",
        },
        {
            "testcase_name": "All servers time out",
            "answers": {
                "https://api.ipify.org": None,
                "https://checkip.amazonaws.com": None,
                "https://icanhazip.com": None,
                "https://ifconfig.co/ip": None,
                "https://ipecho.net/plain": None,
                "https://ipinfo.io/ip": None,
            },
            "want": IOError,
            "regex": "all .* failed",
        },
    )
    @requests_mock.Mocker()
    def test_get(self, mock, answers, want, regex):

        for URL, reply in answers.items():
            if reply is None:
                mock.get(URL, exc=requests.exceptions.ConnectTimeout)
            else:
                mock.get(URL, text=reply)

        with self.assertRaisesRegex(want, regex):
            got = ip.get()


if __name__ == "__main__":
    absltest.main()
