import os
from github import Github
from utility import *

def main():
    # Initialize GitHub API with token
    g = Github(os.getenv('GITHUB_TOKEN'))

    # Get the repo path and PR number from the environment variables
    repo_path = os.getenv('REPO_PATH')
    pull_request_number = int(os.getenv('PR_NUMBER'))

    # Get the repo object
    repo = g.get_repo(repo_path)

    # Fetch Index.md content
    index_content = repo.get_contents("Index.md")

    # print(index_content)
    # Fetch pull request by number
    pull_request = repo.get_pull(pull_request_number)

    # Get the diffs of the pull request
    pull_request_diffs = [
        {
            "filename": file.filename,
            "patch": file.patch
        }
        for file in pull_request.get_files()
    ]

    # Get the commit messages associated with the pull request
    commit_messages = [commit.commit.message for commit in pull_request.get_commits()]

    # Format data for OpenAI prompt
    prompt = format_data_for_openai(pull_request_diffs, index_content, commit_messages)

    # Call OpenAI to generate the updated Index.md content
    updated_index = call_openai(prompt)

    # Create PR for Updated PR
    update_index_and_create_pr(repo, updated_index, index_content.sha)

if __name__ == '__main__':
    main()
