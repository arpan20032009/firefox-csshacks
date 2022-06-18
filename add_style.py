#!/usr/bin/env python3

#
# usage:
#   add_style.py <file_name> <tags>
# 
# where <tags> is a space-separated list of tags to apply
# for that style (1 minimum). Creates a new file to
# chrome/ folder and updates tags.csv and docs/tagmap.json
#
# OR
#
#   add_style.py --update-only
#
# updates docs/tagmap.json based on tags.csv without creating anything
#
# OR
#
#   add_style.py --list
#
# shows a list of unique tags used in tags.csv

import sys, os

def filterEmpty(list):
    for i in range(2,len(list)):
        if list[i] == "":
            del list[i]

def createJSON(tagmap,filename,args,onlyupdate):
    charBuffer = "{\n"
    map_last = len(tagmap) - 1
    n_line=0
    for line in tagmap:
        tokens = line.rsplit(",")
        filterEmpty(tokens)
        if len(tokens) < 2:
            continue
        charBuffer += f'\"{tokens[0]}\":['
        for t in range(1,len(tokens)):
     #      if len(tokens[t]) > 0:
            charBuffer += f'\"{tokens[t]}\"'
            if t < len(tokens)-1:
                charBuffer += ","
        if n_line >= map_last and onlyupdate:
            charBuffer += "]\n}"
            break
        else:
            charBuffer += "],\n"
        n_line += 1
    if not(onlyupdate):
        charBuffer += f'\"{filename}\":['
        for t in range(len(args)):
            charBuffer += f'\"{args[t]}\"'
            if t < len(args) - 1:
                charBuffer += ","
        charBuffer += "]\n}"

    with open("html_resources/tagmap.json","w") as json:
      print(charBuffer,file=json)
      print("wrote JSON\n")
       

def searchFile(tagmap,name):
    return any(name in line for line in tagmap)

def createNewFile(name,folder):
    filesuffix = f"{folder}/{name}"
    text = f"/* Source file https://github.com/MrOtherGuy/firefox-csshacks/tree/master/{filesuffix} made available under Mozilla Public License v. 2.0\nSee the above repository for updates as well as full license text. */\n"


    if os.path.isfile(filesuffix):
        confirm = input(
            f"File {filesuffix} already exists! proceed (will overwrite) ? [y/N] "
        )

        if confirm != "y":
            print("Aborted")
            return False


    with open(filesuffix,"w") as css:
        print(text,file=css)
        print(f"Created file: {filesuffix}")
        return True


class TaskMode:
    def __init__(self,args):
        self.show_help = len(args) < 2 or (args[1] == "-h")
        if self.show_help:
            self.update_only = False
            self.list_tags = False
            self.normal = False
        else:
            self.update_only = args[1] in ["--update-only", "-update-only", "-u"]
            self.list_tags = args[1] in ["--list", "-list", "-l"]
            self.normal = not self.update_only and (not self.list_tags)
        self.min_arg_length = (3 if self.normal else 2) 

def printCurrentTags(filecontent):
    tags = [];
    for line in filecontent:
        tokens = line.rsplit(",")
        filterEmpty(tokens)
        if len(tokens) < 2:
            continue
        for t in range(1,len(tokens)):
            if tags.count(tokens[t]) == 0:
                tags.append(tokens[t])
    tags.sort()
    print("\n".join(tags))
    


if __name__ == "__main__":

    runmode = TaskMode(sys.argv)

    if runmode.show_help or len(sys.argv) < runmode.min_arg_length:
        print("usage: add_file.py <filename> <list_of_tags>")
        exit()

    args = [sys.argv[i] for i in range (2,(len(sys.argv)))]
    name = sys.argv[1]

    if not(runmode.update_only) and not(name.endswith(".css")):
        name += ".css"
    # For the moment files in content/ are not tagged, but the script can still create the css files
    folder = "content" if ("-content" in sys.argv) else "chrome"

    if(folder == "content") and not(runmode.update_only):
        createNewFile(name,folder)
        print("Done")
        exit(0)

    with open("tags.csv") as tagfile:
        tagmap = tagfile.read().lstrip().splitlines()
    if runmode.normal and searchFile(tagmap,name):
        print(f"{name}exist already")
    elif runmode.normal:
        exists = createNewFile(name,folder)
        with open("tags.csv","a") as tagfile:
            tagfile.write(f"{name}," + ",".join(args) + "\n")
        createJSON(tagmap,name,args,runmode.update_only)
    elif runmode.update_only:
        print("Only update json")
        createJSON(tagmap,name,args,runmode.update_only)
    elif runmode.list_tags:
        print("listing tags...")
        printCurrentTags(tagmap)
    else:
        print("this shouldn't happen!")
    # print("Done")
    exit(0)
