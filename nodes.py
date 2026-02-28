from pocketflow import Node
from utils import get_current_timestamp
from datetime import datetime
import sys
import yaml
import ollama
import json
import os
import dateparser

class InputTaskNode(Node):
    def prep(self, shared): 
        if "task_list" not in shared:
            if os.path.exists("tasks.yaml"):
                try:
                    with open("tasks.yaml", "r") as f:
                        shared["task_list"] = yaml.safe_load(f) or []
                except yaml.YAMLError:
                    shared["task_list"] = []
            else:
                shared["task_list"] = []
        return shared["task_list"]

    def exec(self, task_list):
        print("\n" + "="*40)
        print("🎛️  MAIN MENU")
        print("1. 📝 Create a new task")
        print("2. ✅ Mark task as done")
        print("3. 🗑️ Delete task")
        print("4. 📋 View task board")
        print("5. 🚪 Exit")
        print("="*40)
        
        choice = input("👉 Select an option (1-5): ").strip()
        
        if choice == "5" or choice.lower() == "exit":
            return {"action": "exit"}
            
        elif choice == "1":
            task = input("\n📝 Enter task description (or 'b' to go back): ").strip()
            if task.lower() in ['b', 'back']:
                return {"action": "back"}
                
            priority = input("🔥 Enter Priority (e.g., High, Low): ").strip()
            calendar = input("📅 Enter Calendar/Deadline (e.g., Tomorrow at 5pm): ").strip()
            return {"action": "create", "task": task, "priority": priority, "calendar": calendar}
            
        elif choice == "2":
            if not task_list:
                print("\n⚠️ You have no tasks to mark as done!")
                return {"action": "back"}
                
            print("\n📋 Tasks available to complete:")
            for idx, item in enumerate(task_list, 1):
                print(f"  {idx}. {item['task']}")
                
            user_input = input("\n✅ Which task number is done? (e.g., 1, or 'b' to go back): ").strip()
            if user_input.lower() in ['b', 'back']:
                return {"action": "back"}
                
            try:
                idx = int(user_input) - 1
                if 0 <= idx < len(task_list):
                    return {"action": "done", "target": idx}
                else:
                    print("⚠️ Task number out of range.")
                    return {"action": "invalid_cmd"}
            except ValueError:
                print("⚠️ Invalid format. Please enter a number.")
                return {"action": "invalid_cmd"}
                
        elif choice == "3":
            if not task_list:
                print("\n⚠️ You have no tasks to delete!")
                return {"action": "back"}
                
            print("\n📋 Tasks available to delete:")
            for idx, item in enumerate(task_list, 1):
                print(f"  {idx}. {item['task']}")
                
            user_input = input("\n🗑️ Which task number to delete? (e.g., 1, or 'b' to go back): ").strip()
            if user_input.lower() in ['b', 'back']:
                return {"action": "back"}
                
            try:
                idx = int(user_input) - 1
                if 0 <= idx < len(task_list):
                    return {"action": "delete", "target": idx}
                else:
                    print("⚠️ Task number out of range.")
                    return {"action": "invalid_cmd"}
            except ValueError:
                print("⚠️ Invalid format. Please enter a number.")
                return {"action": "invalid_cmd"}
                
        elif choice == "4":
            return {"action": "view"}
            
        else:
            print("⚠️ Invalid choice. Please select 1-5.")
            return {"action": "invalid_cmd"}

    def post(self, shared, prep_res, exec_res):
        if exec_res["action"] == "exit":
            print("👋 Shutting down Smart Task Assistant. Goodbye!")
            sys.exit() 
            
        if exec_res["action"] == "create":
            shared["task_name"] = exec_res["task"]
            shared["priority_input"] = exec_res["priority"]
            shared["calendar"] = exec_res["calendar"]
            
        if exec_res["action"] in ["done", "delete"]:
            shared["target_idx"] = exec_res["target"]
            
        return exec_res["action"]

class ValidationNode(Node):
    def prep(self, shared): return shared.get("task_name", "")
    
    def exec(self, task_name):
        return "valid" if len(task_name.strip()) >= 3 else "invalid"
        
    def post(self, shared, prep_res, exec_res):
        if exec_res == "invalid":
            print("⚠️ Error: Task description too vague. Please provide more detail.")
        return exec_res

class CategorizeNode(Node):
    def prep(self, shared): 
        return shared.get("priority_input", "")
        
    def exec(self, prep_res):
        text = prep_res.lower()
        # Route logic branch based on user's direct input
        triggers = ["high", "urgent", "asap", "priority", "important", "critical"]
        if any(word in text for word in triggers):
            return "high_priority"
        return "low_priority"
        
    def post(self, shared, prep_res, exec_res):
        shared["priority"] = exec_res
        return exec_res

class UpdateTaskNode(Node):
    """New Node to handle removing completed tasks."""
    def prep(self, shared):
        return shared.get("target_idx"), shared.get("task_list", [])
        
    def exec(self, prep_res):
        idx, task_list = prep_res
        if idx is not None and 0 <= idx < len(task_list):
            completed_task = task_list.pop(idx)
            print(f"\n✅ Marked '{completed_task['task']}' as done!")
        else:
            print(f"\n⚠️ Task number {idx + 1 if idx is not None else 'unknown'} not found.")
        return "success"
        
    def post(self, shared, prep_res, exec_res):
        return "default"

class DeleteTaskNode(Node):
    """New Node to handle deleting tasks without marking them done."""
    def prep(self, shared):
        return shared.get("target_idx"), shared.get("task_list", [])
        
    def exec(self, prep_res):
        idx, task_list = prep_res
        if idx is not None and 0 <= idx < len(task_list):
            deleted_task = task_list.pop(idx)
            print(f"\n🗑️ Deleted '{deleted_task['task']}' from the board.")
        else:
            print(f"\n⚠️ Task number {idx + 1 if idx is not None else 'unknown'} not found.")
        return "success"
        
    def post(self, shared, prep_res, exec_res):
        return "default"

class SaveNode(Node):
    """Updated to handle saving the task list to a YAML file."""
    def prep(self, shared): 
        return shared.get("task_list", [])
        
    def exec(self, task_list):
        try:
            with open("tasks.yaml", "w") as f:
                # default_flow_style=False ensures it looks like standard block YAML
                yaml.dump(task_list, f, sort_keys=False, default_flow_style=False)
            return "success"
        except Exception as e:
            print(f"⚠️ Error saving tasks to disk: {e}")
            return "error"
            
    def post(self, shared, prep_res, exec_res):
        return "default"

class ProcessNode(Node):
    def prep(self, shared): 
        return shared["task_name"], shared["priority"], shared.get("calendar", "")
        
    def exec(self, prep_res):
        task, priority, calendar = prep_res
        
        # --- BILINGUAL DATE PARSING LOGIC ---
        if calendar.strip():
            # Now explicitly supports Romanian and English
            parsed_date = dateparser.parse(calendar.strip(), languages=['ro', 'en'])
            schedule = parsed_date.strftime("%Y-%m-%d %H:%M:%S") if parsed_date else calendar.strip()
        else:
            schedule = get_current_timestamp()
            
        print(f"\n🧠 Thinking... breaking down '{task}' and estimating time...")
        
        prompt = (
            f"Break down the following task into 3 to 5 concise, actionable steps. "
            f"Estimate the time in minutes for each step. "
            f"Return ONLY a valid JSON list of dictionaries. "
            f"Use exactly this format: [{{\"step\": \"Action description\", \"estimated_minutes\": 15}}]. "
            f"Task: {task}"
        )
        
        try:
            resp = ollama.chat(
                model="gemma:2b",
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.2}, 
                format="json" 
            )
            
            llm_output = resp["message"]["content"].strip()
            if llm_output.startswith("```json"):
                llm_output = llm_output.replace("```json", "").replace("```", "").strip()
            micro_steps = json.loads(llm_output)
            
        except Exception as e:
            micro_steps = [
                {"step": "Review task requirements", "estimated_minutes": 5},
                {"step": f"Manual execution required (Error: {e})", "estimated_minutes": 0}
            ]

        assistant_response = {
            "intent": "process_and_breakdown_task",
            "entities": {"task_name": task},
            "priority": priority,
            "micro_steps": micro_steps,
            "suggested_schedule": schedule,
            "actions": [f"save_to_memory('{task}')"]
        }
        
        yaml_output = yaml.dump(assistant_response, sort_keys=False, default_flow_style=False)
        
        print("🤖 Smart Task Assistant Output:")
        print(yaml_output)
        
        return "Success", schedule, assistant_response

    # (Keep your existing post method for ProcessNode exactly the same)
    def post(self, shared, prep_res, exec_res):
        status, schedule, assistant_response = exec_res
        shared["task_list"].append({
            "task": shared["task_name"],
            "priority": shared["priority"].upper(),
            "time": schedule,  
            "full_yaml": assistant_response
        })
        return "default"

class SummaryNode(Node):
    def prep(self, shared): return shared
    def exec(self, shared):
        print("\n" + "="*40)
        print("📋 CURRENT TASK BOARD")
        
        total_minutes = 0
        
        for idx, item in enumerate(shared.get("task_list", []), 1):
            task_minutes = 0
            
            # Safely extract micro_steps from the saved yaml
            yaml_data = item.get("full_yaml", {})
            micro_steps = yaml_data.get("micro_steps", [])
            
            # Handle Gemma returning either a list of dicts or a single dict
            if isinstance(micro_steps, list):
                for step in micro_steps:
                    if isinstance(step, dict):
                        task_minutes += step.get("estimated_minutes", 0)
            elif isinstance(micro_steps, dict):
                task_minutes += micro_steps.get("estimated_minutes", 0)
                
            total_minutes += task_minutes
            
            # Add the estimated time to the display line
            time_badge = f" [~{task_minutes}m]" if task_minutes > 0 else ""
            print(f" {idx}. [{item['priority']}] {item['task']} (Scheduled: {item['time']}){time_badge}")
            
        print("-" * 40)
        
        # Format total time into hours and minutes
        hours = total_minutes // 60
        mins = total_minutes % 60
        time_display = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
        
        print(f"⏱️  Total Estimated Workload: {time_display}")
        print("="*40)
        return "Finished"
        
    def post(self, shared, prep_res, exec_res):
        return "default"
    
class CheckDeadlinesNode(Node):
    """Proactively checks for tasks due within an hour or overdue."""
    def prep(self, shared):
        return shared.get("task_list", [])

    def exec(self, task_list):
        now = datetime.now()
        alerts = []
        
        for item in task_list:
            time_str = item.get("time", "")
            try:
                # We expect the strict format "YYYY-MM-DD HH:MM:SS" we set up earlier
                task_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                time_diff = (task_time - now).total_seconds()
                
                # If due in the next 3600 seconds (1 hour) and not in the past
                if 0 <= time_diff <= 3600:
                    mins_left = int(time_diff // 60)
                    alerts.append(f"🔔 REMINDER: '{item['task']}' is due in {mins_left} minutes!")
                # If the time has already passed
                elif time_diff < 0:
                    alerts.append(f"⚠️ OVERDUE: '{item['task']}' was due at {time_str}!")
            except ValueError:
                # Skip tasks that don't have a valid, parseable strict timestamp
                pass
        
        # Print alerts if any exist
        if alerts:
            print("\n" + "❗"*20)
            for alert in alerts:
                print(alert)
            print("❗"*20)
            
        return "success"
        
    def post(self, shared, prep_res, exec_res):
        return "default"