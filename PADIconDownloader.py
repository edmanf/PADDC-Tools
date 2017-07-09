import requests
import io
import json
import os
import sys

BASE_ICON_URL = "https://padherder.com"
SMALL_ICON_URL = "image40_href"
LARGE_ICON_URL = "image60_href"
FOLDER_PATH = "./Monster Icons"

def main():
    if len(sys.argv) < 3:
        usage()
    else:
        dirPath = sys.argv[1]
        if dirPath[-1] != "/":
            dirPath += "/"
        jsonFileName = sys.argv[2]
        file = open(jsonFileName)
        print("loading json")
        monstersJson = json.load(file)
        
        list = os.listdir(FOLDER_PATH)
        if len(list) != len(monstersJson):
            for monster in monstersJson:
                
                path = dirPath + str(monster["id"]) + ".png"
                if not os.path.isfile(path):
                    print("downloading " + str(monster["id"]))
                    img = open(path, "wb")
                    url = BASE_ICON_URL + monster["image60_href"]
                    r = requests.get(url)
                    img.write(r.content)
        else:
            print("No DL necessary.")

def usage():
    str = "./PADIconDOwnloader.py [directory path] [json file] [options]"
    print("Usage:")
    print(str)
    print("Options:\n\t-s image size \t large or small")
		
if __name__ == "__main__":
	main()