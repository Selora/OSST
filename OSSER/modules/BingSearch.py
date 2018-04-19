import sys
from typing import Iterable

from OSSER.modules.AbstractModule import AbstractModule
from py_ms_cognitive import PyMsCognitiveWebSearch as MsWeb


class BingSearch(AbstractModule):

    class Args(AbstractModule.AbstractArgs):
        def __init__(self,
                     bing_api_key: str = '',
                     limit: int = 50,
                     offset: int = None,
                     find_all: bool = True,
                     max_queries: int = 15):
            self.bing_api_key = bing_api_key
            self.limit = limit
            self.offset = offset
            self.find_all = find_all
            self.max_queries = max_queries

    def __init__(self, args: Args):
        self.args = args
        self.query_count = 0

    @staticmethod
    def _parse_results(bing_search_results: Iterable):
        return [{
            'name': x.name,
            'description': x.description,
            'url': x.url} for x in bing_search_results]

    def do_search(self, search_term):
        """ Perform paged searches while we find new FQDN """

        print(search_term)

        custom_params = {'safeSearch': 'Off'}
        if self.args.offset:
            custom_params['offset'] = self.args.offset

        search_service = MsWeb(self.args.bing_api_key, query=search_term,
                               custom_params=custom_params)

        bing_results = search_service.search(limit=self.args.limit, format='json')
        self.query_count += 1
        results = BingSearch._parse_results(bing_results)

        # Find all the things until we can't find new URLs anymore
        # We have the first result set, do a new search and compare it to the previous one.
        if self.args.find_all and self.query_count < self.args.max_queries:

            result_set = set(
                    (x["url"] for x in results)
            )

            # Internal py_ms_cognitive object deals with the offset
            bing_results = search_service.search(limit=self.args.limit, format='json')
            self.query_count += 1
            new_results = BingSearch._parse_results(bing_results)

            new_result_set = set(
                    (x["url"] for x in new_results)
            )

            # New result contains everything already inside result_set
            while not result_set.issuperset(new_result_set):

                results += new_results

                if self.query_count < self.args.max_queries:
                    # Internal py_ms_cognitive object deals with the offset
                    bing_results = search_service.search(limit=self.args.limit, format='json')
                    self.query_count += 1
                    new_results = BingSearch._parse_results(bing_results)

                    new_result_set = set(
                            (tuple(x) for x in results)
                    )


                else:
                    # Do not perform a search, but previous results were added
                    # Stop looping, exit
                    break

        return results


if __name__ == '__main__':
    args = BingSearch.Args(bing_api_key=sys.argv[1],
                           find_all=True)
    bir = BingSearch(args)
    #if len(sys.argv) <= 2:
    #    search_term = input("SearchTerm:")
    #else:
    #    search_term = sys.argv[2]

    search_results = bir.do_search(search_term)

    print("Number of queries: {}".format(bir.query_count))
    print("Results (){}".format(len(search_results)))
    print()
    for x in search_results:
        for k, v in x.items():
            print(k, ":\t", v)

