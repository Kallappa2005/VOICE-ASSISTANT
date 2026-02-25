import os

def create_project_structure():
    """
    Creates a professional, scalable folder structure for Voice Assistant
    Following industry best practices with separation of concerns
    """
    
    # Define the project structure
    structure = {
        'voice-assistant': {
            'src': {
                'core': {
                    '__init__.py': '',
                    'config.py': '# Configuration settings and constants',
                    'logger.py': '# Logging configuration'
                },
                'speech': {
                    '__init__.py': '',
                    'speech_recognition_handler.py': '# Handle voice input',
                    'text_to_speech_handler.py': '# Handle voice output'
                },
                'browser': {
                    '__init__.py': '',
                    'browser_controller.py': '# Browser operations',
                    'navigation.py': '# Navigation related tasks',
                    'tab_manager.py': '# Tab operations'
                },
                'automation': {
                    '__init__.py': '',
                    'screenshot_handler.py': '# Screenshot functionality',
                    'scroll_handler.py': '# Scrolling operations'
                },
                'commands': {
                    '__init__.py': '',
                    'command_parser.py': '# Parse and interpret commands',
                    'command_executor.py': '# Execute parsed commands',
                    'command_registry.py': '# Registry of all available commands'
                },
                'utils': {
                    '__init__.py': '',
                    'helpers.py': '# Helper functions',
                    'validators.py': '# Input validation'
                }
            },
            'tests': {
                '__init__.py': '',
                'test_speech.py': '# Tests for speech module',
                'test_browser.py': '# Tests for browser module',
                'test_commands.py': '# Tests for command module'
            },
            'data': {
                'logs': {
                    '.gitkeep': ''  # Keep empty folder in git
                },
                'screenshots': {
                    '.gitkeep': ''
                }
            },
            'docs': {
                'COMMANDS.md': '# List of all available commands',
                'SETUP.md': '# Setup instructions'
            },
            'main.py': '# Main entry point of the application',
            'requirements.txt': '# Python dependencies',
            'README.md': '# Project documentation',
            '.env.example': '# Environment variables template',
            '.gitignore': '''# Ignore files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.env
*.log
data/logs/*
data/screenshots/*
!data/logs/.gitkeep
!data/screenshots/.gitkeep
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.DS_Store
chromedriver.exe
geckodriver.exe
'''
        }
    }
    
    def create_structure(base_path, structure):
        """Recursively create folders and files"""
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            
            if isinstance(content, dict):
                # It's a directory
                os.makedirs(path, exist_ok=True)
                print(f"📁 Created directory: {path}")
                create_structure(path, content)
            else:
                # It's a file
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"📄 Created file: {path}")
    
    # Get current directory
    base_dir = os.getcwd()
    
    print("🚀 Creating Voice Assistant Project Structure...\n")
    create_structure(base_dir, structure)
    print("\n✅ Project structure created successfully!")
    print("\n📋 Next Steps:")
    print("1. cd voice-assistant")
    print("2. Create conda environment")
    print("3. Install dependencies")

if __name__ == "__main__":
    create_project_structure()