def date_ordinal(n: str) -> str:
    """ Pretty month date."""

    dic = {'01': 'st', '21': 'st', '31': 'st',
           '02': 'nd', '22': 'nd',
           '03': 'rd', '23': 'rd'}
    val = n[:2]
    return f'{val}{dic.get(val, "th")}{n[2:]}'
