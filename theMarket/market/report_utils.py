import datetime
from market.models import Purchased, Category

REPORT_CHOICES = [(0, 'Products'), (1, 'Cities'), (2, 'Prices'), (3, 'Categories'), (4, 'Time')]
REPORT_TIME_PERIODS = ['Days', 'Months', 'Years']
REPORT_PRICE_SLICES = [10, 30, 50, 100, 500]

QUERY_TEMPLATE = '''
    SELECT ph.ID, SUM(ph.quantity) AS quantity_sum {select}
    FROM market_Purchased ph
    INNER JOIN market_Product p ON p.id = ph.product_id
    INNER JOIN market_Category c ON c.id = p.category_id
    {join}
    WHERE
        ph.is_sent = 1 AND
        ph.date >= %s AND
        ph.date <= %s AND
        c.path LIKE %s
    {group}
    {order}
'''

SQL_PIECES = [
    #(select, join, group, order)
    ('p.name AS product_name', '', 'p.id', 'p.name'), #products
    (
        'a.city', [
            ('market_Basket b', 'b.id = ph.basket_id'),
            (
                'market_Address a', (
                'a.user_id = b.user_id OR ' +
                'a.session_id = b.session_id'
            )),
        ], 'a.city', 'a.city'
    ), #cities
    ('p.price', '', '', 'p.price DESC'), #prices
    ('c.name AS category_name, c.path', '', '', 'c.path'), #categories
    ('ph.date', '', 'ph.date', 'ph.date'), #time
    ('', '', '', ''), #zero: for headers
]


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
        joins = ''
        if join_list:
            for join in join_list:
                joins += 'INNER JOIN {0} ON {1} '.format(join[0], join[1])
        return joins

    joins = compose_joins(row_sql[1]) + compose_joins(col_sql[1])
    group_by = compose_line(2).replace(',', 'GROUP BY', 1)
    order_by = compose_line(3).replace(',', 'ORDER BY', 1)
    return template.format(select=select, join=joins, group=group_by, order=order_by)


def check_product(current, header, param):
    return current['product_name'] == previous


def check_city(current, header, param):
    return current['city'] == previous


def check_price(current, header, param):
    return current['price'] <= header


def check_category(current, header, param):
    r = current['path'].find('.' + str(header[1]) + '.') != -1 or
        current['path'].startswith(str(header[1]) + '.') or
        current['path'].endswith('.' + str(header[1]))
    return r


def check_time(current, header, param):
    #not sure about convertion of queryset value to datetime.date
    if param == 0:
        return current['date'].day == header.day
    elif param == 1:
        return current['date'].month == header.month
    else:
        return current['date'].year == header.year


CHECK_FOR_CHANGE = [check_product, check_city, check_price, check_category, check_time]


def make_grouped_header(ds, field_name):
    l = []
    for item in ds:
        if l[-1] != item[field_name]:
            l.append(item[field_name])
    return l


def make_product_header(param, start_date, end_date, root_cat_path):
    ds = Purchased.objects.raw(get_query(QUERY_TEMPLATE, 0, 5), [start_date, end_date, root_cat_path + '%'])
    return make_grouped_header(ds, 'product_name')


def make_city_header(param, start_date, end_date, root_cat_path):
    ds = Purchased.objects.raw(get_query(QUERY_TEMPLATE, 1, 5), [start_date, end_date, root_cat_path + '%'])
    return make_grouped_header(ds, 'city')


def make_price_header(param, start_date, end_date, root_cat_path):
    l = []
    ds = Purchased.objects.raw(get_query(QUERY_TEMPLATE, 2, 5), [start_date, end_date, root_cat_path + '%'])
    if ds:
        l = range(0, (ds[0]['price'] / param + 1) * param, param)
    return l


def make_category_header(param, start_date, end_date, root_cat_path):
    l = []
    root_cats = Category.objects.filter(depth=param, path__startswith=root_cat_path).order_by(id)
    if not root_cats:
        root_cats = Category.objects.get(path=root_cat_path)
    for item in root_cats:
        l.append(item['name'], item['ID'])
    return l


def make_time_header(param, start_date, end_date, root_cat_path):
    l = []
    #hiding unneccessary data
    ds = start_date.day if param < 1 else 1
    de = end_date.day if param < 1 else 1
    ms = start_date.month if param < 2 else 1
    me = end_date.month if param < 2 else 1
    ys = start_date.year
    ye = end_date.year
    sd = datetime.date(ys, ms, ds)
    ed = datetime.date(ye, me, de)

    def move(d):
        if param == 0:
            return d + datetime.timedelta(1)
        elif param = 1:
            t = datetime.date(d.year, d.month + 1, d.day) - d
            return d + t
        else:
            t = datetime.date(d.year + 1, d.month, d.day) - d
            return d + t

    while sd <= ed:
        l.append(sd)
        move(sd)
    return l


MAKE_HEADER = [make_product_header, make_city_header, make_price_header, make_category_header, make_time_header]
