# Task Assignment Agent

A powerful AI agent that automatically divides and assigns tasks to employees based on their skills, experience, and availability.

## Features

- **Intelligent Task Assignment**: Automatically matches tasks to the best-suited employees
- **Skill-Based Matching**: Considers employee skills and task requirements
- **Experience Level Matching**: Matches task complexity with employee experience
- **Workload Balancing**: Distributes work evenly across available team members
- **Priority Handling**: Respects task priorities and dependencies
- **Export Capabilities**: Save assignments and team data to JSON files
- **Portia Integration**: Works seamlessly with existing Portia project plans

## Quick Start

### 1. Basic Usage

```python
from agent.task_assigner import TaskAssignerAgent, Employee, Task, TaskPriority, TaskComplexity

# Create agent
agent = TaskAssignerAgent()

# Add employees
alice = Employee("emp1", "Alice Johnson", ["python", "django"], "senior", 40.0)
bob = Employee("emp2", "Bob Smith", ["javascript", "react"], "mid", 35.0)
agent.add_employee(alice)
agent.add_employee(bob)

# Add tasks
task1 = Task("task1", "Build API", "Develop REST API", ["python"], 16.0, TaskPriority.HIGH, TaskComplexity.MODERATE)
task2 = Task("task2", "Create UI", "Build React frontend", ["javascript"], 20.0, TaskPriority.HIGH, TaskComplexity.MODERATE)
agent.add_task(task1)
agent.add_task(task2)

# Assign tasks
assignments = agent.assign_tasks()
print(f"Assigned {len(assignments)} tasks")
```

### 2. CLI Interface

Run the interactive CLI:

```bash
cd agent
python task_assigner_cli.py --interactive
```

Or use with demo data:

```bash
python task_assigner_cli.py --demo
```

### 3. Portia Integration

Integrate with existing Portia project plans:

```python
from agent.task_integration import integrate_with_portia_plan

# After generating a Portia plan
portia_plan = generate_plan_dict(portia_client, idea_text)

# Integrate with task assignment
results = integrate_with_portia_plan(portia_plan)
print(f"Assigned {results['assignments']} tasks from {results['original_steps']} steps")
```

## Core Components

### Employee Class

Represents a team member with:
- **ID**: Unique identifier
- **Name**: Full name
- **Skills**: List of technical skills
- **Experience Level**: junior, mid, senior, or expert
- **Availability**: Hours per week available for work
- **Current Workload**: Currently assigned hours

### Task Class

Represents a work item with:
- **ID**: Unique identifier
- **Title**: Short description
- **Description**: Detailed description
- **Required Skills**: Skills needed to complete the task
- **Estimated Hours**: Time estimate for completion
- **Priority**: low, medium, high, or critical
- **Complexity**: simple, moderate, complex, or expert
- **Dependencies**: List of task IDs that must be completed first

### TaskAssignerAgent Class

Main agent that:
- Manages employees and tasks
- Calculates optimal assignments
- Balances workloads
- Handles dependencies and priorities

## Assignment Algorithm

The agent uses a sophisticated scoring system:

1. **Skill Match (40%)**: How well employee skills match task requirements
2. **Experience Match (30%)**: How well employee experience matches task complexity
3. **Availability Score (30%)**: How much time the employee has available

### Scoring Details

- **Skill Match**: Percentage of required skills the employee possesses
- **Experience Match**: 
  - Perfect match: 1.0
  - Overqualified: 0.8
  - Underqualified: Penalty based on gap
- **Availability**: Ratio of available time to task requirements

## Usage Examples

### Example 1: Software Development Team

```python
# Create development team
dev_team = [
    Employee("dev1", "Alice", ["python", "django", "postgresql"], "senior", 40.0),
    Employee("dev2", "Bob", ["javascript", "react", "node.js"], "mid", 35.0),
    Employee("dev3", "Carol", ["python", "machine_learning"], "expert", 30.0),
    Employee("dev4", "David", ["html", "css", "javascript"], "junior", 40.0)
]

# Create project tasks
project_tasks = [
    Task("task1", "Backend API", "Develop REST API", ["python", "django"], 16.0, TaskPriority.HIGH, TaskComplexity.MODERATE),
    Task("task2", "Frontend", "Build React app", ["javascript", "react"], 20.0, TaskPriority.HIGH, TaskComplexity.MODERATE),
    Task("task3", "ML Model", "Implement ML algorithm", ["python", "machine_learning"], 25.0, TaskPriority.CRITICAL, TaskComplexity.EXPERT),
    Task("task4", "UI Design", "Design mockups", ["html", "css"], 8.0, TaskPriority.LOW, TaskComplexity.SIMPLE)
]

# Assign tasks
agent = TaskAssignerAgent()
for emp in dev_team:
    agent.add_employee(emp)
for task in project_tasks:
    agent.add_task(task)

assignments = agent.assign_tasks()
```

### Example 2: Marketing Campaign

```python
# Create marketing team
marketing_team = [
    Employee("mkt1", "Eva", ["content_writing", "social_media"], "senior", 35.0),
    Employee("mkt2", "Frank", ["graphic_design", "adobe_creative"], "mid", 40.0),
    Employee("mkt3", "Grace", ["analytics", "seo"], "senior", 30.0)
]

# Create campaign tasks
campaign_tasks = [
    Task("task1", "Content Creation", "Write blog posts", ["content_writing"], 12.0, TaskPriority.HIGH, TaskComplexity.MODERATE),
    Task("task2", "Visual Design", "Create graphics", ["graphic_design"], 16.0, TaskPriority.HIGH, TaskComplexity.MODERATE),
    Task("task3", "SEO Analysis", "Optimize content", ["analytics", "seo"], 8.0, TaskPriority.MEDIUM, TaskComplexity.COMPLEX)
]

# Assign tasks
agent = TaskAssignerAgent()
for emp in marketing_team:
    agent.add_employee(emp)
for task in campaign_tasks:
    agent.add_task(task)

assignments = agent.assign_tasks()
```

## File Structure

```
agent/
├── task_assigner.py          # Core task assignment logic
├── task_assigner_cli.py      # Command-line interface
├── task_integration.py       # Portia integration module
├── planner.py                # Existing Portia planner
└── README_TASK_ASSIGNER.md   # This file
```

## Output Files

### Task Assignments

```json
{
  "assignments": [
    {
      "task_id": "task_001",
      "employee_id": "emp1",
      "assigned_hours": 16.0,
      "start_date": null,
      "end_date": null
    }
  ],
  "summary": {
    "total_tasks": 6,
    "total_employees": 5,
    "assigned_tasks": 6,
    "unassigned_tasks": 0,
    "employee_workloads": [
      {
        "employee_id": "emp1",
        "employee_name": "Alice Johnson",
        "current_workload": 16.0,
        "availability": 40.0,
        "utilization_percentage": 40.0
      }
    ]
  }
}
```

### Project Data

```json
{
  "employees": [
    {
      "id": "emp1",
      "name": "Alice Johnson",
      "skills": ["python", "django", "postgresql"],
      "experience_level": "senior",
      "availability_hours": 40.0,
      "current_workload": 0.0
    }
  ],
  "tasks": [
    {
      "id": "task_001",
      "title": "Backend API Development",
      "description": "Develop REST API endpoints",
      "required_skills": ["python", "django"],
      "estimated_hours": 16.0,
      "priority": "high",
      "complexity": "moderate",
      "dependencies": []
    }
  ]
}
```

## Advanced Features

### Custom Skill Definitions

You can extend the skill inference system:

```python
# Add custom skill keywords
skill_keywords = {
    "custom_skill": ["keyword1", "keyword2", "keyword3"]
}
```

### Workload Constraints

Set maximum workload limits:

```python
# Employee with limited availability
limited_emp = Employee("emp1", "Alice", ["python"], "senior", 20.0)  # Only 20 hours/week
```

### Task Dependencies

Handle complex project dependencies:

```python
# Task that depends on others
dependent_task = Task(
    "task3", "Integration Testing", "Test complete system",
    ["testing"], 8.0, TaskPriority.HIGH, TaskComplexity.MODERATE,
    dependencies=["task1", "task2"]  # Must complete tasks 1 and 2 first
)
```

## Best Practices

1. **Skill Naming**: Use consistent skill names across employees and tasks
2. **Time Estimates**: Provide realistic time estimates for accurate workload distribution
3. **Priority Setting**: Use priority levels to ensure critical tasks are assigned first
4. **Dependency Management**: Properly define task dependencies for complex projects
5. **Regular Updates**: Update employee availability and skills as they change

## Troubleshooting

### Common Issues

1. **No Tasks Assigned**: Check employee skills and availability
2. **Unbalanced Workloads**: Verify time estimates and availability settings
3. **Circular Dependencies**: Ensure task dependencies don't create loops

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

To extend the task assignment agent:

1. Add new scoring factors to `_find_best_employee_for_task()`
2. Extend skill inference in `infer_skills_from_description()`
3. Add new task types or employee attributes
4. Implement additional export formats

## License

This project is part of the Portia PM Agent system.
