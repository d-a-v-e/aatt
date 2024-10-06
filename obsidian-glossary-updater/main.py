import os
from github import Github
from utility import *

def main():
    # Initialize GitHub API with token
    g = Github(os.getenv('GH_TOKEN'))

    # Get the repo path and PR number from the environment variables
    repo_path = os.getenv('REPO_PATH')
    pull_request_number = int(os.getenv('PR_NUMBER'))

    # Get the repo object
    repo = g.get_repo(repo_path)

    # Fetch Glossary.md content
    index_content = repo.get_contents("Glossary.md")

    # Fetch pull request by number
    pull_request = repo.get_pull(pull_request_number)

    # Get the list of new markdown files added in the PR
    ignore_files = {'glossary.md', 'index.md'}

    new_markdown_files = [
        file.filename for file in pull_request.get_files()
        if file.status == 'added' and
           file.filename.endswith('.md') and
           file.filename.lower() not in ignore_files
    ]

    if not new_markdown_files:
        print("No new markdown files to add to the glossary.")
        return

    # Get the commit messages associated with the pull request
    commit_messages = [commit.commit.message for commit in pull_request.get_commits()]

    # Format data for OpenAI prompt
    prompt = format_data_for_openai(new_markdown_files, index_content)

    # Call OpenAI to generate the updated Glossary.md content
    updated_index = call_openai(prompt)

    # Create PR for Updated Glossary.md
    update_index_and_create_pr(repo, updated_index, index_content.sha)

if __name__ == '__main__':
    main()