import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"

@dataclass
class Employee:
    id: str
    name: str
    skills: List[str]
    experience_level: str  # junior, mid, senior, expert
    availability_hours: float
    current_workload: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "skills": self.skills,
            "experience_level": self.experience_level,
            "availability_hours": self.availability_hours,
            "current_workload": self.current_workload
        }

@dataclass
class Task:
    id: str
    title: str
    description: str
    required_skills: List[str]
    estimated_hours: float
    priority: TaskPriority
    complexity: TaskComplexity
    dependencies: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "required_skills": self.required_skills,
            "estimated_hours": self.estimated_hours,
            "priority": self.priority.value,
            "complexity": self.complexity.value,
            "dependencies": self.dependencies or []
        }

@dataclass
class TaskAssignment:
    task_id: str
    employee_id: str
    assigned_hours: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "employee_id": self.employee_id,
            "assigned_hours": self.assigned_hours,
            "start_date": self.start_date,
            "end_date": self.end_date
        }

class TaskAssignerAgent:
    def __init__(self):
        self.employees: List[Employee] = []
        self.tasks: List[Task] = []
        self.assignments: List[TaskAssignment] = []
    
    def add_employee(self, employee: Employee):
        """Add an employee to the system"""
        self.employees.append(employee)
    
    def add_task(self, task: Task):
        """Add a task to the system"""
        self.tasks.append(task)
    
    def _calculate_skill_match(self, task: Task, employee: Employee) -> float:
        """Calculate how well an employee's skills match a task's requirements"""
        if not task.required_skills:
            return 1.0
        
        matched_skills = set(task.required_skills) & set(employee.skills)
        return len(matched_skills) / len(task.required_skills)
    
    def _calculate_experience_match(self, task: Task, employee: Employee) -> float:
        """Calculate how well an employee's experience level matches task complexity"""
        experience_levels = {
            "junior": 1,
            "mid": 2,
            "senior": 3,
            "expert": 4
        }
        
        complexity_levels = {
            TaskComplexity.SIMPLE: 1,
            TaskComplexity.MODERATE: 2,
            TaskComplexity.COMPLEX: 3,
            TaskComplexity.EXPERT: 4
        }
        
        employee_level = experience_levels.get(employee.experience_level, 1)
        task_level = complexity_levels.get(task.complexity, 1)
        
        # Perfect match gets 1.0, overqualified gets 0.8, underqualified gets penalty
        if employee_level >= task_level:
            return 0.8 if employee_level > task_level else 1.0
        else:
            return max(0.1, 1.0 - (task_level - employee_level) * 0.3)
    
    def _calculate_availability_score(self, employee: Employee, task: Task) -> float:
        """Calculate how available an employee is for a task"""
        available_hours = employee.availability_hours - employee.current_workload
        if available_hours <= 0:
            return 0.0
        
        # Prefer employees with more available time
        return min(1.0, available_hours / task.estimated_hours)
    
    def _calculate_priority_score(self, task: Task) -> float:
        """Calculate priority score for task ordering"""
        priority_scores = {
            TaskPriority.LOW: 1.0,
            TaskPriority.MEDIUM: 2.0,
            TaskPriority.HIGH: 3.0,
            TaskPriority.CRITICAL: 4.0
        }
        return priority_scores.get(task.priority, 1.0)
    
    def assign_tasks(self) -> List[TaskAssignment]:
        """Main method to assign tasks to employees"""
        # Sort tasks by priority and dependencies
        sorted_tasks = self._sort_tasks_by_priority_and_dependencies()
        
        # Reset assignments and workload
        self.assignments = []
        for employee in self.employees:
            employee.current_workload = 0.0
        
        for task in sorted_tasks:
            best_employee = self._find_best_employee_for_task(task)
            if best_employee:
                assignment = TaskAssignment(
                    task_id=task.id,
                    employee_id=best_employee.id,
                    assigned_hours=task.estimated_hours
                )
                self.assignments.append(assignment)
                best_employee.current_workload += task.estimated_hours
        
        return self.assignments
    
    def _sort_tasks_by_priority_and_dependencies(self) -> List[Task]:
        """Sort tasks considering dependencies and priority"""
        # Simple topological sort for dependencies
        task_dict = {task.id: task for task in self.tasks}
        visited = set()
        temp_visited = set()
        sorted_tasks = []
        
        def visit(task_id):
            if task_id in temp_visited:
                raise ValueError(f"Circular dependency detected: {task_id}")
            if task_id in visited:
                return
            
            temp_visited.add(task_id)
            task = task_dict.get(task_id)
            if task and task.dependencies:
                for dep_id in task.dependencies:
                    visit(dep_id)
            
            temp_visited.remove(task_id)
            visited.add(task_id)
            sorted_tasks.append(task_dict[task_id])
        
        # Visit all tasks
        for task in self.tasks:
            if task.id not in visited:
                visit(task.id)
        
        # Sort by priority within dependency order
        sorted_tasks.sort(key=lambda t: self._calculate_priority_score(t), reverse=True)
        return sorted_tasks
    
    def _find_best_employee_for_task(self, task: Task) -> Optional[Employee]:
        """Find the best available employee for a given task"""
        best_employee = None
        best_score = -1
        
        for employee in self.employees:
            # Skip if employee has no available time
            if employee.current_workload >= employee.availability_hours:
                continue
            
            # Calculate composite score
            skill_score = self._calculate_skill_match(task, employee)
            experience_score = self._calculate_experience_match(task, employee)
            availability_score = self._calculate_availability_score(employee, task)
            
            # Weighted composite score
            composite_score = (
                skill_score * 0.4 +
                experience_score * 0.3 +
                availability_score * 0.3
            )
            
            if composite_score > best_score:
                best_score = composite_score
                best_employee = employee
        
        return best_employee
    
    def get_assignment_summary(self) -> Dict[str, Any]:
        """Get a summary of all task assignments"""
        summary = {
            "total_tasks": len(self.tasks),
            "total_employees": len(self.employees),
            "assigned_tasks": len(self.assignments),
            "unassigned_tasks": len(self.tasks) - len(self.assignments),
            "assignments": [assignment.to_dict() for assignment in self.assignments],
            "employee_workloads": [
                {
                    "employee_id": emp.id,
                    "employee_name": emp.name,
                    "current_workload": emp.current_workload,
                    "availability": emp.availability_hours,
                    "utilization_percentage": (emp.current_workload / emp.availability_hours * 100) if emp.availability_hours > 0 else 0
                }
                for emp in self.employees
            ]
        }
        return summary
    
    def export_assignments(self, filename: str):
        """Export assignments to a JSON file"""
        data = {
            "assignments": [assignment.to_dict() for assignment in self.assignments],
            "summary": self.get_assignment_summary()
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_from_json(self, filename: str):
        """Load employees and tasks from a JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load employees
        if 'employees' in data:
            self.employees = []
            for emp_data in data['employees']:
                employee = Employee(
                    id=emp_data['id'],
                    name=emp_data['name'],
                    skills=emp_data['skills'],
                    experience_level=emp_data['experience_level'],
                    availability_hours=emp_data['availability_hours']
                )
                self.employees.append(employee)
        
        # Load tasks
        if 'tasks' in data:
            self.tasks = []
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
                self.tasks.append(task)

def create_sample_data() -> tuple[List[Employee], List[Task]]:
    """Create sample data for testing"""
    employees = [
        Employee("emp1", "Alice Johnson", ["python", "django", "postgresql"], "senior", 40.0),
        Employee("emp2", "Bob Smith", ["javascript", "react", "node.js"], "mid", 35.0),
        Employee("emp3", "Carol Davis", ["python", "machine_learning", "data_analysis"], "expert", 30.0),
        Employee("emp4", "David Wilson", ["html", "css", "javascript"], "junior", 40.0),
        Employee("emp5", "Eva Brown", ["project_management", "agile", "documentation"], "senior", 35.0)
    ]
    
    tasks = [
        Task("task1", "Backend API Development", "Develop REST API endpoints", 
             ["python", "django"], 16.0, TaskPriority.HIGH, TaskComplexity.MODERATE),
        Task("task2", "Frontend Dashboard", "Create React dashboard", 
             ["javascript", "react"], 20.0, TaskPriority.HIGH, TaskComplexity.MODERATE),
        Task("task3", "Database Schema Design", "Design and implement database schema", 
             ["postgresql", "database_design"], 12.0, TaskPriority.MEDIUM, TaskComplexity.COMPLEX),
        Task("task4", "Machine Learning Model", "Implement ML prediction model", 
             ["python", "machine_learning"], 25.0, TaskPriority.CRITICAL, TaskComplexity.EXPERT),
        Task("task5", "UI/UX Design", "Design user interface mockups", 
             ["html", "css"], 8.0, TaskPriority.LOW, TaskComplexity.SIMPLE),
        Task("task6", "Project Documentation", "Write project documentation", 
             ["documentation", "project_management"], 10.0, TaskPriority.MEDIUM, TaskComplexity.SIMPLE)
    ]
    
    return employees, tasks

def main():
    """Main function to demonstrate the task assigner agent"""
    print("=== Task Assignment Agent ===\n")
    
    # Create agent
    agent = TaskAssignerAgent()
    
    # Load sample data
    employees, tasks = create_sample_data()
    
    print("Employees:")
    for emp in employees:
        print(f"  - {emp.name} ({emp.experience_level}): {', '.join(emp.skills)}")
        print(f"    Availability: {emp.availability_hours} hours/week")
    
    print("\nTasks:")
    for task in tasks:
        print(f"  - {task.title}")
        print(f"    Skills: {', '.join(task.required_skills)}")
        print(f"    Hours: {task.estimated_hours}, Priority: {task.priority.value}, Complexity: {task.complexity.value}")
    
    # Add data to agent
    for emp in employees:
        agent.add_employee(emp)
    for task in tasks:
        agent.add_task(task)
    
    print("\n=== Assigning Tasks ===\n")
    
    # Assign tasks
    assignments = agent.assign_tasks()
    
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
    
    # Export assignments
    agent.export_assignments("task_assignments.json")
    print(f"\nAssignments exported to task_assignments.json")

if __name__ == "__main__":
    main()
