import os
from django.conf import settings
from datetime import date, timedelta
from market.models import Purchased, Category

REPORT_CHOICES = [(0, 'Products'), (1, 'Cities'), (2, 'Prices'), (3, 'Categories'), (4, 'Time')]
REPORT_TIME_PERIODS = ['Days', 'Months', 'Years']
REPORT_PRICE_SLICES = [10, 30, 50, 100, 500]

QUERY_TEMPLATE = '''
    SELECT ph.ID, ph.quantity {select}
    FROM market_Purchased ph
    INNER JOIN market_Product p ON p.id = ph.product_id
    INNER JOIN market_Category c ON c.id = p.category_id
    {join}
    WHERE
        ph.is_sent = 1 AND
        ph.date >= %s AND
        ph.date <= %s AND
        c.path LIKE %s
    {order}
'''

SQL_PIECES = [
    #(select, join, order)
    ('p.name AS product_name', [], 'p.name'), #products
    (
        'a.city', [
            ('market_Basket b', 'b.id = ph.basket_id'),
            (
                'market_Address a', (
                'a.user_id = b.user_id OR ' +
                'a.session_id = b.session_id'
            )),
        ], 'a.city'
    ), #cities
    ('p.price', [], 'p.price'), #prices
    ('c.name AS category_name, c.path', [], 'c.path'), #categories
    ('ph.date', [], 'ph.date'), #time
    ('', [], ''), #zero: for headers
]

def get_report_name(index):
    return os.path.join(settings.MEDIA_ROOT, 'pdf', 'report' + index + '.pdf')


def set_not_empty_value(param, default):
    return param or default


def get_query(template, row, col):
    row_sql = SQL_PIECES[row]
    col_sql = SQL_PIECES[col]

    def compose_line(index):
        line = ''
        if row_sql[index]:
            line += ', {0}'.format(row_sql[index])
        if col_sql[index]:
            line += ', {0}'.format(col_sql[index])
        return line

    select = compose_line(0)

    def compose_joins(join_list):
        return ' '.join(['INNER JOIN {0} ON {1}'.format(join[0], join[1]) for join in join_list])

    joins = compose_joins(row_sql[1]) + compose_joins(col_sql[1])
    order_by = compose_line(2).replace(',', 'ORDER BY', 1)
    return template.format(select=select, join=joins, order=order_by)


def check_product(current, header, param):
    return current.product_name == header


def check_city(current, header, param):
    return current.city == header


def check_price(current, header, param):
    return current.price <= header


def check_category(current, header, param):
    #print header[1]
    #print current.path
    #print current.category_name
    return str(header[1]) in current.path.split('.')


def check_time(current, header, param):
    if param == 0:
        return current.date.day == header.day
    elif param == 1:
        return current.date.month == header.month
    return current.date.year == header.year


CHECK_FOR_CHANGE = [check_product, check_city, check_price, check_category, check_time]


def make_product_header(param, start_date, end_date, root_cat_path):
    ds = Purchased.objects.raw(get_query(QUERY_TEMPLATE, 0, 5), [start_date, end_date, root_cat_path + '%'])
    return sorted(list(set([item.product_name for item in ds])))


def output_product_header(param, element):
    return element


def make_city_header(param, start_date, end_date, root_cat_path):
    ds = Purchased.objects.raw(get_query(QUERY_TEMPLATE, 1, 5), [start_date, end_date, root_cat_path + '%'])
    return sorted(list(set(item.city for item in ds)))


def output_city_header(param, element):
    return element


def make_price_header(param, start_date, end_date, root_cat_path):
    p = REPORT_PRICE_SLICES[param]
    ds = Purchased.objects.raw(get_query(QUERY_TEMPLATE, 2, 5), [start_date, end_date, root_cat_path + '%'])
    return range(p, (ds[-1].price / p + 1) * p + 1, p) if list(ds) else []


def output_price_header(param, element):
    return '{0}-{1}'.format(element - REPORT_PRICE_SLICES[param] + 1, element)


def make_category_header(param, start_date, end_date, root_cat_path):
    root_cats = Category.objects.filter(depth=str(param), path__startswith=root_cat_path).order_by('id')
    if not root_cats:
        root_cats = [Category.objects.get(path=root_cat_path)]
    return [(item.name, item.id) for item in root_cats]


def output_category_header(param, element):
    return element[0]


def make_time_header(param, start_date, end_date, root_cat_path):
    l = []
    #hiding unneccessary data
    ds = start_date.day if param < 1 else 1
    de = end_date.day if param < 1 else 1
    ms = start_date.month if param < 2 else 1
    me = end_date.month if param < 2 else 1
    ys = start_date.year
    ye = end_date.year
    sd = date(ys, ms, ds)
    ed = date(ye, me, de)

    def move(d):
        if param == 0:
            return d + timedelta(1)
        elif param == 1:
            return date(d.year, d.month + 1, d.day)
        return date(d.year + 1, d.month, d.day)

    while sd <= ed:
        l.append(sd)
        sd = move(sd)
    return l


def output_time_header(param, element):
    format = '%Y' if param == 2 else '%m.%Y' if param == 1 else '%d.%m.%Y'
    return element.strftime(format)


MAKE_HEADER = [make_product_header, make_city_header, make_price_header, make_category_header, make_time_header]
OUTPUT_HEADER = [output_product_header, output_city_header, output_price_header, output_category_header, output_time_header]
