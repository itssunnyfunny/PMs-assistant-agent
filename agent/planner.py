import os
from portia import Portia

# Initialize Portia client
portia = Portia(api_key=os.getenv("PORTIA_API_KEY"))

def generate_project_plan(project_idea: str):
    """
    Generate structured project plan from a user idea.
    """
    prompt = f"""
    You are an assistant for project managers.
    Break down the following project idea into 4–6 clear tasks.

    Rules:
    - Output only in JSON.
    - Each task must have: title, description, suggested_role.

    Project idea: {project_idea}
    """

    response = portia.generate(prompt, format="json")

    return response
