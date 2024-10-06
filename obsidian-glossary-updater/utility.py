import os
import base64
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

def format_data_for_openai(diffs, index_content, commit_messages):
    prompt = None

    # Combine the changes into a string with clear delineation.
    changes = "\n".join(
        [f'File: {file["filename"]}\nDiff: \n{file["patch"]}\n' for file in diffs]
    )

    # Combine all commit messages
    commit_messages = "\n".join(commit_messages) + "\n\n"

    # Decode the README content
    index_content = base64.b64decode(index_content.content).decode("utf-8")

    # Construct the prompt with clear instructions for the LLM.
    prompt = (
        "Please examine the following Obsidian GitHub pull request:\n"
        "Code changes from Pull Request:\n"
        f"{changes}\n"
        "Commit messages:\n"
        f"{commit_messages}"
        "Here is the current Index.md file content:\n"
        f"{index_content}\n"
        "Consider the code changes from the Pull Request (including file names changes), and the commit messages. Determine if the Index.md glossary needs to be updated. If so, edit the Index.md, ensuring to maintain its existing style and clarity. if no update is needed just return 'false'\n"
        "Updated Index.md:\n"
    )

    return prompt

def call_openai(prompt):
    client = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        messages = [
            {
                "role": "system",
                "content": "You are an AI trained to help with updating the Index file of an ever growing Obsidian notepad",
            },
            {"role": "user", "content": prompt},
        ]

        # Call OpenAI
        response = client.invoke(input=messages)
        parser = StrOutputParser()
        content = parser.invoke(input=response)

        return content
    except Exception as e:
        print(f"Error making OpenAI API call: {e}")

def update_index_and_create_pr(repo, updated_index, index_sha):
    if updated_index == "false":
        return
    """
    Submit Updated Index content as a PR in a new branch
    """

    commit_message = "Proposed Index.md update based on recent code changes"
    master_branch = repo.get_branch("master")
    new_branch_name = f"update-index-{index_sha[:10]}"
    new_branch = repo.create_git_ref(
        ref=f"refs/heads/{new_branch_name}", sha=master_branch.commit.sha
    )

    # Update the README file
    repo.update_file(
        path="Index.md",
        message=commit_message,
        content=updated_index,
        sha=index_sha,
        branch=new_branch_name,
    )

    # Create a PR
    pr_title = "Update Index.md based on recent changes"
    br_body = "This PR proposes an update to the Index.md based on recent additions. Please review and merge if appropriate."
    pull_request = repo.create_pull(
        title=pr_title, body=br_body, head=new_branch_name, base="master"
    )
