
import subprocess
from UKGE import run_sim, update_export, today_results_exist
from polls import polls_have_changed

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
    if not polls_have_changed() and today_results_exist():
        return
    run_sim(n=8000)
    # create_output()
    update_export(from_path="UKGE/outputs/EXPORT.csv", to_path="UKGE/outputs/EXPORT.csv")
    stage_commit_push()
    
main()