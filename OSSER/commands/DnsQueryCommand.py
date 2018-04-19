import sys

from OSSER.commands.AbstractCommand import AbstractCommand
from OSSER.modules.DnsQuery import DnsQuery


class DnsQueryCommand(AbstractCommand):

    class Args(AbstractCommand.AbstractArgs):
        def __init__(self, record_type: str, dns_query: str):
            self.record_type = record_type.upper()
            self.dns_query = dns_query

    def __init__(self, dns_query_module_args: DnsQuery.Args, command_args: Args):
        super().__init__()

        self.dns_query_args = dns_query_module_args
        self.command_args = command_args

    @AbstractCommand.leaf_command
    def execute(self):
        self._results = DnsQuery(args=self.dns_query_args).do_query(
                record_type=self.command_args.record_type,
                query=self.command_args.dns_query)

    # @staticmethod
    # def get_record_obj(record_name: str):
    #     records = {
    #         'A': DnsQuery.RecordTypes.A,
    #         'AAAA': DnsQuery.RecordTypes.AAAA,
    #         'SRV': DnsQuery.RecordTypes.SRV,
    #         'NS': DnsQuery.RecordTypes.NS,
    #         'CNAME': DnsQuery.RecordTypes.CNAME,
    #         'PTR': DnsQuery.RecordTypes.PTR,
    #         'SOA': DnsQuery.RecordTypes.SOA,
    #         'MX': DnsQuery.RecordTypes.MX
    #     }

    #     if record_name.upper() not in records.keys():
    #         raise NotImplementedError("This type of record is not implemented!")
    #     else:
    #        return records[record_name.upper()]


def main(args):
    command_args = DnsQueryCommand.Args(record_type=args.record_type, dns_query=args.dns_query)
    dns_args = DnsQuery.Args()

    cmd = DnsQueryCommand(dns_query_module_args=dns_args, command_args=command_args)
    cmd.execute()

    if cmd.executed:
        print("Executed successfully!")
        print("Results:")
        print(cmd.results)

if __name__ == "__main__":
    args = lambda: None
    #args.record_type = sys.argv[1]
    #args.dns_query = sys.argv[2]

    args.record_type = run_args[0]
    args.dns_query = run_args[1]

    main(args)
