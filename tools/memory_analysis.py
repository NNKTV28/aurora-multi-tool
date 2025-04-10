import psutil

def memory_analysis():
    """Analyze system memory usage."""
    print("Memory Analysis")
    print("-" * 30)
    
    try:
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()

        print(f"Total Memory: {virtual_memory.total / (1024 * 1024):.2f} MB")
        print(f"Available Memory: {virtual_memory.available / (1024 * 1024):.2f} MB")
        print(f"Used Memory: {virtual_memory.used / (1024 * 1024):.2f} MB")
        print(f"Memory Usage: {virtual_memory.percent}%")
        print(f"Swap Total: {swap_memory.total / (1024 * 1024):.2f} MB")
        print(f"Swap Used: {swap_memory.used / (1024 * 1024):.2f} MB")
        print(f"Swap Usage: {swap_memory.percent}%")
    except Exception as e:
        print(f"Error: {e}")

def main():
    memory_analysis()

if __name__ == "__main__":
    main()