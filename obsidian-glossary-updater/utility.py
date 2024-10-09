import os
import base64
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

def extract_added_lines(patch):
    added_lines = []
    for line in patch.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            added_lines.append(line[1:])
    return added_lines

def format_extraction_prompt_generic(added_text):
    prompt = (
        "You are an assistant that extracts important terms from the provided text.\n\n"
        "Please perform the following tasks:\n"
        "1. Review the following text:\n"
        f"{added_text}\n"
        "2. Identify and list any significant words, terms, acronyms, or phrases such as objects, products, processes, nouns, proper nouns, and acronyms.\n"
        "3. Provide the list of terms without any definitions or additional explanations.\n"
        "4. If no relevant terms are found, respond with 'false'.\n\n"
        "Please provide the list of terms below:\n"
    )
    return prompt

def format_glossary_prompt(extracted_terms, glossary_content, vault_purpose):
    # Decode the Glossary.md content
    glossary_content_decoded = base64.b64decode(glossary_content.content).decode("utf-8")

    prompt = (
        "You are an assistant that helps update the Glossary.md file in an Obsidian vault.\n"
        f"The purpose of this Obsidian vault is: {vault_purpose}\n"
        "The Glossary.md file serves as a glossary and table of contents for the vault.\n"
        "Please perform the following tasks:\n"
        "1. Using the following text or list of terms:\n"
        f"{extracted_terms}\n"
        "2. Identify any words, terms, acronyms, or phrases that are relevant to the vault's purpose and should be added to the Glossary.\n"
        "3. Update the Glossary.md file by adding entries for these terms, preserving the existing style and formatting.\n"
        "4. Each new entry must include a relevant and concise definition underneath it.\n"
        "5. Do not modify other sections of the Glossary.md file unless you are adding a definition under an existing entry.\n"
        "6. If no updates are necessary, respond with 'false'.\n"
        "7. Provide only the updated Glossary.md content in plain text format, without wrapping it in code blocks or adding any additional explanations.\n"
        "\n"
        "**Note**: Do not include any markdown code block fences (e.g., ```markdown) at the beginning or end of your response.\n"
        "\n"
        "Current Glossary.md content:\n"
        f"{glossary_content_decoded}\n"
        "\n"
        "Please provide the updated Glossary.md content below:\n"
    )
    return prompt

def call_openai(prompt, model_name):
    client = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model_name=model_name)
    try:
        messages = [
            SystemMessage(
                content="You are an AI assistant that processes user requests."
            ),
            HumanMessage(content=prompt),
        ]

        # Call OpenAI
        response = client(messages)
        content = response.content

        return content.strip()
    except Exception as e:
        print(f"Error making OpenAI API call: {e}")
        return "false"

def update_glossary_and_create_pr(repo, updated_glossary, glossary_sha, pull_request_number):
    """
    Submit Updated Glossary content as a PR in a new branch
    """

    commit_message = "Proposed Glossary.md update based on recent changes"
    master_branch = repo.get_branch("master")
    new_branch_name = f"update-glossary-pr{pull_request_number}"
    new_branch = repo.create_git_ref(
        ref=f"refs/heads/{new_branch_name}", sha=master_branch.commit.sha
    )

    # Update the Glossary file
    repo.update_file(
        path="Glossary.md",
        message=commit_message,
        content=updated_glossary,
        sha=glossary_sha,
        branch=new_branch_name,
    )

    # Create a PR
    pr_title = "Update Glossary.md based on recent changes"
    pr_body = "This PR proposes an update to the Glossary.md based on recent additions. Please review and merge if appropriate."
    pull_request = repo.create_pull(
        title=pr_title, body=pr_body, head=new_branch_name, base="master"
    )