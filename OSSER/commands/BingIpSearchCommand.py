import sys

from OSSER.commands.AbstractCommand import AbstractCommand
from OSSER.modules.BingSearch import BingSearch


class BingIpSearchCommand(AbstractCommand):

    class Args(AbstractCommand.AbstractArgs):
        def __init__(self, ip_address):
            self.ip_address = ip_address

    def __init__(self,
                 bing_search_module_args: BingSearch.Args = None,
                 command_args: Args = None,
                 ):
        super().__init__()

        self.bing_search_module_args = bing_search_module_args
        self.command_args = command_args

    @AbstractCommand.leaf_command
    def execute(self):
        self._results = BingSearch(args=self.bing_search_module_args).do_search(search_term='ip:'+self.command_args.ip_address)


if __name__ == '__main__':
    command_args = BingIpSearchCommand.Args(ip_address=sys.argv[2])
    bing_args = BingSearch.Args(bing_api_key=sys.argv[1])

    cmd = BingIpSearchCommand(bing_search_module_args=bing_args, command_args=command_args)
    cmd.execute()

    if cmd.executed:
        print("Executed successfully!")
        print("Results:")
        print(cmd.results)
