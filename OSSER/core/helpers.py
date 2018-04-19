from typing import Iterable
from urllib.parse import urlparse

def expand_fqdn(fqdn: str):
    """
    Moaaar recursive fuckery =D
    :param fqdn: A fully qualified domain name (this.is.sparta.com)
    :return: A tuple of fqdns based on the original (sparta.com, is.sparta.com, this.is.sparta.com)
    """

    zones = str(fqdn).split('.')
    if len(zones) == 2:
        return ['.'.join((zones.pop(0), zones.pop(0)))]
    else:
        new_fqdn = '.'.join((x for x in zones[1:]))
        zones.pop(0)
        return expand_fqdn(new_fqdn) + [fqdn]


def extract_fqdn_from_bing_results(bing_results: Iterable[dict]):
    return set([urlparse(x['url']).netloc for x in bing_results])