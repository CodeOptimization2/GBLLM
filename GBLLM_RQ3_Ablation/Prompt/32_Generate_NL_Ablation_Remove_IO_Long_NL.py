Prompt_Dict = {
    "Prompt_Description": "Code --> (Gen) NL without I/O guidance",

    "Role_Play_Python": (
        "You are an experienced software engineer and technical documentation expert. "
        "Generate a code-function description from Python source code only. "
        "Place the description in this format:\n```Description\n<code function description>\n```"
    ),
    "Role_Play_Cpp": (
        "You are an experienced software engineer and technical documentation expert. "
        "Generate a code-function description from C++ source code only. "
        "Place the description in this format:\n```Description\n<code function description>\n```"
    ),

    "Operation_Command_Python": (
        "Below is Python source code. Without using input/output examples, generate a concise "
        "natural-language description of its functionality.\n\n"
        "### Code:\n```python\n{Slow_program}\n```\n\n"
        "### Generate the code-function description using the required output format:\n"
    ),
    "Operation_Command_Cpp": (
        "Below is C++ source code. Without using input/output examples, generate a concise "
        "natural-language description of its functionality.\n\n"
        "### Code:\n```cpp\n{Slow_program}\n```\n\n"
        "### Generate the code-function description using the required output format:\n"
    ),

    "IO_Format": "",
}
