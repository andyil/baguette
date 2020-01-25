from os.path import join, dirname

def init_fields(file):
    FILE = join(dirname(__file__), file)
    f = open(FILE, 'r')
    t = f.read()
    f.close()
    return t.split('\n')




fields = init_fields('fields_order.txt')
fields_judges = init_fields('fields_order_judges.txt')
