

def format_mask_currency(amount, currency_master):
    result_list = [currency_master.currency_sign, ' ']
    below_period = None
    if currency_master.currency_code != 'KRW':
        below_period = str(round(amount, 2)).split('.')[-1]

    integer_list = []
    while amount >= 1000:
        temp_num_str = str(int(amount % 1000))
        while len(temp_num_str) < 3:
            temp_num_str = '0' + temp_num_str
        integer_list.append(temp_num_str)
        amount /= 1000
    integer_list.append(str(int(amount)))

    for i in range(len(integer_list)):
        result_list.append(integer_list[(i + 1) * (-1)])
        result_list.append(',')
    result_list.pop(-1)
    if below_period:
        result_list.append('.')
        result_list.append(below_period)
    return ''.join(result_list)
