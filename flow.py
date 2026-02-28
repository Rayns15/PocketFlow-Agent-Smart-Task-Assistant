from pocketflow import Flow
from nodes import (
    InputTaskNode, ValidationNode, CategorizeNode, 
    ProcessNode, SaveNode, SummaryNode, UpdateTaskNode,
    CheckDeadlinesNode, DeleteTaskNode # <-- Import DeleteTaskNode
)

input_n = InputTaskNode()
valid_n = ValidationNode()
logic_n = CategorizeNode()
work_n = ProcessNode()
save_n = SaveNode() 
report_n = SummaryNode()
update_n = UpdateTaskNode()
check_n = CheckDeadlinesNode() 
delete_n = DeleteTaskNode() # <-- Instantiate it

# Input Branching
input_n - "create" >> valid_n
input_n - "done" >> update_n
input_n - "delete" >> delete_n   # <-- Route the new delete option
input_n - "view" >> report_n
input_n - "back" >> input_n
input_n - "invalid_cmd" >> input_n

# Standard Creation Graph
valid_n - "invalid" >> input_n
valid_n - "valid" >> logic_n

# Logic Branching
logic_n - "high_priority" >> work_n
logic_n - "low_priority" >> work_n

# Process, Update, & Delete converge on Save
work_n >> save_n       
update_n >> save_n     
delete_n >> save_n     # <-- Route delete_n to save_n

# Save > Report > Check Deadlines > Loop Back to Input
save_n >> report_n     
report_n >> check_n    
check_n >> input_n     

task_flow = Flow(input_n)