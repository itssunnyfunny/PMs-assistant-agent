"""
Integration module to connect the Task Assigner Agent with the Portia planner system.
This allows project managers to generate task breakdowns and then assign them to employees.
"""

import json
from typing import List, Dict, Any, Optional
from task_assigner import TaskAssignerAgent, Employee, Task, TaskPriority, TaskComplexity

def convert_portia_steps_to_tasks(portia_steps: List[Dict[str, Any]], 
                                 default_priority: str = "medium",
                                 default_complexity: str = "moderate") -> List[Task]:
    """
    Convert Portia planner steps to Task objects for the task assigner agent.
    
    Args:
        portia_steps: List of steps from Portia planner
        default_priority: Default priority for tasks
        default_complexity: Default complexity for tasks
    
    Returns:
        List of Task objects
    """
    tasks = []
    
    for i, step in enumerate(portia_steps):
        # Extract task information
        task_text = step.get("task") or step.get("description") or f"Step {i+1}"
        
        # Generate a simple task ID
        task_id = f"task_{i+1:03d}"
        
        # Try to infer skills from task description
        required_skills = infer_skills_from_description(task_text)
        
        # Estimate hours based on task complexity
        estimated_hours = estimate_hours_from_description(task_text)
        
        # Create task
        task = Task(
            id=task_id,
            title=task_text[:50] + "..." if len(task_text) > 50 else task_text,
            description=task_text,
            required_skills=required_skills,
            estimated_hours=estimated_hours,
            priority=TaskPriority(default_priority),
            complexity=TaskComplexity(default_complexity)
        )
        
        tasks.append(task)
    
    return tasks

def infer_skills_from_description(description: str) -> List[str]:
    """
    Infer required skills from task description using keyword matching.
    
    Args:
        description: Task description text
    
    Returns:
        List of inferred skills
    """
    description_lower = description.lower()
    skills = []
    
    # Define skill keywords
    skill_keywords = {
        "python": ["python", "django", "flask", "pandas", "numpy", "scikit-learn"],
        "javascript": ["javascript", "js", "react", "vue", "angular", "node.js", "express"],
        "java": ["java", "spring", "maven", "gradle"],
        "c++": ["c++", "cpp", "c plus plus"],
        "c#": ["c#", "csharp", ".net", "asp.net"],
        "database": ["database", "sql", "mysql", "postgresql", "mongodb", "redis"],
        "frontend": ["frontend", "ui", "ux", "html", "css", "design"],
        "backend": ["backend", "api", "rest", "graphql", "server"],
        "devops": ["devops", "docker", "kubernetes", "aws", "azure", "ci/cd"],
        "testing": ["testing", "test", "unit test", "integration test", "qa"],
        "documentation": ["documentation", "docs", "write", "document"],
        "project_management": ["project", "management", "planning", "coordination"]
    }
    
    for skill, keywords in skill_keywords.items():
        if any(keyword in description_lower for keyword in keywords):
            skills.append(skill)
    
    # If no skills detected, add generic ones
    if not skills:
        if any(word in description_lower for word in ["code", "develop", "program", "implement"]):
            skills.append("programming")
        if any(word in description_lower for word in ["design", "create", "build"]):
            skills.append("design")
        if any(word in description_lower for word in ["test", "verify", "validate"]):
            skills.append("testing")
        if any(word in description_lower for word in ["write", "document", "explain"]):
            skills.append("documentation")
    
    return skills

def estimate_hours_from_description(description: str) -> float:
    """
    Estimate task duration in hours based on description.
    
    Args:
        description: Task description text
    
    Returns:
        Estimated hours
    """
    description_lower = description.lower()
    
    # Simple heuristics for time estimation
    if any(word in description_lower for word in ["simple", "basic", "quick", "minor"]):
        return 2.0
    elif any(word in description_lower for word in ["complex", "advanced", "major", "comprehensive"]):
        return 16.0
    elif any(word in description_lower for word in ["research", "investigation", "analysis"]):
        return 8.0
    elif any(word in description_lower for word in ["design", "architecture", "planning"]):
        return 12.0
    elif any(word in description_lower for word in ["testing", "validation", "qa"]):
        return 6.0
    elif any(word in description_lower for word in ["documentation", "writing", "manual"]):
        return 4.0
    else:
        return 8.0  # Default estimate

def create_sample_team() -> List[Employee]:
    """
    Create a sample team of employees for demonstration.
    
    Returns:
        List of Employee objects
    """
    employees = [
        Employee("dev1", "Alice Johnson", ["python", "django", "postgresql", "programming"], "senior", 40.0),
        Employee("dev2", "Bob Smith", ["javascript", "react", "node.js", "programming"], "mid", 35.0),
        Employee("dev3", "Carol Davis", ["python", "machine_learning", "data_analysis", "programming"], "expert", 30.0),
        Employee("dev4", "David Wilson", ["html", "css", "javascript", "frontend"], "junior", 40.0),
        Employee("dev5", "Eva Brown", ["project_management", "agile", "documentation"], "senior", 35.0),
        Employee("dev6", "Frank Miller", ["java", "spring", "database", "programming"], "mid", 40.0),
        Employee("dev7", "Grace Lee", ["devops", "docker", "aws", "testing"], "senior", 30.0),
        Employee("dev8", "Henry Chen", ["c++", "programming", "testing"], "mid", 35.0)
    ]
    
    return employees

def integrate_with_portia_plan(portia_plan: Dict[str, Any], 
                              employees: Optional[List[Employee]] = None,
                              output_file: str = "integrated_assignments.json") -> Dict[str, Any]:
    """
    Integrate Portia plan with task assignment.
    
    Args:
        portia_plan: Plan dictionary from Portia planner
        employees: List of employees (if None, creates sample team)
        output_file: File to save integrated results
    
    Returns:
        Dictionary containing integration results
    """
    print("=== Integrating Portia Plan with Task Assignment ===\n")
    
    # Extract steps from Portia plan
    steps = portia_plan.get("steps", [])
    if not steps:
        print("No steps found in Portia plan.")
        return {}
    
    print(f"Found {len(steps)} steps in Portia plan.")
    
    # Convert steps to tasks
    tasks = convert_portia_steps_to_tasks(steps)
    print(f"Converted to {len(tasks)} tasks.")
    
    # Use provided employees or create sample team
    if employees is None:
        employees = create_sample_team()
        print(f"Using sample team of {len(employees)} employees.")
    
    # Create task assigner agent
    agent = TaskAssignerAgent()
    
    # Add employees and tasks
    for emp in employees:
        agent.add_employee(emp)
    for task in tasks:
        agent.add_task(task)
    
    # Assign tasks
    print("\n=== Assigning Tasks ===\n")
    assignments = agent.assign_tasks()
    
    if assignments:
        print("Task Assignments:")
        for assignment in assignments:
            task = next(t for t in tasks if t.id == assignment.task_id)
            employee = next(e for e in employees if e.id == assignment.employee_id)
            print(f"  {task.title} -> {employee.name} ({assignment.assigned_hours} hours)")
        
        # Get summary
        summary = agent.get_assignment_summary()
        
        print(f"\n=== Summary ===")
        print(f"Total tasks: {summary['total_tasks']}")
        print(f"Assigned tasks: {summary['assigned_tasks']}")
        print(f"Unassigned tasks: {summary['unassigned_tasks']}")
        
        print(f"\nEmployee Workloads:")
        for workload in summary['employee_workloads']:
            print(f"  {workload['employee_name']}: {workload['current_workload']:.1f}/{workload['availability']:.1f} hours ({workload['utilization_percentage']:.1f}%)")
        
        # Export results
        agent.export_assignments(output_file)
        print(f"\nAssignments exported to {output_file}")
        
        # Return integration results
        results = {
            "portia_plan_id": portia_plan.get("id", "unknown"),
            "original_steps": len(steps),
            "converted_tasks": len(tasks),
            "assignments": len(assignments),
            "summary": summary,
            "output_file": output_file
        }
        
        return results
    else:
        print("No tasks could be assigned.")
        return {"error": "No tasks could be assigned"}

def create_custom_team_from_input() -> List[Employee]:
    """
    Create a custom team by asking user for employee details.
    
    Returns:
        List of Employee objects
    """
    employees = []
    
    print("=== Creating Custom Team ===")
    print("Enter employee details (press Enter without ID to finish)\n")
    
    while True:
        try:
            emp_id = input("Employee ID (or Enter to finish): ").strip()
            if not emp_id:
                break
            
            name = input("Employee Name: ").strip()
            if not name:
                print("Name cannot be empty. Skipping this employee.")
                continue
            
            skills_input = input("Skills (comma-separated): ").strip()
            skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
            
            print("Experience levels: junior, mid, senior, expert")
            experience_level = input("Experience Level (default: mid): ").strip().lower()
            if experience_level not in ["junior", "mid", "senior", "expert"]:
                experience_level = "mid"
            
            try:
                availability = float(input("Availability (hours/week, default: 40): ").strip() or "40")
                if availability <= 0:
                    availability = 40.0
            except ValueError:
                availability = 40.0
            
            employee = Employee(emp_id, name, skills, experience_level, availability)
            employees.append(employee)
            print(f"Added {name} to team.\n")
            
        except (EOFError, KeyboardInterrupt):
            print("\nTeam creation cancelled.")
            break
    
    return employees

def main():
    """Main function for the integration module"""
    print("=== Portia Plan Integration with Task Assignment ===\n")
    
    print("This module integrates Portia project plans with employee task assignment.")
    print("You can:")
    print("1. Use with existing Portia plan data")
    print("2. Create a custom team")
    print("3. Use sample data for testing\n")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        print("Please provide your Portia plan data or use the integration function directly.")
        print("Use integrate_with_portia_plan(portia_plan, employees) function.")
    
    elif choice == "2":
        employees = create_custom_team_from_input()
        if employees:
            print(f"\nCreated team of {len(employees)} employees:")
            for emp in employees:
                print(f"  - {emp.name} ({emp.experience_level}): {', '.join(emp.skills)}")
    
    elif choice == "3":
        employees = create_sample_team()
        print(f"\nSample team of {len(employees)} employees:")
        for emp in employees:
            print(f"  - {emp.name} ({emp.experience_level}): {', '.join(emp.skills)}")
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
