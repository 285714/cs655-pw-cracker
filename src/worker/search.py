import hashlib

def map_order_to_letter(c):
    """
    This function maps 0 -> 'A', ... 26 -> 'a'
    """
    if c < 26:
        return chr(c+65)
    else:
        return chr(c+71)

def convert_order_to_string(n):
    """
    Convert from a number for the order of the string (assigned by the server)
    to a 5-character string
    """
    a = n
    result = ''
    for i in range(5):
        r = a%52
        result = map_order_to_letter(r) + result
        a = a // 52
    return result

def search(range_number, hash):
    """Output the 5-character string in the range if md5 hash matched the input
    Output '' if none matches
    """
    for n in range_number:
        p = convert_order_to_string(n)
        h = hashlib.md5(p.encode()).hexdigest()
        if h == hash:
            return p
    return ""
