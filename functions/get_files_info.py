import os

MAX_CHARS = 10000

def get_files_info(working_directory, directory=None):
    abs_dir = ""
    try:
        abs_dir = check_dir_path(working_directory, directory)
    except Exception as e:
        return str(e)
    try:
        contents = os.listdir(abs_dir)
        #print(f"{abs_dir} : {contents}")
        content_str = ""
        for entry in contents:
            abs_path = os.path.join(abs_dir, entry)
            content_str += f"- {entry}: file_size={os.path.getsize(abs_path)} bytes, is_dir={os.path.isdir(abs_path)}\n"
        return content_str
    except Exception as e:
        return f"Error: {str(e)}"

def get_file_content(working_directory, file_path):
    abs_path = ""
    try:
        abs_path = check_file_path(working_directory, file_path, "read")
    except Exception as e:
        return str(e)
    try:
        file_content_string = ""
        with open(abs_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)
        return file_content_string
    except Exception as e:
        return f"Error: {str(e)}"

def write_file(working_directory, file_path, content):
    working_fullpath = os.path.join(working_directory, file_path)
    abs_path = os.path.abspath(working_fullpath)
    if not abs_path.startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    try:
        dirname = os.path.dirname(abs_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(abs_path, "w") as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error: {str(e)}"

def check_dir_path(working_directory, directory):
    working_fullpath = os.path.join(working_directory, directory)
    abs_dir = os.path.abspath(working_fullpath)
    if not os.path.isdir(abs_dir):
        raise Exception(f'Error: "{directory}" is not a directory')
    if not abs_dir.startswith(os.path.abspath(working_directory)):
        raise Exception(f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
    return abs_dir

def check_file_path(working_directory, file_path, operation):
    working_fullpath = os.path.join(working_directory, file_path)
    abs_path = os.path.abspath(working_fullpath)
    if not os.path.isfile(abs_path):
        raise Exception(f'Error: File not found or is not a regular file: "{file_path}"')
    if not abs_path.startswith(os.path.abspath(working_directory)):
        raise Exception(f'Error: Cannot {operation} "{file_path}" as it is outside the permitted working directory')
    return abs_path
