from os.path import dirname, join

def _get_copy_fields():
    path = join(dirname(__file__), 'copy-fields.txt')
    with open(path, 'r') as f:
        lines = [line.strip() for line in f]
    return lines

copy_fields = _get_copy_fields()
