import re

def camel_case_to_snake_case(string: str) -> str:
	return re.sub(r'([a-z])([A-Z])', r'\1_\2', string).lower()