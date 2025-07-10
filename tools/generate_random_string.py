name = "Generate Random String"

def main():
    import random
    import string


    def generate_random_string(length: int) -> str:
        """Generate a random string of specified length."""
        if length <= 0:
            raise ValueError("Length must be a positive integer.")
        characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(random.choice(characters) for _ in range(length))


    print("Random String Generator")
    print("-" * 30)
    try:
        length = int(input("Enter the length of the random string: ").strip())
        random_string = generate_random_string(length)
        print(f"\nGenerated Random String:\n{random_string}")
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")


def check_platform_compatibility():
    supported = True
    warnings = []

    return supported, warnings
