import sys, os
sys.path.insert(0, r'c:\Users\kalla\Desktop\DEVOPS\voice-assistant')
from src.automation.coding_mode import CodingMode
from src.commands.command_parser import CommandParser

# Test 1: CodingMode loads and validates config.json
cm = CodingMode()
print("CodingMode init  : OK")
ok = cm.validate_config()
print(f"Config valid     : {ok}")

# Test 2: Parser correctly maps all coding-mode phrases
parser = CommandParser()
test_phrases = [
    'start coding',
    'coding mode',
    'start coding mode',
    'begin coding',
    'launch project',
    'open project',
    'dev mode',
    'development mode',
]
print()
print("Parser intent checks:")
all_pass = True
for phrase in test_phrases:
    result = parser.parse(phrase)
    ok_flag = result['intent'] == 'start_coding'
    if not ok_flag:
        all_pass = False
    status = 'PASS' if ok_flag else 'FAIL'
    print(f"  [{status}]  \"{phrase}\"  ->  {result['intent']}")

print()
print("All tests passed!" if all_pass else "SOME TESTS FAILED!")
