import os
from github import Github
from utility import *
import base64

def main():
    # Initialize GitHub API with token
    g = Github(os.getenv('GH_TOKEN'))

    # Get the repo path and PR number from the environment variables
    repo_path = os.getenv('REPO_PATH')
    pull_request_number = int(os.getenv('PR_NUMBER'))

    # Get the repo object
    repo = g.get_repo(repo_path)

    # Fetch Glossary.md content
    glossary_content = repo.get_contents("Glossary.md")

    # Fetch pull request by number
    pull_request = repo.get_pull(pull_request_number)

    # Get the vault purpose from environment variables
    vault_purpose = os.getenv('VAULT_PURPOSE', '')

    # Define a set of files to ignore
    ignored_files = {'Index.md', 'Glossary.md'}

    # Collect added text from the PR, excluding ignored files
    added_text = ''
    for file in pull_request.get_files():
        if file.filename.endswith('.md') and file.filename not in ignored_files:
            if file.status in ['modified', 'added']:
                if file.patch:
                    added_lines = extract_added_lines(file.patch)
                    added_text += '\n'.join(added_lines) + '\n'
                else:
                    # If no patch is available (e.g., new file), get the full content
                    file_contents = repo.get_contents(file.filename, ref=pull_request.head.sha)
                    content_decoded = base64.b64decode(file_contents.content).decode("utf-8")
                    added_text += content_decoded + '\n'

    if not added_text.strip():
        print("No new text to analyze.")
        return

    # Assess the length of the added text
    word_count = len(added_text.split())
    MAX_WORDS = 1500  # Define what "more than a page of text" means

    if word_count > MAX_WORDS:
        # Use gpt-4o-mini to extract relevant terms
        extraction_prompt = format_extraction_prompt_generic(added_text)
        extracted_terms = call_openai(extraction_prompt, model_name="gpt-4o-mini")
    else:
        # Use the original added text
        extracted_terms = added_text

    if extracted_terms.strip().lower() == "false":
        print("No relevant terms found for the glossary.")
        return

    # Stage 2: Generate updated Glossary.md content using gpt-4o
    glossary_prompt = format_glossary_prompt(extracted_terms, glossary_content, vault_purpose)
    updated_glossary = call_openai(glossary_prompt, model_name="gpt-4o")

    if updated_glossary.strip().lower() == "false":
        print("No updates needed for Glossary.md.")
        return

    # Create PR for Updated Glossary.md
    update_glossary_and_create_pr(repo, updated_glossary, glossary_content.sha, pull_request_number)

if __name__ == '__main__':
    main()