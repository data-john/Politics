import subprocess

def stage_commit_push():
    # Stage changes
    subprocess.run(["git", "add", "."])

    # Commit changes with a message
    subprocess.run(["git", "commit", "-m", "Your commit message"])

    # Push changes to remote repository
    subprocess.run(["git", "push"])

stage_commit_push()