import datetime

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

def check_product(current, previous, param):
    return current == previous


def check_city(current, previous, param):
    return current == previous


def check_price(current, previous, param):
    def get_delta(value):
        return (value - 1) / REPORT_PRICE_SLICES[param]
    return get_delta(current) == get_delta(previous)


def check_category(current, previous, param):
    return True


def check_time(current, previous, param):
    if param == 0:
        return current.day == previous.day
    elif param == 1:
        return current.month == previous.month
    elif param == 2:
        return current.year == previous.year
    else
        return False


CHECK_FOR_CHANGE = [check_product, check_city, check_price, check_category, check_time]


def change_product(data_block, appender, current, previous, param):
    data_block.append(appender)
    return len(data_block) - 1

'''
    data_block - grid or row to append. Appender - a [0] or 0 - value to put in the list
    current - to count delta from it and from previous and add as many zeroes as is needed
    param is param =)
    
    need to update iterators with data_block.length -> in views
'''

def change_city():
    pass


def change_price():
    pass


def change_category():
    pass


def change_time():
    pass


CHANGE = [change_product, change_city, change_price, change_category, change_time]
'''
check for change - array of functions checking whether row/col should be changed or not
also need to fill change array with functions that'll move to next with inserting emptys (for rows too)
think about saving col/row headers
and check the category sql pieces
'''