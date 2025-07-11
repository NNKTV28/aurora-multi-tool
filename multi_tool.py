import os
import platform
import sys
from time import sleep


def clear_screen():
    """Clear terminal screen based on OS"""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")



def print_header():
    """Print tool header"""
    clear_screen()
    print("=" * 50)
    print("           Aurora Multi-Tool v2.0")
    print("=" * 50)
    print()

class Sandbox(object):
    def __init__(self):
        self.namespace = {}

    def load(self, code: str):
        exec(code, self.namespace)

        # Check if tool meets standard
        name = self.namespace.get("name")
        main = self.namespace.get("main")
        check = self.namespace.get("check_platform_compatibility")

        if not (name and main and check):
            raise Exception("Code doesn't meet standard")


    def check(self):
        platform_check = self.namespace.get("check_platform_compatibility")
        return platform_check()

    def execute(self):
        tool = self.namespace.get("main")
        tool()

    def get_name(self):
        return self.namespace.get("name")

class Loader(object):
    def __init__(self):
        self.tools = {}

    def load(self, path):
        tool = Sandbox()
        try:
            with open(path, 'r', encoding='utf-8') as f:
                tool.load(''.join(f.readlines()))
        except:
            raise Exception(f"File {path} doesn't meet standard")
        tool_name = tool.get_name()
        self.tools[tool_name] = tool


def run_tool(loader, tool_name):
    """Run a tool script with error handling"""
    try:
        print(f"\nRunning {tool_name}...")
        print("-" * 30)

        loader.tools[tool_name].execute()

        print("\nOperation completed successfully!")

    except Exception as e:
        print(f"\nError: {e}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")

    input("\nPress Enter to continue...")

# implement logic to download tool folder from github web instead of making new empty tool folder
def validate_environment(path):
    """Validate required directories and files exist"""
    if not os.path.exists(path):
        print("Error: Missing tools folder")
        input("\nPress Enter to exit...")
        os.mkdir("tools")
        sys.exit(1)


def show_menu(path):
    """Display the main menu and get user choice"""
    options = {}

    # Get all the files ended with .py
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.py') and os.path.isfile(os.path.join(path, f))]
    loader = Loader()
    for file in files:
        try:
            loader.load(file)
        except:
            print(f"Tool '{file}' doesn't meet the required standard")

    count = 1
    for tool_name in loader.tools.keys():

        tool = loader.tools[tool_name]

        # Run tool's platform support check
        supported, warnings = tool.check()

        for warning in warnings:
            print(warning)

        if supported:
            options[count] = tool_name
            print(f"Tool {tool_name} loaded")
            count += 1
        else:
            print(f"Tool {tool_name} not loaded")
    
    # Add exit option
    options[count] = "Exit"

    while True:
        print("Available Tools:")
        print("-" * 20)

        for key, name in options.items():
            print(f"{key}. {name}")

        try:
            choice = int(input(f"\nSelect an option (1-{len(options)}): ").strip())
        except ValueError:
            print("\nInvalid input. Please enter a number.")
            sleep(1.5)
            continue
        # Since the exit option is always the last in the list, len(options) = Exit option's number
        if choice == len(options):
            print("\nThank you for using Aurora Multi-Tool!")
            sleep(1.5)
            sys.exit(0)

        if choice in options.keys():
            tool_name= options[choice]
            run_tool(loader, tool_name)
        else:
            print("\nInvalid choice. Please try again.")
            sleep(1.5)
        print_header()


def main(path):
    try:
        validate_environment(path)
        show_menu(path)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main("./tools")
