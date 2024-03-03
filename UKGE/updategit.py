
import subprocess

def navigate_to_folder():
    subprocess.run(["cd", "Desktop/Politics"])
    print("NAVIGATED TO POLITICS")

def stage_commit_push():
    # Stage changes
    subprocess.run(["git", "add", "."])

    # Commit changes with a message
    subprocess.run(["git", "commit", "-m", "Auto Update"])

    # Push changes to remote repository
    subprocess.run(["git", "push"])

def main():
    # navigate_to_folder()
    stage_commit_push()

main()