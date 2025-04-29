import os
import re
import json
import subprocess
import sys
from googleapiclient.discovery import build

api_key = 'AIzaSyBIUhbqCYtcoIDxc1BmNqt9TXTpODE_bKM'
youtube = build("youtube", "v3", developerKey=api_key)
path = "links.txt"

RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

RAM = []
MEMORY = []

def main():
    run = True
    help()
    memory()
    while run:
        try:
            print(f"{MAGENTA}[*]══╗ # ", end="")
            ipt = input().strip()

            cmd = ipt.split(" ")[0]
            t1 = re.findall(r'\"([^\"]+)\"|\S+', ipt)[1] if len(re.findall(r'\"([^\"]+)\"|\S+', ipt)) > 1 else None
            t2 = ipt.split(" ")[1] if len(ipt.split(" ")) > 1 else None
            arg = t1 if t1 else t2

            match cmd:
                case "quit":
                    run = False
                case "memory":
                    memory()
                case "rm_memory":
                    rm_memory(arg)
                case "help":
                    help()
                case "remove":
                    remove(arg)
                case "clear":
                    clear()
                case "search":
                    search(arg)
                case "ram":
                    readRAM()
                case "get":
                    get(arg)
                case "install":
                    install(arg)
                case _:
                    read("Invalid Command", RED)
        except Exception as e:
            read(f"Error: {e}", RED)

def help():
    try:
        read(f"{'Command':<20} Description", MAGENTA)
        read("═" * 40, MAGENTA)
        read(f"{'help':<20} Show All Commands", MAGENTA)
        read(f"{'clear':<20} Clear Screen", MAGENTA)
        read(f"{'memory':<20} Show All Links In Memory", MAGENTA)
        read(f"{'rm_memory':<20} Remove Link By ID", MAGENTA)
        read(f"{'remove <id>':<20} Remove Link With ID", MAGENTA)
        read(f"{'search <title>':<20} Search Music On YouTube", MAGENTA)
        read(f"{'ram':<20} Show All Ram", MAGENTA)
        read(f"{'get <id>':<20} Add Music To MEMORY By ID", MAGENTA)
        read(f"{'quit':<20} Quit The Program", MAGENTA)
        read("═" * 40, MAGENTA)
    except Exception as e:
        read(f"Error in help(): {e}", RED)

def get(id):
    try:
        id = int(id) - 1
        title = RAM[id]["title"]
        url = RAM[id]["url"]
        duration = RAM[id]["duration"]
    except (IndexError, ValueError) as e:
        read(f"Error: {e}", RED)
        return
    
    try:
        with open(path, "r") as f:
            temp = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        temp = []
    
    add = {"title": title, "url": url, "duration": duration}
    temp.append(add)

    try:
        with open(path, "w") as f:
            json.dump(temp, f)
        read(f"Added '{title}' to {path}!", GREEN)
    except Exception as e:
        read(f"Error adding to file: {e}", RED)

def install(arg):
    try:
        loadMEMORY()
        if arg == '*':
            for link in MEMORY:
                download(link["url"])
        else:
            try:
                arg = int(arg) - 1
                download(MEMORY[arg]["url"])
            except (ValueError, IndexError):
                read("Invalid argument", RED)
    except Exception as e:
        read(f"Error in install: {e}", RED)

def download(url):
    try:
        read(f"[*] Starting download from {url}", YELLOW)
        check_yt_dlp()
        
        cmd = [
            "yt-dlp",
            "-x", "--audio-format", "mp3", "--audio-quality", "0", "--no-playlist",
            "--no-mtime", "--no-write-thumbnail", "--no-write-sub", "--no-write-info-json", "--no-check-certificate",
            "--prefer-free-formats", url
        ]
        
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        read(f"Download completed successfully! Output: {result.stdout.strip()}", GREEN)
    except subprocess.CalledProcessError as e:
        read(f"Error: Failed to download the video. {e.stderr.strip()}", RED)
    except Exception as e:
        read(f"Unexpected error in download: {e}", RED)

def check_yt_dlp():
    try:
        result = subprocess.run(["yt-dlp", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        read(f"[*] yt-dlp version: {result.stdout.strip()}", GREEN)
    except (subprocess.CalledProcessError, FileNotFoundError):
        read("[*] yt-dlp is not installed.", RED)

        choice = input("[?]  ╚═╗ Do you want to install yt-dlp now? (y/n): ").strip().lower()
        if choice != 'y':
            read("[!] yt-dlp is required to continue. Exiting program.", RED)
            sys.exit(1)
        
        read("[*] Installing yt-dlp...", YELLOW)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            read("[*] yt-dlp was successfully installed.", GREEN)
        except subprocess.CalledProcessError:
            read("[!] Error: Unable to install yt-dlp automatically.", RED)
            sys.exit(1)

def search(title):
    try:
        request = youtube.search().list(
            part="snippet", q=title, type="video", maxResults=30
        )
        response = request.execute()

        resetRAM()
        video_ids = []

        for item in response.get('items', []):
            video_id = item.get('id', {}).get('videoId')
            if video_id:
                video_ids.append(video_id)

        if not video_ids:
            read("Aucune vidéo trouvée.", RED)
            return

        details_request = youtube.videos().list(
            part="contentDetails", id=",".join(video_ids)
        )
        details_response = details_request.execute()

        durations = {}
        for item in details_response['items']:
            video_id = item['id']
            duration = item['contentDetails']['duration']
            durations[video_id] = duration

        for i, item in enumerate(response['items']):
            title = item['snippet']['title']
            video_id = item['id'].get('videoId', 'Unknown')
            url = f"https://www.youtube.com/watch?v={video_id}"
            duration = durations.get(video_id, "Unknown")

            inf = {
                "id": i + 1,
                "title": title,
                "url": url,
                "duration": parse_duration(duration)
            }

            addToRAM(inf)
        readRAM()
    except Exception as e:
        read(f"Error in search: {e}", RED)

def memory():
    try:
        with open(path, "r") as f:
            links = json.loads(f.read())

        read(f"{'ID':<10} {'Link':<50} {"duration":<10}", MAGENTA)
        read("═" * 72, GREEN)

        for i, link in enumerate(links):
            title = link['title']
            duration = link["duration"]
            if len(title) > 50:
                title = title[:47] + "..."
            msg = f"{i+1:<10} {title:<50} {duration:<10}"
            read(msg, GREEN)

        read("═" * 72, GREEN)
    except Exception as e:
        read(f"Error in memory: {e}", RED)


def rm_memory(id):
    try:
        id = int(id) - 1
    except ValueError:
        read("L'ID doit être un nombre valide.", RED)
        return

    loadMEMORY()

    if id < 0 or id >= len(MEMORY):
        read("ID hors de portée.", RED)
        return

    read(f"Suppression de l'élément avec l'ID {id + 1}.", GREEN)
    del MEMORY[id]
    updateMEMORY()

def loadMEMORY():
    global MEMORY
    try:
        with open(path, "r") as f:
            MEMORY = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        MEMORY = []
        read("Aucun fichier mémoire trouvé, initialisation de MEMORY vide.", YELLOW)

def updateMEMORY():
    try:
        with open(path, "w") as f:
            json.dump(MEMORY, f)
        read("La mémoire a été mise à jour avec succès.", GREEN)
    except Exception as e:
        read(f"Erreur lors de la mise à jour du fichier mémoire : {e}", RED)

def remove(id):
    try:
        id = int(id) - 1
    except ValueError:
        read("ID is not a valid number", RED)
        return

    try:
        with open("link.txt", "r") as f:
            links = f.readlines()

        if 0 <= id < len(links):
            read(f"Are you sure you want to remove the link: {links[id].strip()}? (yes/no)", YELLOW)
            confirm = input().strip().lower()

            if confirm == "yes":
                del links[id]
                with open("link.txt", "w") as f:
                    f.writelines(links)
                read("Link removed successfully.", GREEN)
            else:
                read("Removal canceled.", GREEN)
        else:
            read("Invalid ID.", RED)
    except Exception as e:
        read(f"Error in remove: {e}", RED)

def resetRAM():
    global RAM
    RAM = []

def addToRAM(inf):
    RAM.append(inf)

def readRAM():
    try:
        if RAM:
               read(f"{"ID":<10} {"name":<50} {"duration":<10}", MAGENTA)
               read("═" * 72, GREEN)
               for i, inf in enumerate(RAM):
                    title = inf['title']
                    if len(title) > 50:
                         title = title[:47] + "..."
                    read(f"{i+1:<10} {title:<50} {inf['duration']:<10}", GREEN)
               read("═" * 72, GREEN)
        else:
            read("No links in RAM.", RED)
    except Exception as e:
        read(f"Error in readRAM: {e}", RED)

def parse_duration(duration):
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
    hours, minutes, seconds = match.groups()

    hours = int(hours[:-1]) if hours else 0
    minutes = int(minutes[:-1]) if minutes else 0
    seconds = int(seconds[:-1]) if seconds else 0

    return f"{hours:02}:{minutes:02}:{seconds:02}"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def read(text, color):
    print(f"{color}{BOLD}[*]  ╚═╗ {text}{RESET}")

main()