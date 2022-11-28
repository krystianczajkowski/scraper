"""
Board scraper for a mongolian basket weaving forum.

"""

from time import sleep
import sys
import json
from click import progressbar
import requests
from datetime import date
import os
from blessed import Terminal


def main():

    validate_input()
    FILE_IO = sys.argv[1].upper() + " " + str(date.today()) + ".json"
    change_dirs(sys.argv[1])

    get_threads(FILE_IO)
    sleep(1.01)
    get_thread_contents(get_thread_no(FILE_IO))


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
        # didn't bother trying to google how to make this one line instead of three
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
        print(f"Current working directory: {os.getcwd()}")


def get_threads(filename, mode="x"):
    """Grabs a json of the whole board."""
    header = "If-Modified-Since"
    print("Downloading list of threads")
    r = requests.get(f"https://a.4cdn.org/{sys.argv[1]}/threads.json")
    if r.ok:
        try:
            with open(filename, mode) as f:
                f.write(json.dumps(r.json(), indent=4))
        except FileExistsError:
            print("List of threads already exists.")
            # ui = input("Do you want to overwrite it? yes/no ")
            # if ui == 'y' or ui == 'yes':
            #     get_threads(FILE_IO, 'w')
    else:
        exit(f"Error {r.status_code} Something broke!")


def get_thread_no(filename):
    """Separates thread numbers into a separate txt file."""

    with open(filename) as f:
        data = json.load(f)
        to_save = [
            e["threads"][j]["no"]
            for _, e in enumerate(data)
            for j, _ in enumerate(e["threads"])
            if e["threads"][j]["replies"] > 1
        ]

    print(len(to_save), "threads found")
    # TODO istead of saving this to a file just return it
    return to_save
    # TODO make this a generator?

    # output = f"threads_cleaned_{str(date.today())}.txt"

    # with open(output, "w") as f:
    #     for i, e in enumerate(to_save):
    #         if i == len(to_save) - 1:
    #             f.write(str(e))
    #         else:
    #             f.write(f"{e}\n")

    # return output


def get_thread_contents(threads):
    """Downloads all images from a board and separates them by thread"""
    t = Terminal()

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
                    f"{t.red}Replies: {post['replies']}\nImages: {post['images']}{t.normal}"
                )
            try:
                url = f"https://i.4cdn.org/{sys.argv[1]}/{post['tim']}{post['ext']}"
                name = f"{post['filename']}{post['ext']}"
                if os.path.exists(name):
                    print(f"{name} already exists! skipping.")
                    continue
                size = int(post['fsize'])
                req = requests.get(url)
                # download_img()
                dwnl = 0

                with open(name, "xb") as fi:
                    for chunk in req.iter_content(chunk_size=4096):
                        # sys.stdout.write(f"Downlading {name}\n")
                        fi.write(chunk)
                        dwnl += len(chunk)
                        percentage = int(50 * dwnl / size)
                        sys.stdout.write("\r[%s%s] %d/%d" % ('█' * percentage, ' ' * (50 - percentage), dwnl, size))
                        sys.stdout.flush()
                sleep(1)

            except KeyError:
                print("\nNo image found!")
                continue
            # print(url)
        os.chdir("..")


def download_img():
    pass
def draw_bar():
    pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Aborting!")
        exit(130)
