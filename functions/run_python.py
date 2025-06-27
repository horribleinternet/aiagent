import os
import subprocess

def run_python_file(working_directory, file_path):
    working_fullpath = os.path.join(working_directory, file_path)
    abs_path = os.path.abspath(working_fullpath)
    abs_working_dir = os.path.abspath(working_directory)
    if not os.path.isfile(abs_path):
        return f'Error: File "{file_path}" not found.'
    if not abs_path.startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if file_path[-2:] != "py":
        return f'Error: "{file_path}" is not a Python file.'
    try:
        completed = subprocess.run(["python3", abs_path], cwd=abs_working_dir, capture_output=True, timeout=30)
        output = ""
        if len(completed.stdout) > 0:
            output += f"STDOUT: {completed.stdout}\n"
        if len(completed.stderr) > 0:
            output += f"STDERR: {completed.stderr}\n"
        if len(completed.stdout) == 0 and len(completed.stderr) == 0:
            output += "No output produced\n"
        if completed.returncode != 0:
            output += f"Process exited with code {completed.returncode}"
        return output
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
