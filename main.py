import os
import sys
from functions.get_files_info import get_files_info, get_file_content, write_file
from functions.run_python import run_python_file
from dotenv import load_dotenv
from google import genai
from google.genai import types

func_dict  = {"get_files_info":get_files_info,"get_file_content":get_file_content,"write_file":write_file,"run_python_file":run_python_file}

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    if not function_call_part.name in func_dict:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )
    args = function_call_part.args.copy()
    args["working_directory"] = "./calculator"
    output = func_dict[function_call_part.name](**args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": output},
            )
        ],
    )


if len(sys.argv) < 2 or sys.argv[1] == None:
    print("Error: Missing prompt")
    sys.exit(1)
verbose = False
if len(sys.argv) > 2 and sys.argv[2] == "--verbose":
    verbose = True

user_prompt = sys.argv[1]

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            )
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Retrieves the content of the specified file, which is constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file from which to retrieve content, relative to the working directory.",
            )
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes the python code in the specified file, which is constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file in which to execute the python code, relative to the working directory.",
            )
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write out to the specified file, which is constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to which to write out, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content of the file to write out.",
            )
        },
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

response = client.models.generate_content(model='gemini-2.0-flash-001', contents=user_prompt,
                                          config=types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt))

if verbose:
    print(f"User prompt: {user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    print()

print(response.text)

for call in response.function_calls:
    func_call = types.FunctionCall(name=call.name, args=call.args)
    content = call_function(func_call, verbose)
    if len(content.parts) == 0:
        raise Exception("invalid function call response")
    if verbose:
        print(f"-> {content.parts[0].function_response.response}")
    #print(f"Calling function: {call.name}({call.args})")
