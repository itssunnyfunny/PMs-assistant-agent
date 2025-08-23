"""
Product Manager Planning Agent

This agent provides a conversational interface for Product Managers to:
1. Input product requirements
2. Generate initial project plans with milestones
3. Iteratively edit plans through conversational feedback
4. Store final approved plans in structured format
5. Use Portia's memory to maintain conversation context
"""

import json
import yaml
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

class PlanStatus(Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    ARCHIVED = "archived"

class MilestoneType(Enum):
    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    LAUNCH = "launch"

@dataclass
class Milestone:
    id: str
    title: str
    description: str
    type: MilestoneType
    target_date: datetime
    dependencies: List[str] = None
    deliverables: List[str] = None
    success_criteria: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type.value,
            "target_date": self.target_date.isoformat(),
            "dependencies": self.dependencies or [],
            "deliverables": self.dependencies or [],
            "success_criteria": self.success_criteria or []
        }

@dataclass
class ProjectPlan:
    id: str
    title: str
    description: str
    requirements: List[str]
    milestones: List[Milestone]
    estimated_duration_days: int
    status: PlanStatus
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "requirements": self.requirements,
            "milestones": [m.to_dict() for m in self.milestones],
            "estimated_duration_days": self.estimated_duration_days,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by
        }

class PMPlanningAgent:
    def __init__(self, portia_client=None):
        self.portia_client = portia_client
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_plan: Optional[ProjectPlan] = None
        self.plan_templates = self._load_plan_templates()
    
    def _load_plan_templates(self) -> Dict[str, Any]:
        """Load predefined plan templates for different project types"""
        return {
            "web_app": {
                "milestones": [
                    {"type": "planning", "duration_days": 7, "title": "Requirements & Design"},
                    {"type": "development", "duration_days": 21, "title": "Core Development"},
                    {"type": "testing", "duration_days": 7, "title": "Testing & QA"},
                    {"type": "deployment", "duration_days": 3, "title": "Deployment"},
                    {"type": "launch", "duration_days": 2, "title": "Launch & Monitoring"}
                ]
            },
            "mobile_app": {
                "milestones": [
                    {"type": "planning", "duration_days": 10, "title": "UX/UI Design & Planning"},
                    {"type": "development", "duration_days": 35, "title": "App Development"},
                    {"type": "testing", "duration_days": 14, "title": "Testing & Beta"},
                    {"type": "deployment", "duration_days": 7, "title": "App Store Submission"},
                    {"type": "launch", "duration_days": 3, "title": "Launch & Marketing"}
                ]
            },
            "api_service": {
                "milestones": [
                    {"type": "planning", "duration_days": 5, "title": "API Design & Architecture"},
                    {"type": "development", "duration_days": 14, "title": "Backend Development"},
                    {"type": "testing", "duration_days": 7, "title": "API Testing"},
                    {"type": "deployment", "duration_days": 3, "title": "Infrastructure Setup"},
                    {"type": "launch", "duration_days": 2, "title": "Documentation & Launch"}
                ]
            }
        }
    
    def start_planning_conversation(self, initial_requirements: str) -> str:
        """Start a new planning conversation with initial requirements"""
        self.conversation_history = []
        
        # Add initial requirements to conversation
        self._add_to_conversation("pm", initial_requirements)
        
        # Generate initial response
        response = self._generate_planning_response(initial_requirements)
        self._add_to_conversation("agent", response)
        
        return response
    
    def _add_to_conversation(self, speaker: str, message: str):
        """Add a message to the conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": speaker,
            "message": message
        })
    
    def _generate_planning_response(self, requirements: str) -> str:
        """Generate a response based on the requirements and conversation context"""
        if not self.current_plan:
            # First time - generate initial plan
            return self._generate_initial_plan(requirements)
        else:
            # Continue conversation based on context
            return self._continue_planning_conversation(requirements)
    
    def _generate_initial_plan(self, requirements: str) -> str:
        """Generate the initial project plan based on requirements"""
        # Analyze requirements to determine project type
        project_type = self._classify_project_type(requirements)
        
        # Create initial plan
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_date = datetime.now()
        
        # Generate milestones based on project type
        milestones = self._generate_milestones(project_type, start_date)
        
        # Create project plan
        self.current_plan = ProjectPlan(
            id=plan_id,
            title=f"Project Plan for {requirements[:50]}...",
            description=requirements,
            requirements=self._extract_requirements(requirements),
            milestones=milestones,
            estimated_duration_days=sum(m.get("duration_days", 0) for m in self.plan_templates.get(project_type, {}).get("milestones", [])),
            status=PlanStatus.DRAFT,
            created_at=start_date,
            updated_at=start_date
        )
        
        return self._format_plan_summary()
    
    def _classify_project_type(self, requirements: str) -> str:
        """Classify the project type based on requirements"""
        requirements_lower = requirements.lower()
        
        if any(word in requirements_lower for word in ["mobile", "app", "ios", "android"]):
            return "mobile_app"
        elif any(word in requirements_lower for word in ["api", "service", "backend", "microservice"]):
            return "api_service"
        else:
            return "web_app"  # Default
    
    def _generate_milestones(self, project_type: str, start_date: datetime) -> List[Milestone]:
        """Generate milestones based on project type and start date"""
        milestones = []
        current_date = start_date
        
        template = self.plan_templates.get(project_type, {})
        
        for i, milestone_info in enumerate(template.get("milestones", [])):
            milestone = Milestone(
                id=f"milestone_{i+1:02d}",
                title=milestone_info["title"],
                description=f"Complete {milestone_info['title']} phase",
                type=MilestoneType(milestone_info["type"]),
                target_date=current_date + timedelta(days=milestone_info["duration_days"]),
                dependencies=[f"milestone_{i:02d}"] if i > 0 else [],
                deliverables=[f"Deliverable for {milestone_info['title']}"],
                success_criteria=[f"Successfully complete {milestone_info['title']}"]
            )
            milestones.append(milestone)
            current_date = milestone.target_date
        
        return milestones
    
    def _extract_requirements(self, requirements_text: str) -> List[str]:
        """Extract structured requirements from text"""
        # Simple extraction - split by common delimiters
        delimiters = ["\n", ".", ";", ","]
        requirements = []
        
        for delimiter in delimiters:
            if delimiter in requirements_text:
                parts = requirements_text.split(delimiter)
                requirements = [req.strip() for req in parts if req.strip()]
                break
        
        if not requirements:
            requirements = [requirements_text.strip()]
        
        return requirements[:10]  # Limit to 10 requirements
    
    def _format_plan_summary(self) -> str:
        """Format the current plan as a readable summary"""
        if not self.current_plan:
            return "No plan available."
        
        plan = self.current_plan
        summary = f"""
🎯 **Project Plan Generated: {plan.title}**

📋 **Requirements:**
"""
        
        for i, req in enumerate(plan.requirements, 1):
            summary += f"{i}. {req}\n"
        
        summary += f"""
⏱️ **Estimated Duration:** {plan.estimated_duration_days} days
📅 **Milestones:**
"""
        
        for milestone in plan.milestones:
            summary += f"• {milestone.title} - {milestone.target_date.strftime('%Y-%m-%d')}\n"
        
        summary += """
💬 **You can now:**
- Ask me to modify any part of the plan
- Add new requirements or milestones
- Adjust timelines or priorities
- Get detailed information about specific milestones
- Approve the plan when ready

What would you like to adjust or discuss?
"""
        
        return summary
    
    def process_feedback(self, feedback: str) -> str:
        """Process feedback from the PM and update the plan accordingly"""
        if not self.current_plan:
            return "No active plan to modify. Please start a new planning conversation."
        
        # Add feedback to conversation
        self._add_to_conversation("pm", feedback)
        
        # Process the feedback and update plan
        response = self._process_feedback_and_update(feedback)
        
        # Add response to conversation
        self._add_to_conversation("agent", response)
        
        return response
    
    def _process_feedback_and_update(self, feedback: str) -> str:
        """Process feedback and update the plan accordingly"""
        feedback_lower = feedback.lower()
        
        # Update timestamp
        self.current_plan.updated_at = datetime.now()
        
        # Handle different types of feedback
        if any(word in feedback_lower for word in ["add", "new", "include"]):
            return self._handle_add_request(feedback)
        elif any(word in feedback_lower for word in ["change", "modify", "update", "edit"]):
            return self._handle_modify_request(feedback)
        elif any(word in feedback_lower for word in ["remove", "delete", "exclude"]):
            return self._handle_remove_request(feedback)
        elif any(word in feedback_lower for word in ["timeline", "schedule", "duration"]):
            return self._handle_timeline_request(feedback)
        elif any(word in feedback_lower for word in ["approve", "final", "done", "complete"]):
            return self._handle_approval_request(feedback)
        else:
            return self._handle_general_feedback(feedback)
    
    def _handle_add_request(self, feedback: str) -> str:
        """Handle requests to add new elements to the plan"""
        # Simple keyword-based addition
        if "requirement" in feedback.lower():
            new_req = feedback.replace("add requirement", "").replace("add", "").strip()
            if new_req:
                self.current_plan.requirements.append(new_req)
                return f"✅ Added new requirement: {new_req}\n\n{self._format_plan_summary()}"
        
        if "milestone" in feedback.lower():
            # Extract milestone information
            milestone_title = feedback.replace("add milestone", "").replace("add", "").strip()
            if milestone_title:
                new_milestone = Milestone(
                    id=f"milestone_{len(self.current_plan.milestones) + 1:02d}",
                    title=milestone_title,
                    description=f"Complete {milestone_title}",
                    type=MilestoneType.PLANNING,
                    target_date=datetime.now() + timedelta(days=7)
                )
                self.current_plan.milestones.append(new_milestone)
                return f"✅ Added new milestone: {milestone_title}\n\n{self._format_plan_summary()}"
        
        return "I understand you want to add something. Could you be more specific about what you'd like to add?"
    
    def _handle_modify_request(self, feedback: str) -> str:
        """Handle requests to modify existing plan elements"""
        return "I understand you want to modify something. Could you specify what you'd like to change?"
    
    def _handle_remove_request(self, feedback: str) -> str:
        """Handle requests to remove elements from the plan"""
        return "I understand you want to remove something. Could you specify what you'd like to remove?"
    
    def _handle_timeline_request(self, feedback: str) -> str:
        """Handle requests related to timeline and scheduling"""
        return "I understand you want to adjust the timeline. Could you specify what changes you'd like to make?"
    
    def _handle_approval_request(self, feedback: str) -> str:
        """Handle plan approval requests"""
        self.current_plan.status = PlanStatus.APPROVED
        self.current_plan.approved_at = datetime.now()
        self.current_plan.approved_by = "Product Manager"
        
        return f"""
🎉 **Plan Approved!**

Your project plan has been approved and is ready for task assignment.

📊 **Final Plan Summary:**
{self._format_plan_summary()}

The plan is now ready to be passed to the Task Assignment Agent for employee allocation.
"""
    
    def _handle_general_feedback(self, feedback: str) -> str:
        """Handle general feedback and questions"""
        return f"""
I received your feedback: "{feedback}"

I'm here to help you refine your project plan. You can:
- Ask me to add new requirements or milestones
- Modify existing elements
- Adjust timelines or priorities
- Get more details about any part of the plan
- Approve the plan when you're satisfied

What would you like to do next?
"""
    
    def _continue_planning_conversation(self, requirements: str) -> str:
        """Continue the planning conversation based on context"""
        # This would use Portia's reasoning to generate contextual responses
        return "I'm here to help you refine your project plan. What would you like to adjust or discuss?"
    
    def get_current_plan(self) -> Optional[ProjectPlan]:
        """Get the current project plan"""
        return self.current_plan
    
    def save_plan(self, filename: str, format: str = "json"):
        """Save the current plan to a file"""
        if not self.current_plan:
            raise ValueError("No plan to save")
        
        plan_data = self.current_plan.to_dict()
        
        if format.lower() == "yaml":
            with open(filename, 'w', encoding='utf-8') as f:
                yaml.dump(plan_data, f, default_flow_style=False, indent=2)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, indent=2, default=str)
        
        return f"Plan saved to {filename}"
    
    def load_plan(self, filename: str, format: str = "json"):
        """Load a plan from a file"""
        if format.lower() == "yaml":
            with open(filename, 'r', encoding='utf-8') as f:
                plan_data = yaml.safe_load(f)
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
        
        # Reconstruct the plan object
        milestones = []
        for m_data in plan_data.get("milestones", []):
            milestone = Milestone(
                id=m_data["id"],
                title=m_data["title"],
                description=m_data["description"],
                type=MilestoneType(m_data["type"]),
                target_date=datetime.fromisoformat(m_data["target_date"]),
                dependencies=m_data.get("dependencies", []),
                deliverables=m_data.get("deliverables", []),
                success_criteria=m_data.get("success_criteria", [])
            )
            milestones.append(milestone)
        
        self.current_plan = ProjectPlan(
            id=plan_data["id"],
            title=plan_data["title"],
            description=plan_data["description"],
            requirements=plan_data["requirements"],
            milestones=milestones,
            estimated_duration_days=plan_data["estimated_duration_days"],
            status=PlanStatus(plan_data["status"]),
            created_at=datetime.fromisoformat(plan_data["created_at"]),
            updated_at=datetime.fromisoformat(plan_data["updated_at"]),
            approved_at=datetime.fromisoformat(plan_data["approved_at"]) if plan_data.get("approved_at") else None,
            approved_by=plan_data.get("approved_by")
        )
        
        return f"Plan loaded from {filename}"
    
    def load_plan_from_dict(self, plan_data: Dict[str, Any]) -> str:
        """Load a plan from a dictionary (for workflow restoration)"""
        try:
            # Reconstruct milestones
            milestones = []
            for m_data in plan_data.get("milestones", []):
                milestone = Milestone(
                    id=m_data["id"],
                    title=m_data["title"],
                    description=m_data["description"],
                    type=MilestoneType(m_data["type"]),
                    target_date=datetime.fromisoformat(m_data["target_date"]),
                    dependencies=m_data.get("dependencies", []),
                    deliverables=m_data.get("deliverables", []),
                    success_criteria=m_data.get("success_criteria", [])
                )
                milestones.append(milestone)
            
            # Create project plan
            self.current_plan = ProjectPlan(
                id=plan_data["id"],
                title=plan_data["title"],
                description=plan_data["description"],
                requirements=plan_data["requirements"],
                milestones=milestones,
                estimated_duration_days=plan_data["estimated_duration_days"],
                status=PlanStatus(plan_data["status"]),
                created_at=datetime.fromisoformat(plan_data["created_at"]),
                updated_at=datetime.fromisoformat(plan_data["updated_at"]),
                approved_at=datetime.fromisoformat(plan_data["approved_at"]) if plan_data.get("approved_at") else None,
                approved_by=plan_data.get("approved_by")
            )
            
            return f"Plan loaded from dictionary: {self.current_plan.title}"
            
        except Exception as e:
            return f"Error loading plan from dictionary: {e}"

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
        self.current_plan = None
