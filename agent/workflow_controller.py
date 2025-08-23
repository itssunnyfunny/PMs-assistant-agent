"""
Main Workflow Orchestration Controller

This controller manages the complete workflow from project planning to task assignment:
1. Initializes both agents with UV-managed dependencies
2. Maintains state between planning and assignment phases
3. Handles environment configurations (API keys, email credentials)
4. Provides CLI/Web interface for the Product Manager
5. Manages persistent storage for plans and assignments
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# Import our agents
from .pm_planning_agent import PMPlanningAgent, ProjectPlan, PlanStatus
from .task_assigner import TaskAssignerAgent, Employee, Task, TaskPriority, TaskComplexity
from .task_integration import integrate_with_portia_plan

class WorkflowState:
    """Represents the current state of the workflow"""
    
    PLANNING = "planning"
    PLANNING_COMPLETE = "planning_complete"
    ASSIGNMENT = "assignment"
    ASSIGNMENT_COMPLETE = "assignment_complete"
    COMPLETED = "completed"

class WorkflowController:
    def __init__(self, config_file: str = "workflow_config.yaml"):
        self.config = self._load_config(config_file)
        self.state = WorkflowState.PLANNING
        self.pm_agent = PMPlanningAgent()
        self.task_agent = TaskAssignerAgent()
        self.current_plan: Optional[ProjectPlan] = None
        self.workflow_history: List[Dict[str, Any]] = []
        self.storage_dir = Path(self.config.get("storage_dir", "workflow_data"))
        self.storage_dir.mkdir(exist_ok=True)
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        default_config = {
            "storage_dir": "workflow_data",
            "portia_api_key": os.getenv("PORTIA_API_KEY", ""),
            "email_enabled": False,
            "email_smtp_server": "",
            "email_username": "",
            "email_password": "",
            "database_enabled": False,
            "database_url": "",
            "log_level": "INFO",
            "auto_save": True,
            "backup_enabled": True
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f) or {}
                    default_config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
        
        return default_config
    
    def start_new_project(self, project_title: str, requirements: str) -> str:
        """Start a new project workflow"""
        self.state = WorkflowState.PLANNING
        self.current_plan = None
        
        # Start planning conversation
        response = self.pm_agent.start_planning_conversation(requirements)
        
        # Log workflow event
        self._log_workflow_event("project_started", {
            "project_title": project_title,
            "requirements": requirements,
            "response": response
        })
        
        return response
    
    def process_planning_feedback(self, feedback: str) -> str:
        """Process feedback during the planning phase"""
        if self.state != WorkflowState.PLANNING:
            return "Planning phase is not active. Current state: " + self.state
        
        response = self.pm_agent.process_feedback(feedback)
        
        # Check if plan was approved
        current_plan = self.pm_agent.get_current_plan()
        if current_plan and current_plan.status == PlanStatus.APPROVED:
            self.state = WorkflowState.PLANNING_COMPLETE
            self.current_plan = current_plan
            self._log_workflow_event("plan_approved", {
                "plan_id": current_plan.id,
                "plan_title": current_plan.title
            })
        
        # Auto-save if enabled
        if self.config.get("auto_save", True):
            self._auto_save_workflow()
        
        return response
    
    def transition_to_assignment(self) -> str:
        """Transition from planning to task assignment phase"""
        if self.state != WorkflowState.PLANNING_COMPLETE:
            return f"Cannot transition to assignment. Current state: {self.state}. Plan must be approved first."
        
        if not self.current_plan:
            return "No approved plan available for task assignment."
        
        self.state = WorkflowState.ASSIGNMENT
        
        # Convert plan milestones to tasks
        tasks = self._convert_milestones_to_tasks()
        
        # Add tasks to task agent
        for task in tasks:
            self.task_agent.add_task(task)
        
        # Load sample employees (in real scenario, this would come from database)
        employees = self._load_sample_employees()
        for employee in employees:
            self.task_agent.add_employee(employee)
        
        # Log transition
        self._log_workflow_event("transitioned_to_assignment", {
            "plan_id": self.current_plan.id,
            "tasks_count": len(tasks),
            "employees_count": len(employees)
        })
        
        return f"""
🔄 **Transitioned to Task Assignment Phase**

✅ Plan: {self.current_plan.title}
📋 Tasks: {len(tasks)} milestones converted to tasks
👥 Team: {len(employees)} employees loaded
⏱️ Estimated Duration: {self.current_plan.estimated_duration_days} days

Ready to assign tasks to team members!
"""
    
    def _convert_milestones_to_tasks(self) -> List[Task]:
        """Convert approved plan milestones to tasks for assignment"""
        if not self.current_plan:
            return []
        
        tasks = []
        for milestone in self.current_plan.milestones:
            # Determine task priority based on milestone type
            priority = self._get_priority_from_milestone_type(milestone.type)
            
            # Determine complexity based on milestone type
            complexity = self._get_complexity_from_milestone_type(milestone.type)
            
            # Estimate hours based on milestone type and duration
            estimated_hours = self._estimate_hours_from_milestone(milestone)
            
            # Extract required skills from milestone description
            required_skills = self._extract_skills_from_milestone(milestone)
            
            task = Task(
                id=f"task_{milestone.id}",
                title=milestone.title,
                description=milestone.description,
                required_skills=required_skills,
                estimated_hours=estimated_hours,
                priority=priority,
                complexity=complexity,
                dependencies=milestone.dependencies
            )
            tasks.append(task)
        
        return tasks
    
    def _get_priority_from_milestone_type(self, milestone_type) -> TaskPriority:
        """Map milestone type to task priority"""
        priority_mapping = {
            "planning": TaskPriority.HIGH,
            "development": TaskPriority.HIGH,
            "testing": TaskPriority.MEDIUM,
            "deployment": TaskPriority.CRITICAL,
            "launch": TaskPriority.CRITICAL
        }
        return priority_mapping.get(milestone_type.value, TaskPriority.MEDIUM)
    
    def _get_complexity_from_milestone_type(self, milestone_type) -> TaskComplexity:
        """Map milestone type to task complexity"""
        complexity_mapping = {
            "planning": TaskComplexity.MODERATE,
            "development": TaskComplexity.COMPLEX,
            "testing": TaskComplexity.MODERATE,
            "deployment": TaskComplexity.MODERATE,
            "launch": TaskComplexity.SIMPLE
        }
        return complexity_mapping.get(milestone_type.value, TaskComplexity.MODERATE)
    
    def _estimate_hours_from_milestone(self, milestone) -> float:
        """Estimate task hours based on milestone information"""
        # Base estimation: 8 hours per day
        base_hours_per_day = 8.0
        
        # Get milestone duration from the plan templates
        milestone_type = milestone.type.value
        duration_days = 0
        
        # Find duration from templates
        for template_name, template_data in self.pm_agent.plan_templates.items():
            for m in template_data.get("milestones", []):
                if m["type"] == milestone_type:
                    duration_days = m.get("duration_days", 1)
                    break
            if duration_days > 0:
                break
        
        if duration_days == 0:
            duration_days = 1  # Default to 1 day
        
        return duration_days * base_hours_per_day
    
    def _extract_skills_from_milestone(self, milestone) -> List[str]:
        """Extract required skills from milestone description"""
        description_lower = milestone.description.lower()
        skills = []
        
        # Simple skill extraction based on keywords
        skill_keywords = {
            "planning": ["project_management", "planning"],
            "development": ["programming", "development"],
            "testing": ["testing", "qa"],
            "deployment": ["devops", "deployment"],
            "launch": ["marketing", "launch"]
        }
        
        milestone_type = milestone.type.value
        if milestone_type in skill_keywords:
            skills.extend(skill_keywords[milestone_type])
        
        return skills
    
    def _load_sample_employees(self) -> List[Employee]:
        """Load sample employees for demonstration"""
        from .task_integration import create_sample_team
        return create_sample_team()
    
    def assign_tasks(self) -> str:
        """Assign tasks to employees"""
        if self.state != WorkflowState.ASSIGNMENT:
            return f"Cannot assign tasks. Current state: {self.state}"
        
        assignments = self.task_agent.assign_tasks()
        
        if assignments:
            self.state = WorkflowState.ASSIGNMENT_COMPLETE
            
            # Log successful assignment
            self._log_workflow_event("tasks_assigned", {
                "assignments_count": len(assignments),
                "plan_id": self.current_plan.id if self.current_plan else None
            })
            
            # Auto-save if enabled
            if self.config.get("auto_save", True):
                self._auto_save_workflow()
            
            return f"""
✅ **Task Assignment Complete!**

📊 **Summary:**
- Total Tasks: {len(self.task_agent.tasks)}
- Assigned Tasks: {len(assignments)}
- Team Members: {len(self.task_agent.employees)}

🎯 **Next Steps:**
- Review assignments in detail
- Export assignment data
- Monitor progress
- Generate reports
"""
        else:
            return "No tasks could be assigned. Please check employee availability and skill requirements."
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        status = {
            "state": self.state,
            "current_plan": self.current_plan.to_dict() if self.current_plan else None,
            "planning_agent_status": "active" if self.pm_agent.current_plan else "inactive",
            "task_agent_status": "active" if self.task_agent.tasks else "inactive",
            "workflow_history": self.workflow_history[-10:],  # Last 10 events
            "storage_directory": str(self.storage_dir),
            "auto_save": self.config.get("auto_save", True)
        }
        
        if self.current_plan:
            status["plan_approval_status"] = self.current_plan.status.value
            status["estimated_duration"] = f"{self.current_plan.estimated_duration_days} days"
        
        return status
    
    def export_workflow_data(self, format: str = "json") -> str:
        """Export complete workflow data"""
        if not self.current_plan:
            return "No workflow data to export. Start a project first."
        
        # Prepare export data
        export_data = {
            "workflow_info": {
                "state": self.state,
                "created_at": datetime.now().isoformat(),
                "config": self.config
            },
            "project_plan": self.current_plan.to_dict(),
            "task_assignments": self.task_agent.get_assignment_summary() if self.task_agent.assignments else None,
            "conversation_history": self.pm_agent.get_conversation_history(),
            "workflow_history": self.workflow_history
        }
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workflow_export_{timestamp}.{format}"
        filepath = self.storage_dir / filename
        
        # Export based on format
        if format.lower() == "yaml":
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(export_data, f, default_flow_style=False, indent=2)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
        
        return f"Workflow data exported to {filepath}"
    
    def save_workflow(self, filename: str = None) -> str:
        """Save current workflow state"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_save_{timestamp}.json"
        
        filepath = self.storage_dir / filename
        
        save_data = {
            "state": self.state,
            "current_plan": self.current_plan.to_dict() if self.current_plan else None,
            "pm_agent_data": {
                "conversation_history": self.pm_agent.get_conversation_history(),
                "current_plan": self.pm_agent.get_current_plan().to_dict() if self.pm_agent.get_current_plan() else None
            },
            "task_agent_data": {
                "employees": [emp.to_dict() for emp in self.task_agent.employees],
                "tasks": [task.to_dict() for task in self.task_agent.tasks],
                "assignments": [ass.to_dict() for ass in self.task_agent.assignments]
            },
            "workflow_history": self.workflow_history,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        return f"Workflow saved to {filepath}"
    
    def load_workflow(self, filename: str) -> str:
        """Load workflow from saved file"""
        filepath = self.storage_dir / filename
        
        if not filepath.exists():
            return f"Workflow file {filename} not found."
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Restore state
            self.state = save_data.get("state", WorkflowState.PLANNING)
            
            # Restore PM agent data
            if save_data.get("pm_agent_data", {}).get("current_plan"):
                self.pm_agent.load_plan_from_dict(save_data["pm_agent_data"]["current_plan"])
                self.current_plan = self.pm_agent.get_current_plan()
            
            # Restore task agent data
            task_data = save_data.get("task_agent_data", {})
            if task_data.get("employees"):
                for emp_data in task_data["employees"]:
                    employee = Employee(
                        id=emp_data["id"],
                        name=emp_data["name"],
                        skills=emp_data["skills"],
                        experience_level=emp_data["experience_level"],
                        availability_hours=emp_data["availability_hours"]
                    )
                    self.task_agent.add_employee(employee)
            
            if task_data.get("tasks"):
                for task_data_item in task_data["tasks"]:
                    task = Task(
                        id=task_data_item["id"],
                        title=task_data_item["title"],
                        description=task_data_item["description"],
                        required_skills=task_data_item["required_skills"],
                        estimated_hours=task_data_item["estimated_hours"],
                        priority=TaskPriority(task_data_item["priority"]),
                        complexity=TaskComplexity(task_data_item["complexity"]),
                        dependencies=task_data_item.get("dependencies", [])
                    )
                    self.task_agent.add_task(task)
            
            # Restore workflow history
            self.workflow_history = save_data.get("workflow_history", [])
            
            return f"Workflow loaded from {filename}"
            
        except Exception as e:
            return f"Error loading workflow: {e}"
    
    def _log_workflow_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log a workflow event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "event_data": event_data,
            "state": self.state
        }
        self.workflow_history.append(event)
    
    def _auto_save_workflow(self):
        """Automatically save workflow state"""
        if self.config.get("auto_save", True):
            try:
                self.save_workflow("workflow_autosave.json")
            except Exception as e:
                print(f"Warning: Auto-save failed: {e}")
    
    def get_help(self) -> str:
        """Get help information for the workflow"""
        return """
🔄 **Workflow Controller Help**

**Available Commands:**
1. `start_new_project(title, requirements)` - Start a new project
2. `process_planning_feedback(feedback)` - Provide feedback during planning
3. `transition_to_assignment()` - Move to task assignment phase
4. `assign_tasks()` - Assign tasks to employees
5. `get_workflow_status()` - Check current status
6. `export_workflow_data(format)` - Export data (json/yaml)
7. `save_workflow(filename)` - Save current state
8. `load_workflow(filename)` - Load saved state
9. `get_help()` - Show this help

**Workflow States:**
- PLANNING: Creating and refining project plan
- PLANNING_COMPLETE: Plan approved, ready for assignment
- ASSIGNMENT: Assigning tasks to team members
- ASSIGNMENT_COMPLETE: Tasks assigned, ready for execution
- COMPLETED: Project completed

**Usage Example:**
```python
controller = WorkflowController()
response = controller.start_new_project("My App", "Build a mobile app for task management")
print(response)
```
"""
