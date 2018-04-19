import sys
from urllib.parse import urlparse
from typing import Iterable

import OSSER.core.helpers as helpers
from OSSER.commands.AbstractCommand import AbstractCommand
from OSSER.commands.DnsReconCommand import DnsReconCommand
from OSSER.commands.BingIpSearchCommand import BingIpSearchCommand
from OSSER.modules.DnsQuery import DnsQuery
from OSSER.modules.BingSearch import BingSearch


class BingIpReconCommand(AbstractCommand):

    class Args(AbstractCommand.AbstractArgs):
        def __init__(self, ip_addresses: Iterable[str]):
            self.ip_addresses = set(ip_addresses)

    def __init__(self,
                 dns_query_module_args: DnsQuery.Args,
                 bing_serch_module_args: BingSearch.Args,
                 command_args: Args):
        super().__init__()

        self.command_args = command_args
        self.dns_query_module_args = dns_query_module_args
        self.bing_search_module_args = bing_serch_module_args

        for ip in self.command_args.ip_addresses:
            bing_ip_search = BingIpSearchCommand(
                    command_args=BingIpSearchCommand.Args(ip_address=ip),
                    bing_search_module_args=self.bing_search_module_args
            )

            self.add(bing_ip_search)

    @AbstractCommand.composite_command
    def execute(self):

        for child in self.children():
            child.execute()

        bing_results = [res for cmd in self.children()
                        if cmd.results
                        for res in cmd.results]

        found_fqdn = helpers.extract_fqdn_from_bing_results(bing_results)
        dns_recon_cmd = DnsReconCommand(
                dns_query_module_args=self.dns_query_module_args,
                command_args=DnsReconCommand.Args(
                        ip_addresses=[],
                        fully_qualified_domain_names=found_fqdn
                )
        )




        print(found_fqdn)


def print_children(command: AbstractCommand):
    """
    Depth first print (print leafs up to the top)
    """
    for c in command.children():
        print_children(c)

    print(command.command_args)


def main(args):
    command_args = BingIpReconCommand.Args(ip_addresses=args.ip_addresses)
    dns_args = DnsQuery.Args()
    bing_args = BingSearch.Args(bing_api_key=args.api_key)

    cmd = BingIpReconCommand(dns_query_module_args=dns_args,
                             bing_serch_module_args=bing_args,
                             command_args=command_args)
    cmd.execute()

    if cmd.executed:
        print("Executed successfully!")
        print("Results:")
        print(cmd.results)
        print_children(cmd)


if __name__ == "__main__":
    args = lambda: None
    #args.record_type = sys.argv[1]
    #args.dns_query = sys.argv[2]

    args.ip_addresses = run_args
    args.api_key = sys.argv[1]

    main(args)
