import os


def get_field_binary(data: dict, field: str):
    return b"%s" % bytearray(data.get(field, ""), "utf-8")


def root_dir():
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        return open(src).read()
    except IOError as exc:
        return str(exc)
