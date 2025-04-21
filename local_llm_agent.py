
# import os
# from langchain_openai import ChatOpenAI

# def generate_local_readme(path: str = ".") -> str:
#     """
#     Inspect the folder structure under `path`, ask the LLM to
#     write a comprehensive README.md, then save it at path/README.md.
#     Returns the generated content.
#     """
#     # 1) Build a simple tree representation
#     tree_lines = []
#     for root, dirs, files in os.walk(path):
#         # skip hidden folders
#         rel = os.path.relpath(root, path)
#         indent = "" if rel == "." else "  " * rel.count(os.sep)
#         tree_lines.append(f"{indent}- {os.path.basename(root)}/")
#         for f in files:
#             if f.startswith("."):
#                 continue
#             tree_lines.append(f"{indent}  - {f}")
#     structure = "\n".join(tree_lines)

#     # 2) Prompt the LLM
#     llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
#     prompt = (
#         "You are a README generator. Here is my project’s directory structure:\n\n"
#         f"{structure}\n\n"
#         "Please write a comprehensive `README.md` for this project, including:\n"
#         "1. Project Title (use the folder name)\n"
#         "2. Short Description\n"
#         "3. Installation instructions\n"
#         "4. Usage examples\n"
#         "5. Directory Structure section (render the tree above as a code block)\n"
#         "6. Contributing guidelines\n"
#         "7. License placeholder\n\n"
#         "Return only the new README.md content in markdown."
#     )
#     generated = llm.invoke(prompt).content

#     # 3) Write to README.md
#     out_path = os.path.join(path, "README.md")
#     with open(out_path, "w", encoding="utf-8") as f:
#         f.write(generated)

#     return generated


import os
from langchain_openai import ChatOpenAI

def generate_local_readme(path: str = ".") -> str:
    """
    Inspect the folder structure under `path`, ask the LLM to
    write a comprehensive README.md, then save it at path/README.md.
    Returns the generated content.
    """
    # 1) Build a simple tree representation
    tree_lines = []
    main_files = [f for f in os.listdir(path) if f.endswith((".py", ".md", ".json", ".js"))]
    main_files = main_files[:20]  # limit to avoid token overload

    for root, dirs, files in os.walk(path):
        rel = os.path.relpath(root, path)
        indent = "" if rel == "." else "  " * rel.count(os.sep)
        tree_lines.append(f"{indent}- {os.path.basename(root)}/")
        for f in files:
            if f.startswith("."):
                continue
            tree_lines.append(f"{indent}  - {f}")

    structure = "\n".join(tree_lines)

    # 2) Prompt the LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    prompt = (
        "You are a README generator. Here is my project’s directory structure:\n\n"
        f"{structure}\n\n"
        f"Key files include: {', '.join(main_files)}.\n\n"
        "Please write a comprehensive `README.md` for this project, including:\n"
        "1. Project Title (use the folder name)\n"
        "2. Short Description\n"
        "3. Installation instructions\n"
        "4. Usage examples\n"
        "5. Directory Structure section (render the tree above as a code block)\n"
        "6. Contributing guidelines\n"
        "7. License placeholder\n\n"
        "Return only the new README.md content in markdown."
    )
    generated = llm.invoke(prompt).content

    # 3) Write to README.md
    out_path = os.path.join(path, "README.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(generated)

    return generated
