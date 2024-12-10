import ast

# Function to detect CPU-bound operations
def is_cpu_bound(function):
    
    return any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(function))

# Function to detect I/O-bound operations 
def is_io_bound(function):
    
    return any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'sleep' for node in ast.walk(function))

# Function to detect spinlock (infinite while loop with no exit condition)
def has_spinlock(function):
    
    for node in ast.walk(function):
        if isinstance(node, ast.While):
            if not any(isinstance(child, ast.Pass) for child in ast.iter_child_nodes(node)):
                return False
            return True
    return False

# Function to detect redundant function calls inside loops
def has_redundant_function_calls(function):
    
    calls = {}
    for node in ast.walk(function):
        if isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name:
                if func_name in calls:
                    calls[func_name] += 1
                else:
                    calls[func_name] = 1
    return any(count > 1 for count in calls.values())

# Function to detect excessive loops (more than a certain threshold of loops)
def has_excessive_loops(function):
    
    loop_count = sum(1 for node in ast.walk(function) if isinstance(node, (ast.For, ast.While)))
    return loop_count > 5

# Function to detect Monte Carlo estimation (based on use of random.uniform())
def is_monte_carlo_estimation(function):
   
    return any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'uniform' for node in ast.walk(function))

# Main function to analyze the code and provide optimization suggestions
def analyze_code(code):
    
    bottlenecks = []

    # Parse the provided code into an abstract syntax tree (AST)
    try:
        tree = ast.parse(code)
    except SyntaxError:
        bottlenecks.append("Syntax error in the provided code.")
        return bottlenecks

    # Analyze the functions in the code
    for function in tree.body:
        if isinstance(function, ast.FunctionDef):
            # Check if the function is CPU-bound
            if is_cpu_bound(function):
                if has_spinlock(function):
                    bottlenecks.append("Avoid spinlocks; use sleep or proper synchronization methods.")

            # Check if the function is I/O-bound
            if is_io_bound(function):
                bottlenecks.append("Consider using non-blocking I/O or optimizing sleep calls.")
                
            if has_redundant_function_calls(function):
                bottlenecks.append("Reduce redundant function calls inside loops to improve efficiency.")
            
            if has_excessive_loops(function):
                bottlenecks.append("Consider optimizing or reducing unnecessary loop iterations.")
            
            if is_monte_carlo_estimation(function):
                bottlenecks.append("Consider terminating the Monte Carlo estimation early once the result stabilizes.")

    # Check for inefficient use of time functions (e.g., time.sleep())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == 'sleep' and not is_io_bound(function):
                bottlenecks.append("Use `time.perf_counter()` for real-time tasks and `time.process_time()` for CPU-bound tasks.")
    
    # If no bottlenecks were detected
    if not bottlenecks:
        bottlenecks.append("No performance bottlenecks detected.")

    return bottlenecks
