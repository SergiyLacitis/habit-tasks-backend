import re


def camel_case_to_snake_case(string: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()
