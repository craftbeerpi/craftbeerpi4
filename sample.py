import re

pattern = "(actor)\/([\d])\/(on|toggle|off)$"

p = re.compile(pattern)
result = p.match("actor/1/toggle")

print(result, result.group(3))





