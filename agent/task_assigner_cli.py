import json
import argparse
import sys
from typing import List, Dict, Any
from task_assigner import TaskAssignerAgent, Employee, Task, TaskPriority, TaskComplexity

def create_employee_from_input() -> Employee:
    """Create an employee from user input"""
    print("\n=== Adding New Employee ===")
    
    emp_id = input("Employee ID: ").strip()
    if not emp_id:
        raise ValueError("Employee ID cannot be empty")
    
    name = input("Employee Name: ").strip()
    if not name:
        raise ValueError("Employee name cannot be empty")
    
    skills_input = input("Skills (comma-separated): ").strip()
    skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
    
    print("Experience levels: junior, mid, senior, expert")
    experience_level = input("Experience Level: ").strip().lower()
    if experience_level not in ["junior", "mid", "senior", "expert"]:
        experience_level = "mid"
    
    try:
        availability = float(input("Availability (hours/week): ").strip())
        if availability <= 0:
            raise ValueError("Availability must be positive")
    except ValueError:
        availability = 40.0
    
    return Employee(emp_id, name, skills, experience_level, availability)

def create_task_from_input() -> Task:
    """Create a task from user input"""
    print("\n=== Adding New Task ===")
    
    task_id = input("Task ID: ").strip()
    if not task_id:
        raise ValueError("Task ID cannot be empty")
    
    title = input("Task Title: ").strip()
    if not title:
        raise ValueError("Task title cannot be empty")
    
    description = input("Task Description: ").strip()
    if not description:
        description = title
    
    skills_input = input("Required Skills (comma-separated): ").strip()
    required_skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
    
    try:
        estimated_hours = float(input("Estimated Hours: ").strip())
        if estimated_hours <= 0:
            raise ValueError("Estimated hours must be positive")
    except ValueError:
        estimated_hours = 8.0
    
    print("Priority levels: low, medium, high, critical")
    priority_input = input("Priority: ").strip().lower()
    try:
        priority = TaskPriority(priority_input)
    except ValueError:
        priority = TaskPriority.MEDIUM
    
    print("Complexity levels: simple, moderate, complex, expert")
    complexity_input = input("Complexity: ").strip().lower()
    try:
        complexity = TaskComplexity(complexity_input)
    except ValueError:
        complexity = TaskComplexity.MODERATE
    
    dependencies_input = input("Dependencies (comma-separated task IDs, or empty): ").strip()
    dependencies = [dep.strip() for dep in dependencies_input.split(",") if dep.strip()]
    
    return Task(task_id, title, description, required_skills, estimated_hours, priority, complexity, dependencies)

def load_data_from_file(filename: str) -> tuple[List[Employee], List[Task]]:
    """Load employees and tasks from a JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        employees = []
        if 'employees' in data:
            for emp_data in data['employees']:
                employee = Employee(
                    id=emp_data['id'],
                    name=emp_data['name'],
                    skills=emp_data['skills'],
                    experience_level=emp_data['experience_level'],
                    availability_hours=emp_data['availability_hours']
                )
                employees.append(employee)
        
        tasks = []
        if 'tasks' in data:
            for task_data in data['tasks']:
                task = Task(
                    id=task_data['id'],
                    title=task_data['title'],
                    description=task_data['description'],
                    required_skills=task_data['required_skills'],
                    estimated_hours=task_data['estimated_hours'],
                    priority=TaskPriority(task_data['priority']),
                    complexity=TaskComplexity(task_data['complexity']),
                    dependencies=task_data.get('dependencies', [])
                )
                tasks.append(task)
        
        return employees, tasks
    except FileNotFoundError:
        print(f"File {filename} not found. Starting with empty data.")
        return [], []
    except json.JSONDecodeError:
        print(f"Invalid JSON in {filename}. Starting with empty data.")
        return [], []

def save_data_to_file(employees: List[Employee], tasks: List[Task], filename: str):
    """Save employees and tasks to a JSON file"""
    data = {
        "employees": [emp.to_dict() for emp in employees],
        "tasks": [task.to_dict() for task in tasks]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"Data saved to {filename}")

def interactive_mode():
    """Run the task assigner in interactive mode"""
    print("=== Task Assignment Agent - Interactive Mode ===\n")
    
    # Load existing data or start fresh
    try:
        load_file = input("Load existing data from file? (y/N): ").strip().lower()
        if load_file == 'y':
            filename = input("Filename: ").strip() or "project_data.json"
            employees, tasks = load_data_from_file(filename)
        else:
            employees, tasks = [], []
    except (EOFError, KeyboardInterrupt):
        employees, tasks = [], []
    
    agent = TaskAssignerAgent()
    
    # Add existing data to agent
    for emp in employees:
        agent.add_employee(emp)
    for task in tasks:
        agent.add_task(task)
    
    while True:
        try:
            print("\n=== Menu ===")
            print("1. Add Employee")
            print("2. Add Task")
            print("3. View Employees")
            print("4. View Tasks")
            print("5. Assign Tasks")
            print("6. View Assignments")
            print("7. Save Data")
            print("8. Load Data")
            print("9. Exit")
            
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == "1":
                try:
                    employee = create_employee_from_input()
                    agent.add_employee(employee)
                    employees.append(employee)
                    print(f"Employee {employee.name} added successfully!")
                except ValueError as e:
                    print(f"Error: {e}")
                except (EOFError, KeyboardInterrupt):
                    print("Operation cancelled.")
            
            elif choice == "2":
                try:
                    task = create_task_from_input()
                    agent.add_task(task)
                    tasks.append(task)
                    print(f"Task '{task.title}' added successfully!")
                except ValueError as e:
                    print(f"Error: {e}")
                except (EOFError, KeyboardInterrupt):
                    print("Operation cancelled.")
            
            elif choice == "3":
                print("\n=== Employees ===")
                if not employees:
                    print("No employees added yet.")
                else:
                    for i, emp in enumerate(employees, 1):
                        print(f"{i}. {emp.name} ({emp.experience_level})")
                        print(f"   Skills: {', '.join(emp.skills)}")
                        print(f"   Availability: {emp.availability_hours} hours/week")
                        print()
            
            elif choice == "4":
                print("\n=== Tasks ===")
                if not tasks:
                    print("No tasks added yet.")
                else:
                    for i, task in enumerate(tasks, 1):
                        print(f"{i}. {task.title}")
                        print(f"   Description: {task.description}")
                        print(f"   Skills: {', '.join(task.required_skills)}")
                        print(f"   Hours: {task.estimated_hours}, Priority: {task.priority.value}, Complexity: {task.complexity.value}")
                        if task.dependencies:
                            print(f"   Dependencies: {', '.join(task.dependencies)}")
                        print()
            
            elif choice == "5":
                if not employees:
                    print("No employees available. Add employees first.")
                    continue
                if not tasks:
                    print("No tasks available. Add tasks first.")
                    continue
                
                print("\n=== Assigning Tasks ===")
                assignments = agent.assign_tasks()
                
                if assignments:
                    print("Task Assignments:")
                    for assignment in assignments:
                        task = next(t for t in tasks if t.id == assignment.task_id)
                        employee = next(e for e in employees if e.id == assignment.employee_id)
                        print(f"  {task.title} -> {employee.name} ({assignment.assigned_hours} hours)")
                    
                    # Show summary
                    summary = agent.get_assignment_summary()
                    print(f"\nSummary:")
                    print(f"  Total tasks: {summary['total_tasks']}")
                    print(f"  Assigned tasks: {summary['assigned_tasks']}")
                    print(f"  Unassigned tasks: {summary['unassigned_tasks']}")
                    
                    # Show workloads
                    print(f"\nEmployee Workloads:")
                    for workload in summary['employee_workloads']:
                        print(f"  {workload['employee_name']}: {workload['current_workload']:.1f}/{workload['availability']:.1f} hours ({workload['utilization_percentage']:.1f}%)")
                    
                    # Export assignments
                    try:
                        export = input("\nExport assignments to file? (y/N): ").strip().lower()
                        if export == 'y':
                            filename = input("Filename (default: task_assignments.json): ").strip() or "task_assignments.json"
                            agent.export_assignments(filename)
                            print(f"Assignments exported to {filename}")
                    except (EOFError, KeyboardInterrupt):
                        pass
                else:
                    print("No tasks could be assigned. Check employee availability and skill requirements.")
            
            elif choice == "6":
                if not agent.assignments:
                    print("No assignments made yet. Run 'Assign Tasks' first.")
                else:
                    print("\n=== Current Assignments ===")
                    for i, assignment in enumerate(agent.assignments, 1):
                        task = next(t for t in tasks if t.id == assignment.task_id)
                        employee = next(e for e in employees if e.id == assignment.employee_id)
                        print(f"{i}. {task.title} -> {employee.name} ({assignment.assigned_hours} hours)")
            
            elif choice == "7":
                filename = input("Filename (default: project_data.json): ").strip() or "project_data.json"
                save_data_to_file(employees, tasks, filename)
            
            elif choice == "8":
                filename = input("Filename: ").strip()
                if filename:
                    new_employees, new_tasks = load_data_from_file(filename)
                    # Clear existing data
                    agent.employees.clear()
                    agent.tasks.clear()
                    employees.clear()
                    tasks.clear()
                    
                    # Add new data
                    for emp in new_employees:
                        agent.add_employee(emp)
                        employees.append(emp)
                    for task in new_tasks:
                        agent.add_task(task)
                        tasks.append(task)
                    
                    print(f"Data loaded from {filename}")
            
            elif choice == "9":
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please select 1-9.")
        
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Task Assignment Agent CLI")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive mode")
    parser.add_argument("--demo", "-d", action="store_true",
                       help="Run with demo data")
    parser.add_argument("--input", "-f", type=str,
                       help="Input JSON file with employees and tasks")
    parser.add_argument("--output", "-o", type=str, default="task_assignments.json",
                       help="Output file for assignments (default: task_assignments.json)")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return
    
    # Non-interactive mode
    agent = TaskAssignerAgent()
    
    if args.demo:
        from task_assigner import create_sample_data
        employees, tasks = create_sample_data()
        print("=== Running with Demo Data ===\n")
    elif args.input:
        employees, tasks = load_data_from_file(args.input)
        if not employees and not tasks:
            print(f"No data loaded from {args.input}")
            return
        print(f"=== Loaded data from {args.input} ===\n")
    else:
        print("No input specified. Use --interactive, --demo, or --input <file>")
        return
    
    # Add data to agent
    for emp in employees:
        agent.add_employee(emp)
    for task in tasks:
        agent.add_task(task)
    
    # Show input data
    print("Employees:")
    for emp in employees:
        print(f"  - {emp.name} ({emp.experience_level}): {', '.join(emp.skills)}")
        print(f"    Availability: {emp.availability_hours} hours/week")
    
    print("\nTasks:")
    for task in tasks:
        print(f"  - {task.title}")
        print(f"    Skills: {', '.join(task.required_skills)}")
        print(f"    Hours: {task.estimated_hours}, Priority: {task.priority.value}, Complexity: {task.complexity.value}")
    
    # Assign tasks
    print("\n=== Assigning Tasks ===\n")
    assignments = agent.assign_tasks()
    
    if assignments:
        print("Task Assignments:")
        for assignment in assignments:
            task = next(t for t in tasks if t.id == assignment.task_id)
            employee = next(e for e in employees if e.id == assignment.employee_id)
            print(f"  {task.title} -> {employee.name} ({assignment.assigned_hours} hours)")
        
        # Export assignments
        agent.export_assignments(args.output)
        print(f"\nAssignments exported to {args.output}")
        
        # Show summary
        summary = agent.get_assignment_summary()
        print(f"\nSummary:")
        print(f"  Total tasks: {summary['total_tasks']}")
        print(f"  Assigned tasks: {summary['assigned_tasks']}")
        print(f"  Unassigned tasks: {summary['unassigned_tasks']}")
    else:
        print("No tasks could be assigned.")

if __name__ == "__main__":
    main()
