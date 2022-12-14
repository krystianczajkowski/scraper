"""
    Image scraper for a mongolian basket weaving forum.

"""
from time import (
    sleep,
    time,
)  # sleep for 1 second after each request to avoid breaking api rules
import sys
import requests
import os
from blessed import Terminal


def main():

    validate_input(2)
    change_dirs(sys.argv[1])
    get_thread_contents(get_thread_no(check_timestamp()))

def check_timestamp():
    """
        Return a JSON of all threads on the board.
        
        Check timestamp in the file, if it's older than 10 seconds update it else wait till they pass.
    """
    
    flag = False
    timestamp = int(time())
    if os.path.exists("timestamp.txt"):
        with open("timestamp.txt", "r") as f:
            old_timestamp = int(f.readline())
            # if timestamp now is older than 10 seconds check if threads were modified
            if (result := timestamp - old_timestamp) > 10:
                print(f"Last update: {result} seconds ago.")
                f.close()
                flag = True
                
            else:
                # following api rules
                print("Last update was less than 10 seconds ago!")
                for i in range(10-result,0,-1):
                    sys.stdout.write(f'\rWait {i}')
                    sys.stdout.flush()
                    sleep(1)
                sys.stdout.write('\n')
    else:
        old_timestamp = 0
    
    if flag:
        timestamp = max(timestamp, old_timestamp)

    data = get_threads()
    for _, page in enumerate(data):
        for _, post in enumerate(page["threads"]):
            if post["last_modified"] > old_timestamp:
                old_timestamp = post["last_modified"]

    with open("timestamp.txt", "w") as file:
        file.write(str(timestamp))
    return data
    


def validate_input(args : int):
    """Check if program is run with enough command-line arguments."""
    board_list = (
        "a",
        "c",
        "w",
        "m",
        "cgl",
        "cm",
        "n",
        "jp",
        "vp",
        "v",
        "vg",
        "vr",
        "co",
        "g",
        "tv",
        "k",
        "o",
        "an",
        "tg",
        "sp",
        "asp",
        "sci",
        "int",
        "out",
        "toy",
        "biz",
        "i",
        "po",
        "p",
        "ck",
        "ic",
        "wg",
        "mu",
        "fa",
        "3",
        "gd",
        "diy",
        "wsg",
        "s",
        "hc",
        "hm",
        "h",
        "e",
        "u",
        "d",
        "y",
        "t",
        "hr",
        "gif",
        "trv",
        "fit",
        "x",
        "lit",
        "adv",
        "lgbt",
        "mlp",
        "b",
        "r",
        "r9k",
        "pol",
        "soc",
        "s4s",
    )
    if len(sys.argv) != args:
        exit(f"Usage {sys.argv[0]} [board name]")
    elif sys.argv[1].lower() not in board_list:
        print("Board not found!\nAvailable boards:")
        print(*board_list)
        exit(1)


def change_dirs(dir_name):
    """Change current working directory to specified one, if not found create one."""

    try:
        print(f"Changing directory to {os.getcwd()}/{dir_name}")
        os.chdir(os.getcwd() + "/" + dir_name)
    except FileNotFoundError:
        print(f"Directory {dir_name} not found, creating...")
        os.system(f"mkdir {dir_name}")
        os.chdir(os.getcwd() + "/" + dir_name)
    finally:
        print(f"Current working directory: {os.getcwd()}")


def get_threads():
    """Get a list of all threads from a board, check timestamps of all threads and update them."""
    
    print("Getting a list of threads")
    
    r = requests.get(f"https://a.4cdn.org/{sys.argv[1]}/threads.json")
    
    sleep(1)
    
    if r.ok:
        return r.json()
    else:
        print(f"Error {r.status_code} Something broke!")
        exit(130)

def get_thread_no(data):
    """Separates thread numbers."""

    to_save = [
        e["threads"][j]["no"]
        for _, e in enumerate(data)
        for j, _ in enumerate(e["threads"])
        if e["threads"][j]["replies"] > 1
    ]

    print(len(to_save), "threads found")
    return to_save


def get_thread_contents(threads):
    """Downloads all images from a board and separates them into folders by thread name"""

    # for colors in terminal
    term = Terminal()

    for i, line in enumerate(threads):
        r = requests.get(f"https://a.4cdn.org/{sys.argv[1]}/thread/{line}.json")
        data = r.json()

        sys.stdout.write(f"Thread {i+1}/{len(threads)}")
        sys.stdout.write("\n")
        sys.stdout.flush()
        sleep(1)
        
        for j, post in enumerate(data["posts"]):
            if not j:
                change_dirs(post["semantic_url"])
                print(
                    f"{term.red}Replies: {post['replies']}\nImages: {post['images']}{term.normal}"
                )
            try:
                url = f"https://i.4cdn.org/{sys.argv[1]}/{post['tim']}{post['ext']}"
                name = post["filename"] + post["ext"]
                if os.path.exists(name):
                    print(f"{name} exists skipping.")
                    continue
                size = int(post["fsize"])
                req = requests.get(url)
                print(term.green)
                download_img(name, req, size)
                print(term.normal)

                sleep(1)

            except KeyError:
                continue
        os.chdir("..")


def download_img(name, request, size):
    """Download an image."""

    dwnl = 0
    with open(name, "xb") as fi:
        print(f"Donloading {name}")
        for chunk in request.iter_content(chunk_size=4096):
            fi.write(chunk)
            dwnl += len(chunk)
            draw_progress_bar(dwnl, size)


def draw_progress_bar(dwnl, size):
    """Draw a progress bar."""

    percentage = int(50 * dwnl / size)
    sys.stdout.write(
        "\r[%s%s] %d/%d KB"
        % ("█" * percentage, " " * (50 - percentage), dwnl//1000, size//1000)
    )
    sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborting!")
        exit(130)
