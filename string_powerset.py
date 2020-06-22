from pset_partitions import generate_powerset, string_handler
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("items_str", action="append", help="A string to" +
    "be split as multiple items, or multiple space-separated strings, " +
    "representing the set of items whose powerset is to be determined")
parser.add_argument("-q", "--quiet", dest="verbose", action="store_false")
args = parser.parse_args()

items = list(args.items_str)

if len(items) == 1:
    items = list(items[0])

ps = generate_powerset(items, subset_handler=string_handler, verbose=args.verbose)
