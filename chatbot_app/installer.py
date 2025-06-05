import subprocess

known_software = {
    "zoom": "Zoom.Zoom",
    "slack": "SlackTechnologies.Slack",
    "chrome": "Google.Chrome",
    "outlook": "Microsoft.Outlook",
    "teams": "Microsoft.Teams",
    "vscode": "Microsoft.VisualStudioCode",
    "vlc": "VideoLAN.VLC",
    "python": "Python.Python.3",
    "discord": "Discord.Discord"
}

def install_software(software_name):
    pkg_id = known_software.get(software_name.lower())
    if not pkg_id:
        return f"I don’t recognize '{software_name}' as installable software."
    
    try:
        subprocess.run(["winget", "install", "--id", pkg_id, "-e", "--silent"], check=True)
        return f"'{software_name}' installation started."
    except subprocess.CalledProcessError:
        return f"Failed to install '{software_name}'."

def uninstall_software(software_name):
    try:
        subprocess.run(f"winget uninstall {software_name}", shell=True, check=True)
        return f"{software_name.capitalize()} has been uninstalled successfully."
    except Exception as e:
        return f"Failed to uninstall {software_name}: {str(e)}"

def update_software(software_name):
    try:
        subprocess.run(f"winget upgrade {software_name}", shell=True, check=True)
        return f"{software_name.capitalize()} has been updated successfully."
    except Exception as e:
        return f"Failed to update {software_name}: {str(e)}"
