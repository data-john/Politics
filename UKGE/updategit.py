
import subprocess
from UKGE import run_sim, update_export

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
    run_sim()
    # create_output()
    update_export(from_path="UKGE/outputs/EXPORT.csv", to_path="UKGE/outputs/EXPORT.csv")
    stage_commit_push()

main()