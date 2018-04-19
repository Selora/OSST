import sys
from typing import Iterable

import OSSER.core.helpers as helpers
from OSSER.commands.AbstractCommand import AbstractCommand
from OSSER.commands.DnsQueryCommand import DnsQueryCommand
from OSSER.modules.DnsQuery import DnsQuery


class DnsReconCommand(AbstractCommand):
    """
    This class is used to perform a two-way lookup of "IP <-> FQDN" until the results are stabilized:
    tl;dr:
    dig -x ip_list >> fqdn_list
    dig -t A fqdn_list >> ip_list
    dig -x ip_list >> fqdn_list
    (. . .)
    -> Stops when results are stable (No new IP or FQDN from an iteration)

    Moar complex explanation:
        Tx: task that could be in parallel

        T1: Do a forward query (A record) for all FQDN in scope
        T2: Do a reverse query (PTR record) for all IPs in scope

        After T1 and T2 are finished,
        While ( T1.resulting_ips != T2.queried_ips OR
                T1.queried_fqdns are not superset or T2.resulting_fqdn )
            T2 += T1.resulting_ips
            T1 += T2.resulting_fqdns
            Restart T1,T2

        That way, if PRT query yields a new fqdn, we feed it to A query, and vice-versa

        Note: The "while" is performed with recursion and composite pattern, see self.execute()
            If it's not stable after an iteration, this command will create a new command as a child

    This would catch
        -misconfigured PTR records (ex. IP changed, but PTR still points to old IP)
        -IPs not deemed in scope (but that should be)
        -FQDNs not deemed in scope (but that should be)

    """

    class Args(AbstractCommand.AbstractArgs):
        def __init__(self, ip_addresses: Iterable[str], fully_qualified_domain_names: Iterable[str]):
            self.ip_addresses = set(ip_addresses)
            # Getting all zones as well: admin.test.com -> (admin.test.com, test.com)
            # The sum part flattens the list (each calls returns a list of possible domains,
            # otherwise its a list of list)
            self.fully_qualified_domain_names = set(sum([helpers.expand_fqdn(x)
                                                         for x in fully_qualified_domain_names], []))

    def __init__(self,
                 dns_query_module_args: DnsQuery.Args = None,
                 command_args: Args = None):
        super().__init__()

        self.command_args = command_args
        self.dns_query_module_args = dns_query_module_args


        # Generate sub-commands for every IPs and FQDNs
        for ip in self.command_args.ip_addresses:
            ip_reverse_query = DnsQueryCommand(dns_query_module_args=self.dns_query_module_args,
                                               command_args=DnsQueryCommand.Args(record_type='PTR', dns_query=ip))
            self.add(ip_reverse_query)

        for fqdn in self.command_args.fully_qualified_domain_names:
            dns_query = DnsQueryCommand(dns_query_module_args=self.dns_query_module_args,
                                        command_args=DnsQueryCommand.Args(record_type='A', dns_query=fqdn))

            self.add(dns_query)

    @AbstractCommand.composite_command
    def execute(self):
        """
        This one is a recursive mindfuck, but it's awesome!
        First, we execute all the children ourselves.
        If the condition to stop is not met, we build a new composite command, add it to childrens, return.
        The decorator will take care of executing the "new" children we just append.

        That way, we have complete tracability over what commands were executed in order to find something.
            Ex. google.com -> 8.8.8.8 was discovered in the third pass.
            We can find that by getting its parents.
                (Which IP lead to google.com previously?)

        :return:
        """

        # print("Executing the {} children of {}".format(len([x for x in self.children() if not x.executed]), self))
        for child in self.children():
            child.execute()

        # Get all the FQDN-> IPs
        ip_results = set([res.address for cmd in self.children()
                      if cmd.command_args.record_type == 'A' # Get all fqdn -> ip cmd
                      and cmd.results                        # If results are not empty
                      for res in cmd.results])

        # The [:-1] is to skip the last '.' and get a usable fqdn (test.fqdn.com.)
        fqdn_results = [res.to_text()[:-1] for cmd in self.children()
                        if cmd.command_args.record_type == 'PTR'
                        and cmd.results
                        for res in cmd.results]

        # Get all possible new FQDN
        # 'sum' is to flatten list of list (results of expand_fqdn is list)
        fqdn_results = set(sum([helpers.expand_fqdn(x) for x in fqdn_results], []))

        # Getting all previously queried IPs using command args
        previous_ip = set([cmd.command_args.dns_query for cmd in self.children()
                       if cmd.command_args.record_type == 'PTR'])

        # Getting all previously queried FQDNs using command args
        previous_fqdn = set([cmd.command_args.dns_query for cmd in self.children()
                       if cmd.command_args.record_type == 'A'])

        if ip_results != previous_ip or not \
            previous_fqdn.issuperset(fqdn_results):

            new_command = DnsReconCommand(
                    command_args=DnsReconCommand.Args(ip_addresses=ip_results.difference(previous_ip),
                                                      fully_qualified_domain_names=fqdn_results.difference(previous_fqdn)),
                    dns_query_module_args=self.dns_query_module_args)

            # Adding already executed children so we can keep a track of previous commands run
            for c in self.children():
                new_command.add(c)

            self.add(new_command)

    @property
    def results(self):
        """
        Get a dict of ip-fqdn by crawling depth-first throught childrens
        :return:
        """
        results = {}
        for c in self.children():
            # We know the only two types of commands in this composite are either
            # another DnsReconCommand or some DnsQueryCommand

            # This is sketchy...
            if type(c) is DnsReconCommand:
                results += c.results
            else:
                pass




def print_children(command: AbstractCommand):
    """
    Depth first print (print leafs up to the top)
    """
    for c in command.children():
        print_children(c)

    print(command, command.command_args)

def main(args):
    command_args = DnsReconCommand.Args(ip_addresses=args.ip_addresses,
                                        fully_qualified_domain_names=args.fully_qualified_domain_names)
    dns_args = DnsQuery.Args()

    cmd = DnsReconCommand(dns_query_module_args=dns_args, command_args=command_args)
    cmd.execute()

    if cmd.executed:
        print("Executed successfully!")
        print("Results:")
        print(cmd.results)
        print_children(cmd)


run_args = [

]


if __name__ == "__main__":
    args = lambda: None
    #args.record_type = sys.argv[1]
    #args.dns_query = sys.argv[2]

    args.ip_addresses = run_args[0]
    args.fully_qualified_domain_names = run_args[1]

    main(args)
