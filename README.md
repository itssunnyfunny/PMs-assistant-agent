# Portia PM Agent

🤖 AI assistant for project managers.  
Input a project idea → get structured tasks with roles and descriptions.  

## Setup
```bash
uv sync
cp .env.example .env  # add PORTIA_API_KEY
uv run main.py --idea "Build a hackathon portal"