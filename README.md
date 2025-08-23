# Portia PM Agent

A comprehensive AI-powered project management system that combines conversational project planning with intelligent task assignment.

## 🚀 Features

### 1. **Product Manager Planning Agent**
- **Conversational Interface**: Natural language project planning with iterative feedback
- **Smart Templates**: Pre-built templates for web apps, mobile apps, and API services
- **Milestone Management**: Automatic milestone generation with realistic timelines
- **Interactive Editing**: Modify plans through natural conversation
- **Plan Approval**: Structured approval workflow with status tracking

### 2. **Task Assignment Agent**
- **Intelligent Matching**: AI-powered task-to-employee assignment based on skills and availability
- **Workload Balancing**: Automatic distribution of work across team members
- **Skill Analysis**: Sophisticated skill matching and experience level consideration
- **Dependency Handling**: Respects task dependencies and priorities
- **Export Capabilities**: JSON/YAML export for integration with other tools

### 3. **Main Workflow Orchestration**
- **Unified Interface**: Single controller managing both planning and assignment phases
- **State Management**: Maintains workflow state between phases
- **Configuration Management**: Environment-based configuration with YAML support
- **Persistent Storage**: Automatic saving and loading of workflow state
- **CLI Interface**: User-friendly command-line interface for Product Managers

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Workflow Controller                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │ PM Planning     │    │ Task Assignment Agent           │ │
│  │ Agent           │    │                                 │ │
│  │                 │    │ • Employee Management           │ │
│  │ • Requirements  │    │ • Task Assignment               │ │
│  │ • Milestones    │    │ • Workload Balancing            │ │
│  │ • Conversations │    │ • Skill Matching                │ │
│  │ • Plan Approval │    │ • Export/Import                 │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd portia-pm-agent

# Install dependencies
pip install -r requirements.txt
# or using uv
uv sync
```

### Basic Usage

```bash
# Interactive mode (recommended)
python main.py

# Demo mode
python main.py --demo

# Quick start with project idea
python main.py --idea "Build a task management app"
```

### Interactive Workflow

1. **Start New Project**: Enter project title and requirements
2. **Conversational Planning**: Refine your plan through natural conversation
3. **Approve Plan**: When satisfied, approve the plan
4. **Task Assignment**: Automatically convert milestones to tasks
5. **Team Allocation**: AI assigns tasks to best-suited team members
6. **Export Results**: Save assignments and project data

## 📋 Usage Examples

### Example 1: Web Application Project

```python
from agent.workflow_controller import WorkflowController

# Initialize controller
controller = WorkflowController()

# Start project
response = controller.start_new_project(
    "E-commerce Platform",
    "Build a modern e-commerce platform with user authentication, product catalog, and payment processing"
)

# Provide feedback
controller.process_planning_feedback("Add requirement: Mobile responsive design")
controller.process_planning_feedback("Add milestone: Security audit phase")

# Approve plan
controller.process_planning_feedback("Approve plan")

# Move to task assignment
controller.transition_to_assignment()

# Assign tasks
controller.assign_tasks()
```

### Example 2: Mobile App Development

```python
# The system automatically detects mobile app requirements
# and applies appropriate templates and timelines

controller.start_new_project(
    "Task Management App",
    "Create an iOS and Android app for personal task management with cloud sync"
)

# System automatically:
# - Classifies as mobile_app project type
# - Generates appropriate milestones (UX/UI, Development, Testing, App Store)
# - Sets realistic timelines (35+ days for development)
```

## 🔧 Configuration

### Environment Variables

```bash
export PORTIA_API_KEY="your-portia-api-key"
export WORKFLOW_CONFIG_PATH="custom_config.yaml"
```

### Configuration File (workflow_config.yaml)

```yaml
# Storage and Data Management
storage_dir: "workflow_data"
auto_save: true
backup_enabled: true

# Portia Integration
portia_api_key: ""  # Set via environment variable

# Email Notifications
email_enabled: false
email_smtp_server: "smtp.gmail.com"

# Workflow Settings
auto_transition_to_assignment: false
default_export_format: "json"
```

## 📁 Project Structure

```
portia-pm-agent/
├── agent/
│   ├── pm_planning_agent.py      # Product Manager Planning Agent
│   ├── task_assigner.py          # Task Assignment Agent
│   ├── task_assigner_cli.py      # CLI for task assignment
│   ├── task_integration.py       # Portia integration utilities
│   ├── workflow_controller.py    # Main workflow orchestration
│   ├── planner.py                # Legacy Portia planner
│   └── README_TASK_ASSIGNER.md   # Task assignment documentation
├── workflow_data/                 # Persistent storage directory
├── main.py                       # Main entry point
├── workflow_config.yaml          # Configuration file
├── pyproject.toml               # Project dependencies
└── README.md                    # This file
```

## 🔄 Workflow States

1. **PLANNING**: Creating and refining project plan
2. **PLANNING_COMPLETE**: Plan approved, ready for assignment
3. **ASSIGNMENT**: Assigning tasks to team members
4. **ASSIGNMENT_COMPLETE**: Tasks assigned, ready for execution
5. **COMPLETED**: Project completed

## 📊 Data Export

### Supported Formats
- **JSON**: Full workflow data with all details
- **YAML**: Human-readable format for configuration

### Export Contents
- Project plan with milestones
- Task assignments and employee workloads
- Conversation history
- Workflow event log
- Configuration settings

## 🛠️ Development

### Adding New Project Templates

```python
# In pm_planning_agent.py
def _load_plan_templates(self):
    return {
        "custom_project": {
            "milestones": [
                {"type": "planning", "duration_days": 5, "title": "Custom Planning"},
                # ... more milestones
            ]
        }
    }
```

### Extending Task Assignment Logic

```python
# In task_assigner.py
def _calculate_custom_score(self, task, employee):
    # Add custom scoring logic
    return custom_score
```

## 🧪 Testing

```bash
# Run demo mode
python main.py --demo

# Test individual components
python -m agent.pm_planning_agent
python -m agent.task_assigner
python -m agent.workflow_controller
```

## 📈 Roadmap

- [ ] **Web Interface**: React-based web UI for non-technical users
- [ ] **Team Management**: Employee database with skill tracking
- [ ] **Progress Monitoring**: Real-time project progress tracking
- [ ] **Integration APIs**: REST API for external tool integration
- [ ] **Advanced Analytics**: Project performance metrics and insights
- [ ] **Multi-language Support**: Internationalization for global teams

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the Portia PM Agent system.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information
4. Contact the development team

---

**Built with ❤️ using Portia AI and modern Python practices**