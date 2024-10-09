# aatt
Automate All the Things

Reference the actions here to add smart automation workflows to your projects

## Obsidian Glossary Updater

Include this action as a workflow in your obsidian vault github repository

### Expects

#### `OPENAI_API_KEY`
For accessing OpenAI api

#### `GH_TOKEN`, `REPO_PATH`, `PR_NUMBER`
To allow updates to your repository via the action you are using

#### `VAULT_PURPOSE`
Acts as a prompt modifier so the Glossary Updater can be used more generally.

Providing this GH Action with a well written `VAULT_PURPOSE` will help it to
more accurately define relevant Glossary terms with good definitions.


### How to use

1. define a new workflow in you obsidian vault

```yaml
# .github/workflows/update-glossary.yml

name: Update Glossary on Merge

on:
  pull_request:
    types: [closed]

jobs:
  update-glossary:
    runs-on: ubuntu-latest
    if: github.event.pull_request.merged == true  # Only run if the PR is merged

    steps:
      - name: Run Obsidian Glossary Updater
        uses: d-a-v-e/aatt/obsidian-glossary-updater@master
        with:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
          REPO_PATH: ${{ github.repository }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          VAULT_PURPOSE: "The purpose of this Obsidian vault is to ...."
```
2. Add your GH_TOKEN and OPENAI_API_KEY to your repository secrets
3. Merge a pull request that adds or modifies a note
4. That's it! You can expect to find an updated or newly created Glossary.md
   file in a new PR
