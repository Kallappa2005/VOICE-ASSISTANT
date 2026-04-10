import sys
sys.path.insert(0, r'c:\Users\kalla\Desktop\DEVOPS\voice-assistant')
from src.automation.coding_mode import CodingMode

cm = CodingMode()
print("Testing terminal launch...")
result = cm._run_in_new_terminal(
    project_path=r"C:\Users\kalla\Desktop\PROD_RPD\backend",
    command="nodemon server.js"
)
print(f"Result: {result}")
