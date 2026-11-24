# Setting up Flask Lab

## Clean Setup

1. Cannot build in Shared Folder between VM and Windows host.
2. Install uv to manage environment:
   1. `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Have to install the Tkinter System Package to work with the SampleNetworkServer.py
   1. `sudo apt update && sudo apt install -y python3-tk tk-dev`
   2. `uv sync --reinstall`
4. Need to install python3.11 in addition to pyton3.12 for this project

```shell
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-tk
python3.11 --version
python3 --version
```

5. Install Python3.11 with uv

```shell
cd lab3
uv python pin /usr/bin/python3.11
uv add -r requirements.txt
uv sync
uv run python SampleNetworkServer.py
```

6. Run Flask so that you can access from outside VM (via host machine)

```shell
export FLASK_APP="app.py"
uv run flask run --host 0.0.0.0 --port 5000
```

7. SQLi: 

```sql
a' OR 'b' = 'b
```

Output:

```
:101:b'0123456789abcdef\xd7\xfa]\x82\xa1\xdf\x98\x9bu/\x06\x8d+vS\x7f\xddl\x02I\xe6\xb4\x80\xde\xbbw\xef\x10Q\xbbR\xe5\xb7\x9eqHq\xaf}\xf8':!Q#E%T&U8i6y4r2w
```

Password: 
SQLi_is_easier_than_this

8. Add support for .env file in project
   1. `uv add python-dotenv`
   2. add the following to the .env file

```shell
FLASK_APP=app.py
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
FLASK_DEBUG=1
```

    3. Now you can run flask with `uv run flask run`

## Setup Gitrepo for the project

1. setup .gitignore

```shell
cat << 'EOF' > .gitignore
# Virtual environment
.venv/
env/
venv/

# Environment variables / secrets
.env

# Python bytecode and cache
__pycache__/
*.py[cod]
*$py.class

# IDE and OS settings
.vscode/
.idea/
.DS_Store
EOF
```

2. Get the repo ready

```shell
git add .
git commit -m "Initial commit of Flask app with uv configuration"
git remote -v
git remote set-url origin git@github.com:ds7389/ISSEM-Lab03.git
git remote add origin git@github.com:ds7389/ISSEM-Lab03.git
git push -u origin main
```

# Git

## Creating and Switching Branches

```shell
# create new branch
git checkout -b TLS_Implementation

# commit and push to branch on github
git add .
git commit -m "TLS Implementation: ..."
git push -u origin TLS_Implementation

# Switch back to main
git checkout main

# create next branch
git checkout -b DTLS_Implementation

# follow previous steps to do updates and push to github, switch back to main
#   And then create final branch
git checkout -b HMAC_Implementation

```



## Merging a Branch with Main

### CLI Merge

```python
git checkout main
git pull origin main
git merge DTLS_Implementation
git push origin main
```

### Pull Request Merge Option

Step 1: Set Up GitHub Pull Requests for Team Review
The best way for your team to inspect, run, and vote on the options is by opening Draft Pull Requests:
Go to your repository on GitHub.
Click the Pull Requests tab > New Pull Request.
Set base: main and compare: option-a.
Click Create Pull Request (or select Create Draft Pull Request from the dropdown).
Repeat this process for option-b and option-c.

Step 2: Finalize the Winning Option
Once your team votes and decides on a winner (for example, DTLS_Implementation):
Merge the winning PR: Click Merge Pull Request on the option-b PR on GitHub (or merge it locally into main and push).
Close the remaining PRs: Close the PRs for option-a and option-c without merging.

Clean up old branches (Optional): Delete the unmerged feature branches on GitHub and locally:

```shell
# Switch back to main and get the updated code
git checkout main
git pull origin main

# Delete local branches
git branch -d option-a option-b option-c

# Delete remote branches on GitHub
git push origin --delete option-a option-c
```

---

# Appendix

## Running with `uv`

- https://docs.astral.sh/uv/#highlights
- https://docs.astral.sh/uv/getting-started/first-steps/
- https://docs.astral.sh/uv/guides/projects/#managing-dependencies

1. Run your Flask applicationInstead of manually activating the virtual environment every time (e.g., source .venv/bin/activate), run your commands directly through uv run:
```Bash
uv run flask run
```

(Or `uv run python app.py`, depending on how your Flask entry point is configured).

Common `uv` Workflow Quick-Reference

| Action | Command |
| ------ | ------- |
| Add a new package             | `uv add <package-name>` | 
| Remove a package              | `uv remove <package-name>` | 
| Run arbitrary scripts         | `uv run <command>` | 
| Upgrade all lock dependencies | `uv lock --upgrade` | 


## Mess of a Setup

These are some missteps along the way. 
For reference only.  
Do not follow these.

1. Cannot build in Shared Folder between VM and Windows host. 
2. Install uv to manage environment:
   1. `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. In root of "lab3" folder:
   1. `uv init --bare`
   2. `uv python pin 3.11`
   3. `uv add -r requirements.txt`
   4. `uv sync`
   5. `uv run python SampleNetworkServer.py`
4. Have to install the Tkinter System Package to work with the SampleNetworkServer.py
   1. `sudo apt update && sudo apt install -y python3-tk tk-dev`
   2. `uv sync --reinstall`

Need to install python3.11 in addition to python3.12:
```shell
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-tk
python3.11 --version
python3 --version
```

Install Python3.11 with uv

```shell
cd lab3
rm -rf .venv
uv python pin /usr/bin/python3.11
uv add -r requirements.txt
uv sync
uv run python SampleNetworkServer.py
```
