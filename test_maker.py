import time
import text_parser
import json
from pprint import pprint
from random import randint, choice, random

def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        print(f"Executed in {'{:.6f}'.format(time.time() - start_time)} seconds")
        return result
    return wrapper

# doesn't include A, T, 1,111 edge cases
def randfloat():
    return str(choice([1,-1]) * round(random() * 1000, 3))
def random_text():
    return '\n'.join([
        choice(["True", "False", "WRONG"]),
        choice(["True", "False", "WRONG"]),
        ','.join(map(str, [randint(0,255), randint(0,255), randint(0,255)])) + choice(["", ","]),
        choice(list(text_parser.MATERIAL) + ["WRONG"]),
        randfloat(),
        choice(list(text_parser.SURFACETYPE) + ["WRONG"]),
        randfloat(),
        ','.join([randfloat(), randfloat(), randfloat()]) + choice(["", ","]),
        ','.join([randfloat(), randfloat(), randfloat()]) + choice(["", ","]),
        ','.join([randfloat(), randfloat(), randfloat()]) + choice(["", ","]),
        choice(list(text_parser.PARTTYPE) + ["WRONG"]),
        choice(list(text_parser.TRUSS_STYLES.keys()) + ["WRONG"]),
    ])

@time_it
def generate_random_parts(count=10, file='test'):
    all_data = list()
    all_data_del = list()

    for _ in range(count):
        part_data = text_parser.parse_image_text(random_text())
        all_data.append(part_data)
        delimited_part_data = text_parser.to_delimeted(part_data, ';')
        all_data_del.append(delimited_part_data)

    with open(file+'.json', 'w') as f:
        json.dump(all_data, f, sort_keys=False, indent=4)
    with open(file+'.csv', 'w') as f:
        f.writelines(all_data_del)

    pprint(all_data, indent=4, sort_dicts=False)

generate_random_parts()

