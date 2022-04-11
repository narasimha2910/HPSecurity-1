import os


def listDirectoryRecursively(startPath):
    tree = {}

    for root, dirs, files in os.walk(startPath):
        cd = root.replace(startPath, '')
        levels = filter(None, cd.split(os.sep)) if cd is not "" else []
        b = tree
        for level in levels:
            b = b[level]

        for dir in dirs:
            b[dir] = {}
        if len(files) > 0:
            b["files"] = files

    return tree


# if __name__ == "__main__":
#     tree = listDirectoryRecursively(
#         "/home/chandradhar/Projects/HPE/dcs-appserver-master/pv/dummy-tailgating")

#     print(f"The tree structure: {tree}")
