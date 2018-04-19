from enum import Enum
from typing import Iterable

from dns.rdtypes.ANY import NS as dns_NS, \
    CNAME as dns_CNAME,\
    PTR as dns_PTR, \
    SOA as dns_SOA,\
    MX as dns_MX
from dns.rdtypes.IN import A as dns_A,\
    AAAA as dns_AAAA,\
    SRV as dns_SRV

from dns.resolver import Resolver, NXDOMAIN
import dns.reversename

from OSSER.modules.AbstractModule import AbstractModule


class DnsQuery(AbstractModule):

    # If we decide to change lib after...it's easier that way I guess?
    class RecordTypes(Enum):
        A = dns_A
        AAAA = dns_AAAA
        SRV = dns_SRV
        NS = dns_NS
        CNAME = dns_CNAME
        PTR = dns_PTR
        SOA = dns_SOA
        MX = dns_MX

    class Args(AbstractModule.AbstractArgs):
        def __init__(self, nameservers: Iterable[str] = None, ttl: int = 3, timeout: int = 3):
            self.ttl = ttl
            self.nameservers = nameservers
            self.timeout = timeout

    def __init__(self, args: Args):
        self.args = args

        if self.args.nameservers:
            self._resolver = Resolver(configure=False)
            self._resolver.nameservers = args.nameservers
        else:
            self._resolver = Resolver(configure=True)

        self._resolver.timeout = self.args.timeout
        self._resolver.lifetime = self.args.ttl

    def do_query(self, query: str, record_type: str = 'A'):
        # Testing purposes
        # return 'dig -t {} @{} {}'.format(record_type._name_, self.args.nameservers[0], query)

        if record_type.upper() == 'PTR':
            # Get canonical ptr name
            query = dns.reversename.from_address(query)

        # print('dig -t {} @{} {}'.format(record_type, self._resolver.nameservers[0], query))

        try:
            results = [x for x in self._resolver.query(qname=query, rdtype=record_type, raise_on_no_answer=False)]
        except NXDOMAIN as err:
            results = []

        return results
