#!/usr/bin/env python

import os
import sys
import inspect
import scrapy
import scrapy.crawler
import scrapy.exporters
import re
import argparse
import logging
import fnmatch
import json
import csv
import itertools
import six
import progressbar

# cqparts
import cqparts

# cqparts_fasteners
import cqparts_fasteners
import cqparts_fasteners.screws
import cqparts_fasteners.solidtypes
from cqparts_fasteners.solidtypes.fastener_heads import find as find_head
from cqparts_fasteners.solidtypes.screw_drives import find as find_drive
from cqparts_fasteners.solidtypes.threads import find as find_thread

# ---------- Constants ----------
STORE_NAME = 'BoltDepot'
STORE_URL = 'https://www.boltdepot.com'


# ---------- Utilities ----------

def split_url(url):
    match = re.search(r'^(?P<base>.*)\?(?P<params>.*)$', url, flags=re.I)
    return (
        match.group('base'),
        {k: v for (k, v) in (p.split('=') for p in match.group('params').split('&'))}
    )

def join_url(base, params):
    return "{base}?{params}".format(
        base=base,
        params='&'.join('%s=%s' % (k, v) for (k, v) in params.items()),
    )


def utf8encoded(d):
    return {k.encode('utf-8'): v.encode('utf-8') for (k, v) in d.items()}


def in2mm(inches):
    if isinstance(inches, six.string_types):
        # valid formats:
        #   1-3/4"
        #   1/2"
        #   -5/9"
        #   1"
        #   0.34"
        #   .34"
        match = re.search(
            r'''^
                (?P<neg>-)?
                (?P<whole>(\d+)?(\.\d+)?)?
                -?
                ((?P<numerator>\d+)/(?P<denominator>\d+))?
                "
            $''',
            inches,
            flags=re.MULTILINE | re.VERBOSE,
        )
        inches = float(match.group('whole') or 0) + (
            float(match.group('numerator') or 0) / \
            float(match.group('denominator') or 1)
        )
        if match.group('neg'):
            inches *= -1

    return inches * 25.4


def mm2mm(mm):
    if isinstance(mm, six.string_types):
        mm = float(re.sub(r'mm$', '', mm))
    return mm


UNIT_FUNC_MAP = {
    'metric': mm2mm,
    'us': in2mm,
}

def unit2mm(value, unit):
    unit = unit.strip().lower()
    if unit in UNIT_FUNC_MAP:
        return UNIT_FUNC_MAP[unit](value)
    else:
        raise ValueError("invalid unit: %r" % unit)



# ---------- Scraper Spiders ----------

class BoltDepotSpider(scrapy.Spider):
    prefix = ''  # no prefix by default
    name = None  # no name, should raise exception if not set

    FEED_URI = "%(prefix)sscrape-%(name)s.json"

    @classmethod
    def get_feed_uri(cls):
        return cls.FEED_URI % {k: getattr(cls, k) for k in dir(cls)}

    @classmethod
    def get_data(cls):
        if not hasattr(cls, '_data'):
            with open(cls.get_feed_uri(), 'r') as fh:
                setattr(cls, '_data', json.load(fh))
        return cls._data

    @classmethod
    def get_data_item(cls, key, criteria=lambda i: True, cast=lambda v: v):
        # utility function to get data out of a json dict list easily
        valid_data = [cast(i[key]) for i in cls.get_data() if criteria(i)]
        assert len(valid_data) == 1, "%r" % valid_data
        return valid_data[0]


class BoltDepotProductSpider(BoltDepotSpider):

    # criteria added to every cqparts.catalogue.JSONCatalogue entry
    common_catalogue_criteria = {
        'store': STORE_NAME,
        'store_url': STORE_URL,
    }

    def parse(self, response):
        # Look for : Product catalogue table
        product_catalogue = response.css('table.product-catalog-table')
        if product_catalogue:
            for catalogue_link in product_catalogue.css('li a'):
                next_page_url = catalogue_link.css('::attr("href")').extract_first()
                yield response.follow(next_page_url, self.parse)

        # Look for : Product list table
        product_list = response.css('#product-list-table')
        if product_list:
            for product in product_list.css('td.cell-prod-no'):
                next_page_url = product.css('a::attr("href")').extract_first()
                yield response.follow(next_page_url, self.parse_product_detail)

    def parse_product_detail(self, response):
        heading = response.css('#catalog-header-title h1::text').extract_first()
        print("Product: %s" % heading)

        (url_base, url_params) = split_url(response.url)

        # details table
        detail_table = response.css('#product-property-list')
        details = {}
        for row in detail_table.css('tr'):
            key = row.css('td.name span::text').extract_first()
            value = row.css('td.value span::text').extract_first()
            if key and value:
                (key, value) = (key.strip('\n\r\t '), value.strip('\n\r\t '))
                if key and value:
                    details[key] = value

        product_data = {
            'id': url_params['product'],
            'name': heading,
            'url': response.url,
            'details': details,
        }

        # Image url
        image_url = response.css('.catalog-header-product-image::attr("src")').extract_first()
        if image_url:
            product_data.update({'image_url': image_url})

        yield product_data

    # --- cqparts catalogue building specific functions
    # These functions are kept with the spider as a means to encapsulate
    # component-specific logic.

    @classmethod
    def add_to_catalogue(cls, data, catalogue):
        criteria = cls.item_criteria(data)
        criteria.update(cls.common_catalogue_criteria)
        criteria.update({'scraperclass': cls.__name__})
        catalogue.add(
            id=data['id'],
            obj=cls.build_component(data),
            criteria=criteria,
            _check_id=False,
        )

    @classmethod
    def item_criteria(cls, data):
        return {}  # should be overridden

    @classmethod
    def build_component(cls, data):
        from cqparts_misc.basic.primatives import Cube
        return Cube()  # should be overridden

    CATALOGUE_URI = "%(prefix)s%(name)s.json"
    CATALOGUE_CLASS = cqparts.catalogue.JSONCatalogue

    @classmethod
    def get_catalogue_uri(cls):
        filename = cls.CATALOGUE_URI % {k: getattr(cls, k) for k in dir(cls)}
        return os.path.join('..', filename)

    @classmethod
    def get_catalogue(cls, **kwargs):
        return cls.CATALOGUE_CLASS(cls.get_catalogue_uri(), **kwargs)

    @classmethod
    def get_item_str(cls, data):
        return "[%(id)s] %(name)s" % data


class WoodScrewSpider(BoltDepotProductSpider):
    name = 'woodscrews'
    start_urls = [
        'https://www.boltdepot.com/Wood_screws_Phillips_flat_head.aspx',
        'https://www.boltdepot.com/Wood_screws_Slotted_flat_head.aspx',
    ]

    @classmethod
    def item_criteria(cls, data):
        criteria = {
            'name': data['name'],
            'url': data['url'],
        }
        criteria_content = [  # (<key>, <header>), ...
            ('diameter', 'Diameter:'),
            ('plating', 'Plating:'),
            ('material', 'Material:'),
        ]
        for (key, header) in criteria_content:
            value = data['details'].get(header, None)
            if value is not None:
                criteria[key] = value.lower()
        return criteria

    @classmethod
    def build_component(cls, data):
        details = data['details']

        # --- Head
        head = None
        if details['Head style:'] == 'Flat':  # countersunk
            head_diam = (  # averaged min/max
                unit2mm(details['Head diameter Min:'], details['Units:']) + \
                unit2mm(details['Head diameter Max:'], details['Units:'])
            ) / 2

            head = find_head(name='countersunk')(
                diameter=head_diam,
                bugle=False,
                raised=0,
                # TODO: details['Head angle:'] usually 82deg
            )

        else:
            raise ValueError("head style %r not supported" % details['Head style:'])

        # --- Drive
        drive = None
        if details['Drive type:'] == 'Phillips':
            # FIXME: use actual drive sizes from DataPhillipsDriveSizes to shape
            drive = find_drive(name='phillips')(
                diameter=head_diam * 0.6
            )

        elif details['Drive type:'] == 'Slotted':
            drive = find_drive(name='slot')(
                diameter=head_diam,
            )

        else:
            raise ValueError("drive type %r not supported" % details['Drive type:'])

        # --- Thread
        # Accuracy is Questionable:
        #   Exact screw thread specs are very difficult to find, so some
        #   of this is simply observed from screws I've salvaged / bought.
        thread_diam = DataWoodScrewDiam.get_data_item(
            'Decimal',
            criteria=lambda i: i['Size'] == details['Diameter:'],
            cast=lambda v: unit2mm(v, 'us'),
        )

        thread = find_thread(name='triangular')(
            diameter=thread_diam,
            pitch=thread_diam * 0.6,
        )

        # --- Build screw
        screw_length = unit2mm(details['Length:'], details['Units:'])
        screw = cqparts_fasteners.screws.Screw(
            drive=drive,
            head=head,
            thread=thread,

            length=screw_length,
            neck_length=screw_length * 0.25,
            tip_length=1.5 * thread_diam,
        )

        return screw


class BoltSpider(BoltDepotProductSpider):
    name = 'bolts'
    start_urls = [
        'https://www.boltdepot.com/Hex_bolts_2.aspx',
        'https://www.boltdepot.com/Metric_hex_bolts_2.aspx',
    ]

class NutSpider(BoltDepotProductSpider):
    name = 'nuts'
    start_urls = [
        'https://www.boltdepot.com/Hex_nuts.aspx',
        'https://www.boltdepot.com/Square_nuts.aspx',
        'https://www.boltdepot.com/Metric_hex_nuts.aspx',
    ]

class ThreadedRodSpider(BoltDepotProductSpider):
    name = 'threaded-rods'
    start_urls = [
        'https://www.boltdepot.com/Threaded_rod.aspx',
        'https://www.boltdepot.com/Metric_threaded_rod.aspx',
    ]


SPIDERS = [
    WoodScrewSpider,
    BoltSpider,
    NutSpider,
    ThreadedRodSpider,
]
SPIDER_MAP = {
    cls.name: cls
    for cls in SPIDERS
}


class GrowingList(list):
    """
    A list that will automatically expand if indexed beyond its limit.
    (the list equivalent of collections.defaultdict)
    """

    def __init__(self, *args, **kwargs):
        self._default_type = kwargs.pop('default_type', lambda: None)
        super(GrowingList, self).__init__(*args, **kwargs)

    def __getitem__(self, index):
        if index >= len(self):
            self.extend([self._default_type() for i in range(index + 1 - len(self))])
        return super(GrowingList, self).__getitem__(index)

    def __setitem__(self, index, value):
        if index >= len(self):
            self.extend([self._default_type() for i in range(index + 1 - len(self))])
        super(GrowingList, self).__setitem__(index, value)


class BoltDepotDataSpider(BoltDepotSpider):

    @staticmethod
    def table_data(table):
        # Pull data out of a table into a 2d list.
        # Merged Cells:
        #   any merged cells (using rowspan / colspan) will have duplicate
        #   data over each cell.
        #   "merging cells does not a database make" said me, just now

        def push_data(row, i, val):
            # push data into next available slot in the given list
            # return the index used (will be >= i)
            assert isinstance(row, GrowingList), "%r" % row
            assert val is not None
            try:
                while row[i] is not None:
                    i += 1
            except IndexError:
                pass
            row[i] = val
            return i

        data = GrowingList(default_type=GrowingList)  # nested growing list
        header_count = 0
        for (i, row) in enumerate(table.css('tr')):
            j = 0
            is_header_row = True
            for cell in row.css('th, td'):
                # cell data
                value = cell.css('::text').extract_first()
                if value is None:
                    value = ''
                value = value.rstrip('\r\n\t ')
                rowspan = int(cell.css('::attr("rowspan")').extract_first() or 1)
                colspan = int(cell.css('::attr("colspan")').extract_first() or 1)
                # is header row?
                if cell.root.tag != 'th':
                    is_header_row = False
                # populate data (duplicate merged content)
                j = push_data(data[i], j, value)
                for di in range(rowspan):
                    for dj in range(colspan):
                        data[i + di][j + dj] = value
                j += 1
            if is_header_row:
                header_count += 1

        return (data, header_count)

    def parse(self, response):
        table = response.css('table.fastener-info-table')
        (data, header_count) = self.table_data(table)

        header = data[header_count - 1]  # last header row
        for row in data[header_count:]:
            row_data = dict(zip(header, row))
            if any(v for v in row_data.values()):
                # don't yield if there's no data
                yield row_data


class DataWoodScrewDiam(BoltDepotDataSpider):
    name = 'd-woodscrew-diam'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Wood-Screws/Wood-Screw-Diameter.aspx',
    ]

class DataUSBoltThreadLen(BoltDepotDataSpider):
    name = 'd-us-bolt-thread-len'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Bolts/US-Thread-Length.aspx',
    ]

class DataUSThreadPerInch(BoltDepotDataSpider):
    name = 'd-us-tpi'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Measuring/US-TPI.aspx',
    ]

class DataMetricThreadPitch(BoltDepotDataSpider):
    name = 'd-met-threadpitch'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Measuring/Metric-Thread-Pitch.aspx',
    ]

class DataMetricBoltHeadSize(BoltDepotDataSpider):
    name = 'd-met-boltheadsize'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Bolts/Metric-Bolt-Head-Size.aspx',
    ]

class DataPhillipsDriveSizes(BoltDepotDataSpider):
    name = 'd-drivesizes-phillips'
    start_urls = [
        'https://www.boltdepot.com/fastener-information/Driver-Bits/Phillips-Driver-Sizes.aspx',
    ]


METRICS_SPIDERS = [
    DataWoodScrewDiam,
    DataUSBoltThreadLen,
    DataUSThreadPerInch,
    DataMetricThreadPitch,
    DataMetricBoltHeadSize,
    DataPhillipsDriveSizes,
]

# ---------- Command-line Arguments Parser ----------
DEFAULT_PREFIX = os.path.splitext(os.path.basename(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
))[0] + '-'

parser = argparse.ArgumentParser(
    description='Build Bolt Depot catalogue by crawling their website',
    epilog="""
Actions:
    scrape  scrape product details from website
    csv     convert scraped output to csv [optional]
    build   builds catalogue from scraped data

Note: Actions will always be performed in the order shown above,
      even if they're not listed in that order on commandline.
    """,
    formatter_class=argparse.RawTextHelpFormatter,
)

VALID_ACTIONS = set(['scrape', 'csv', 'build'])
def action_type(value):
    value = value.lower()
    if value not in VALID_ACTIONS:
        raise argparse.ArgumentError()
    return value

parser.add_argument(
    'actions', metavar='action', type=action_type, nargs='*',
    help='action(s) to perform'
)

# Scraper arguments
parser.add_argument(
    '--prefix', '-p', dest='prefix', default=DEFAULT_PREFIX,
    help="scraper file prefix (default: '%s')" % DEFAULT_PREFIX,
)

parser.add_argument(
    '--onlymetrics', '-om', dest='onlymetrics',
    action='store_const', const=True, default=False,
    help="if set, when scraping, only metrics data is scraped"
)

# Catalogues
parser.add_argument(
    '--list', '-l', dest='list',
    default=False, action='store_const', const=True,
    help="list catalogues to build",
)

def catalogues_list_type(value):
    catalogues_all = set(SPIDER_MAP.keys())
    catalogues = set()
    for filter_str in value.split(','):
        catalogues |= set(fnmatch.filter(catalogues_all, filter_str))
    return sorted(catalogues)

parser.add_argument(
    '--catalogues', '-c', dest='catalogues',
    type=catalogues_list_type, default=catalogues_list_type('*'),
    help="csv list of catalogues to act on",
)

args = parser.parse_args()

BoltDepotSpider.prefix = args.prefix


# list catalogues & exit
if args.list:
    for name in args.catalogues:
        print(name)
    exit(0)

# no actions, print help & exit
if not args.actions:
    parser.print_help()
    exit(1)


# ----- Start Crawl -----

if 'scrape' in args.actions:
    print("----- Scrape: %s (+ metrics)" % (', '.join(args.catalogues)))

    # --- Clear feed files
    feed_names = []
    if not args.onlymetrics:
        feed_names += args.catalogues
    feed_names += [cls.name for cls in METRICS_SPIDERS]

    for name in feed_names:
        feed_filename = BoltDepotSpider.FEED_URI % {
            'prefix': args.prefix, 'name': name,
        }
        if os.path.exists(feed_filename):
            os.unlink(feed_filename)  # remove feed file to populate from scratch


    # --- Create Crawlers
    process = scrapy.crawler.CrawlerProcess(
        settings={
            'LOG_LEVEL': logging.INFO,
            'FEED_FORMAT': "json",
            'FEED_URI': BoltDepotSpider.FEED_URI,
        },
    )

    # product crawlers
    if not args.onlymetrics:
        for name in args.catalogues:
            process.crawl(SPIDER_MAP[name])
    # metrics crawlers
    for metrics_spider in METRICS_SPIDERS:
        process.crawl(metrics_spider)

    # --- Start Scraping
    process.start()


# ----- Convert to CSV -----
# Conversion of json files to csv is optional, csv's are easy to open
# in a 3rd party application to visualise the data that was scraped.

if 'csv' in args.actions:

    def flatten_dict(dict_in):
        # flatten nested dicts using '.' separated keys
        def inner(d, key_prefix=''):
            for (k, v) in d.items():
                if isinstance(v, dict):
                    for (k1, v1) in inner(v, k + '.'):
                        yield (k1, v1)
                else:
                    yield (key_prefix + k, v)

        return dict(inner(dict_in))

    for cls in itertools.chain([SPIDER_MAP[n] for n in args.catalogues], METRICS_SPIDERS):
        print("----- CSV: %s" % cls.name)
        feed_json = cls.get_feed_uri()
        feed_csv = "%s.csv" % os.path.splitext(feed_json)[0]
        print("   %s --> %s" % (feed_json, feed_csv))
        data = cls.get_data()

        # pull out all possible keys to build header row
        headers = set(itertools.chain(*[
            tuple(str(k) for (k, v) in flatten_dict(row).items())
            for row in data
        ]))

        # Write row by row
        with open(feed_csv, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            for rowdata in data:
                writer.writerow(utf8encoded(flatten_dict(rowdata)))


# ----- Build Catalogues -----


if 'build' in args.actions:
    for name in args.catalogues:
        cls = SPIDER_MAP[name]
        print("----- Build: %s" % name)
        catalogue_file = os.path.join(
            '..', "%s.json" % os.path.splitext(cls.get_feed_uri())[0]
        )
        catalogue = cls.get_catalogue(clean=True)
        data = cls.get_data()

        sys.stdout.flush()  # make sure prints come through before bar renders
        bar = progressbar.ProgressBar()

        for item_data in bar(data):
            try:
                cls.add_to_catalogue(item_data, catalogue)
            except Exception as e:
                print("couldn't add: %s" % cls.get_item_str(item_data))
                print(e)
                sys.stdout.flush()