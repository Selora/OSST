import sys
import time
import json
from typing import Iterable

from OSSER.commands.AbstractCommand import AbstractCommand
from OSSER.modules.BingSearch import BingSearch


class BingLinkedInScraperCommand(AbstractCommand):

    class Args(AbstractCommand.AbstractArgs):

        def __init__(self,
                     company: str,
                     location: str,
                     additional_query_args
                     ):
            self.company = company
            self.location = location
            self.additional_query = additional_query_args

    def __init__(self,
                 bing_search_module_args: BingSearch.Args,
                 command_args: Args):

        super().__init__()
        self.command_args = command_args
        self.bing_search_module_args = bing_search_module_args

    @AbstractCommand.leaf_command
    def execute(self):
        search_term = 'site:www.linkedin.com/in intitle:"{company}" "Location {location}" {add_query}'.format(
            company=self.command_args.company,
            location=self.command_args.location,
            add_query=self.command_args.additional_query)

        self._results = BingSearch(args=self.bing_search_module_args).do_search(
            search_term=search_term
        )

if __name__ == '__main__':
    if len(sys.argv) != 5:
        api_key = input("api:")
        company = input("company:")
        location = input("location:")
        additional_query_args = input("additional_query:")
    else:
        api_key = sys.argv[1]
        company = sys.argv[2]
        location = sys.argv[3]
        additional_query_args = sys.argv[4]

    bing_args = BingSearch.Args(bing_api_key=api_key)
    command_args = BingLinkedInScraperCommand.Args(company=company,
                                                   location=location,
                                                   additional_query_args=additional_query_args)

    cmd = BingLinkedInScraperCommand(bing_search_module_args=bing_args,
                                     command_args=command_args)
    print("Searching...")
    cmd.execute()
    if cmd.executed:
        print("Executed successfully!")
        print("Results ({}):".format(len(cmd.results)))

        filename = "linkedin_{company}_{location}_{timestamp}.json".format(
            company=company.replace(' ', '-'),
            location=location.replace(' ', '-'),
            timestamp=str(int(time.time()))

        )

        print("Storing results in ({}):".format(filename))
        with open(filename, 'w') as f:
            f.write(json.dumps(cmd.results))

