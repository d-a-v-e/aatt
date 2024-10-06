import os
import base64
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

def format_data_for_openai(new_markdown_files, index_content):
    # Decode the Glossary.md content
    index_content_decoded = base64.b64decode(index_content.content).decode("utf-8")

    # Construct the prompt with clear instructions
    prompt = (
        "You are an assistant that helps update the Glossary.md file in an Obsidian vault.\n"
        "The Glossary.md file serves as a glossary and table of contents for the vault.\n"
        "Please perform the following tasks:\n"
        "1. Review the list of new markdown files added to the vault:\n"
        f"{', '.join(new_markdown_files)}\n"
        "2. Update the Glossary.md file by adding links to these new markdown files, preserving the existing style and formatting.\n"
        "3. Any and all glossary links should have a short concise definition underneath the link to their note.\n"
        "4. Do not modify other sections of the Glossary.md file unless you are adding a short concise definition under an existing link.\n"
        "5. Provide only the updated Glossary.md content without any additional explanations.\n\n"
        "Current Glossary.md content:\n"
        f"{index_content_decoded}\n\n"
        "Please provide the updated Glossary.md content below:\n"
    )

    return prompt

def call_openai(prompt):
    client = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant that updates the Glossary.md file in an Obsidian vault based on recent changes.",
            },
            {"role": "user", "content": prompt},
        ]

        # Call OpenAI
        response = client.invoke(input=messages)
        parser = StrOutputParser()
        content = parser.invoke(input=response)

        return content.strip()
    except Exception as e:
        print(f"Error making OpenAI API call: {e}")
        return "false"

def update_index_and_create_pr(repo, updated_index, index_sha):
    if updated_index == "false":
        return
    """
    Submit Updated Index content as a PR in a new branch
    """

    commit_message = "Proposed Glossary.md update based on recent code changes"
    master_branch = repo.get_branch("master")
    new_branch_name = f"update-index-{index_sha[:10]}"
    new_branch = repo.create_git_ref(
        ref=f"refs/heads/{new_branch_name}", sha=master_branch.commit.sha
    )

    # Update the Glossary file
    repo.update_file(
        path="Glossary.md",
        message=commit_message,
        content=updated_index,
        sha=index_sha,
        branch=new_branch_name,
    )

    # Create a PR
    pr_title = "Update Glossary.md based on recent changes"
    br_body = "This PR proposes an update to the Glossary.md based on recent additions. Please review and merge if appropriate."
    pull_request = repo.create_pull(
        title=pr_title, body=br_body, head=new_branch_name, base="master"
    )
