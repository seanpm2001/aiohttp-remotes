from ipaddress import (ip_address, ip_network, IPv4Address,
                       IPv6Address, IPv4Network, IPv6Network)

import pytest

from aiohttp_remotes.exceptions import UntrustedIP, IncorrectIPsCount
from aiohttp_remotes.utils import parse_trusted_list, remote_ip


def test_parse_str():
    with pytest.raises(TypeError):
        parse_trusted_list('127.0.0.1')


def test_parse_non_sequence():
    with pytest.raises(TypeError):
        parse_trusted_list(1)


def test_parse_non_sequence_of_containers():
    with pytest.raises(TypeError):
        parse_trusted_list([1])


def test_parse_ipv4():
    ret = parse_trusted_list([[IPv4Address('127.0.0.1')]])
    assert ret == [[IPv4Address('127.0.0.1')]]


def test_parse_ipv6():
    ret = parse_trusted_list([[IPv6Address('::1')]])
    assert ret == [[IPv6Address('::1')]]


def test_parse_ipv4_str():
    ret = parse_trusted_list([['127.0.0.1']])
    assert ret == [[IPv4Address('127.0.0.1')]]


def test_parse_ipv6_str():
    ret = parse_trusted_list([['::1']])
    assert ret == [[IPv6Address('::1')]]


def test_parse_non_ip_item():
    with pytest.raises(ValueError):
        parse_trusted_list([['garbage']])

# --------------------- remote_ip -----------------------

def test_remote_ip_no_trusted():
    ip = ip_address('10.10.10.10')
    assert ip == remote_ip([], [ip])


def test_remote_ip_ok():
    ips = [ip_address('10.10.10.10'),
           ip_address('20.20.20.20'),
           ip_address('30.30.30.30')]
    trusted = parse_trusted_list([['10.10.0.0/16'],
                                  ['20.20.20.20']])
    assert ips[-1] == remote_ip(trusted, ips)


def test_remote_ip_not_trusted_network():
    ips = [ip_address('10.10.10.10'),
           ip_address('20.20.20.20'),
           ip_address('30.30.30.30')]
    trusted = parse_trusted_list([['40.40.0.0/16'],
                                  ['20.20.20.20']])
    with pytest.raises(UntrustedIP) as ctx:
        remote_ip(trusted, ips)
    assert ctx.value.trusted == [ip_network('40.40.0.0/16')]
    assert ctx.value.ip == ip_address('10.10.10.10')


def test_remote_ip_not_trusted_ip():
    ips = [ip_address('10.10.10.10'),
           ip_address('20.20.20.20'),
           ip_address('30.30.30.30')]
    trusted = parse_trusted_list([['40.40.40.40'],
                                  ['20.20.20.20']])
    with pytest.raises(UntrustedIP) as ctx:
        remote_ip(trusted, ips)
    assert ctx.value.trusted == [ip_address('40.40.40.40')]
    assert ctx.value.ip == ip_address('10.10.10.10')


def test_remote_ip_invalis_ips_count():
    ips = [ip_address('10.10.10.10'),
           ip_address('20.20.20.20')]
    trusted = parse_trusted_list([['40.40.40.40'],
                                  ['20.20.20.20']])
    with pytest.raises(IncorrectIPsCount) as ctx:
        remote_ip(trusted, ips)
    assert ctx.value.expected == 3
    assert ctx.value.actual == 2
