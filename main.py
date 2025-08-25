#!/usr/bin/env python3
"""
Portia PM Agent - Main Entry Point

This is the main controller that provides a unified interface for:
1. Product Manager Planning (conversational project planning)
2. Task Assignment (employee allocation)
3. Complete workflow management
"""

import argparse
import sys
import os
from pathlib import Path

# Add the agent directory to the path
sys.path.insert(0, str(Path(__file__).parent / "agent"))

try:
    from agent.workflow_controller import WorkflowController
    from agent.pm_planning_agent import PMPlanningAgent
    from agent.task_assigner import TaskAssignerAgent
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}")
    print("Make sure all agent files are in the agent/ directory.")
    sys.exit(1)

def interactive_workflow_mode():
    """Run the workflow in interactive mode"""
    print("🚀 Welcome to Portia PM Agent - Interactive Workflow Mode")
    print("=" * 60)
    
    # Initialize workflow controller
    controller = WorkflowController()
    
    print("\nThis system will help you:")
    print("1. 📋 Plan your project with conversational feedback")
    print("2. 👥 Assign tasks to your team members")
    print("3. 📊 Track progress and manage the complete workflow")
    
    while True:
        try:
            print("\n" + "=" * 60)
            print("🎯 **Main Menu**")
            print("1. Start New Project")
            print("2. Continue Planning (if active)")
            print("3. Move to Task Assignment")
            print("4. Assign Tasks")
            print("5. View Workflow Status")
            print("6. Export Workflow Data")
            print("7. Save/Load Workflow")
            print("8. Help")
            print("9. Exit")
            
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == "1":
                # Start new project
                project_title = input("Enter project title: ").strip()
                if not project_title:
                    print("Project title cannot be empty.")
                    continue
                
                print("\nDescribe your project requirements:")
                requirements = input("Requirements: ").strip()
                if not requirements:
                    print("Requirements cannot be empty.")
                    continue
                
                print("\n🔄 Starting project planning...")
                response = controller.start_new_project(project_title, requirements)
                print(response)
                
                # Enter planning conversation loop
                planning_loop(controller)
                
            elif choice == "2":
                # Continue planning if active
                if controller.state == "planning":
                    print("\n💬 Continue planning conversation...")
                    planning_loop(controller)
                else:
                    print(f"Planning phase is not active. Current state: {controller.state}")
            
            elif choice == "3":
                # Transition to task assignment
                print("\n🔄 Transitioning to task assignment...")
                response = controller.transition_to_assignment()
                print(response)
            
            elif choice == "4":
                # Assign tasks
                if controller.state == "assignment":
                    print("\n👥 Assigning tasks to team members...")
                    response = controller.assign_tasks()
                    print(response)
                else:
                    print(f"Cannot assign tasks. Current state: {controller.state}")
            
            elif choice == "5":
                # View workflow status
                print("\n📊 Current Workflow Status:")
                status = controller.get_workflow_status()
                print(f"State: {status['state']}")
                if status.get('current_plan'):
                    print(f"Plan: {status['current_plan']['title']}")
                    print(f"Status: {status.get('plan_approval_status', 'N/A')}")
                    print(f"Duration: {status.get('estimated_duration', 'N/A')}")
                print(f"Planning Agent: {status['planning_agent_status']}")
                print(f"Task Agent: {status['task_agent_status']}")
            
            elif choice == "6":
                # Export workflow data
                format_choice = input("Export format (json/yaml): ").strip().lower()
                if format_choice not in ["json", "yaml"]:
                    format_choice = "json"
                
                response = controller.export_workflow_data(format_choice)
                print(response)
            
            elif choice == "7":
                # Save/Load workflow
                save_load_menu(controller)
            
            elif choice == "8":
                # Help
                print(controller.get_help())
            
            elif choice == "9":
                # Exit
                print("\n👋 Thank you for using Portia PM Agent!")
                break
            
            else:
                print("Invalid choice. Please select 1-9.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or contact support.")

def planning_loop(controller):
    """Interactive planning conversation loop"""
    print("\n💬 **Planning Conversation Mode**")
    print("Type your feedback or requests. Type 'done' to finish planning.")
    print("Examples:")
    print("- 'Add requirement: User authentication system'")
    print("- 'Add milestone: Security review phase'")
    print("- 'Change timeline to be more aggressive'")
    print("- 'Approve plan'")
    
    while True:
        try:
            feedback = input("\n💭 Your feedback: ").strip()
            
            if feedback.lower() in ["done", "exit", "quit"]:
                print("Planning conversation ended.")
                break
            
            if not feedback:
                continue
            
            # Process feedback
            response = controller.process_planning_feedback(feedback)
            print(f"\n🤖 Agent: {response}")
            
            # Check if plan was approved
            if "Plan Approved!" in response:
                print("\n🎉 Planning phase completed! You can now move to task assignment.")
                break
        
        except KeyboardInterrupt:
            print("\n\nPlanning conversation interrupted.")
            break
        except Exception as e:
            print(f"\n❌ Error processing feedback: {e}")

def save_load_menu(controller):
    """Save/Load workflow menu"""
    while True:
        print("\n💾 **Save/Load Menu**")
        print("1. Save current workflow")
        print("2. Load saved workflow")
        print("3. Back to main menu")
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == "1":
            filename = input("Save filename (or press Enter for auto-name): ").strip()
            response = controller.save_workflow(filename if filename else None)
            print(response)
        
        elif choice == "2":
            # List available save files
            storage_dir = Path("workflow_data")
            if storage_dir.exists():
                save_files = list(storage_dir.glob("*.json"))
                if save_files:
                    print("\nAvailable save files:")
                    for i, file in enumerate(save_files, 1):
                        print(f"{i}. {file.name}")
                    
                    try:
                        file_choice = int(input("Select file number: ").strip())
                        if 1 <= file_choice <= len(save_files):
                            selected_file = save_files[file_choice - 1].name
                            response = controller.load_workflow(selected_file)
                            print(response)
                        else:
                            print("Invalid file number.")
                    except ValueError:
                        print("Please enter a valid number.")
                else:
                    print("No save files found.")
            else:
                print("No workflow data directory found.")
        
        elif choice == "3":
            break
        
        else:
            print("Invalid choice. Please select 1-3.")

def demo_mode():
    """Run a demonstration of the complete workflow"""
    print("🎬 **Portia PM Agent - Demo Mode**")
    print("=" * 50)
    
    controller = WorkflowController()
    
    # Demo 1: Start a project
    print("\n1️⃣ Starting a new project...")
    response = controller.start_new_project(
        "Task Management Mobile App",
        "Build a mobile app for task management with user authentication, task creation, and progress tracking"
    )
    print(response)
    
    # Demo 2: Add some requirements
    print("\n2️⃣ Adding requirements...")
    controller.process_planning_feedback("Add requirement: Push notifications for task reminders")
    controller.process_planning_feedback("Add requirement: Offline mode support")
    
    # Demo 3: Approve the plan
    print("\n3️⃣ Approving the plan...")
    response = controller.process_planning_feedback("Approve plan")
    print(response)
    
    # Demo 4: Transition to assignment
    print("\n4️⃣ Transitioning to task assignment...")
    response = controller.transition_to_assignment()
    print(response)
    
    # Demo 5: Assign tasks
    print("\n5️⃣ Assigning tasks...")
    response = controller.assign_tasks()
    print(response)
    
    # Demo 6: Show final status
    print("\n6️⃣ Final workflow status:")
    status = controller.get_workflow_status()
    print(f"State: {status['state']}")
    print(f"Plan: {status['current_plan']['title']}")
    print(f"Tasks: {len(controller.task_agent.tasks)}")
    print(f"Assignments: {len(controller.task_agent.assignments)}")
    
    print("\n✅ Demo completed! The system successfully:")
    print("- Created a project plan with milestones")
    print("- Processed conversational feedback")
    print("- Converted milestones to tasks")
    print("- Assigned tasks to team members")
    print("- Maintained complete workflow state")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Portia PM Agent - Complete Project Management Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Interactive mode
  %(prog)s --demo            # Run demonstration
  %(prog)s --idea "Build a web app"  # Quick project start
        """
    )
    
    parser.add_argument(
        "--demo", "-d",
        action="store_true",
        help="Run demonstration mode"
    )
    
    parser.add_argument(
        "--idea", "-i",
        type=str,
        help="Quick start with project idea (skips interactive planning)"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="workflow_config.yaml",
        help="Configuration file path (default: workflow_config.yaml)"
    )
    
    args = parser.parse_args()
    
    # Set up configuration
    if args.config and not os.path.exists(args.config):
        print(f"Warning: Configuration file {args.config} not found. Using defaults.")
    
    try:
        if args.demo:
            demo_mode()
        elif args.idea:
            # Quick start mode
            print("🚀 Quick Start Mode")
            print(f"Project Idea: {args.idea}")
            
            controller = WorkflowController(args.config)
            response = controller.start_new_project("Quick Project", args.idea)
            print(response)
            
            # Auto-approve for quick start
            print("\n🔄 Auto-approving plan for quick start...")
            controller.process_planning_feedback("Approve plan")
            
            # Auto-transition to assignment
            print("\n🔄 Auto-transitioning to task assignment...")
            controller.transition_to_assignment()
            
            # Auto-assign tasks
            print("\n👥 Auto-assigning tasks...")
            controller.assign_tasks()
            
            print("\n✅ Quick start completed! Use interactive mode for full control.")
        else:
            # Interactive mode
            interactive_workflow_mode()
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()