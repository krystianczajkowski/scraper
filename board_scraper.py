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

    validate_input()
    timestamp = int(time())
    change_dirs(sys.argv[1])
    get_thread_contents(get_thread_no(get_threads(timestamp)))


def validate_input():
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
    if len(sys.argv) != 2:
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


def get_threads(timestamp=0):
    """Get a list of all threads from a board, check timestamps of all threads and update them."""
    print("Downloading list of threads")
    r = requests.get(f"https://a.4cdn.org/{sys.argv[1]}/threads.json")
    sleep(1)

    # code below needs retinking
    # while thread not updated cont
    # else download images
    # repeat
    
    if r.ok:
        data = r.json()
        # data[0]["threads"][0]["last_modified"]
        if os.path.exists("timestamp.txt"):
            with open("timestamp.txt", "r") as f:
                old_timestamp = int(f.readline())
                # TODO if timestamp now is older than 10 seconds check if threads were modified
                if (result := timestamp - old_timestamp) > 10:
                    print(f"Last update: {result} seconds ago.")
                    f.close()

                    # loop through all posts and check if timestamps are newer than the one in file
                    for _, page in enumerate(data):
                        for _, post in enumerate(page["threads"]):
                            if post["last_modified"] > old_timestamp:
                                old_timestamp = post["last_modified"]

                    with open("timestamp.txt", "w") as file:
                        file.write(str(timestamp))
        else:
            with open("timestamp.txt", "w") as file:
                file.write(str(timestamp))

        return data

    else:
        exit(f"Error {r.status_code} Something broke!")


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
        sleep(1.01)
        
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
                sys.stdout.write("\rNo image found!")
                sys.stdout.flush()
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
        "\r[%s%s] %d b/%d b "
        % ("█" * percentage, " " * (50 - percentage), dwnl, size)
    )
    sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborting!")
        exit(130)
