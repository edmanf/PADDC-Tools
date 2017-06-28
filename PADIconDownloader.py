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
	print(sys.argv)
	file = open("padjson.json")
	monstersJson = json.load(file)
	
	list = os.listdir(FOLDER_PATH)
	if len(list) != len(monstersJson):
		for monster in monstersJson:
			path = "Monster Icons/" + str(monster["id"]) + ".png"
			if not os.path.isfile(path):
				img = open(path, "wb")
				url = BASE_ICON_URL + monster["image60_href"]
				r = requests.get(url)
				img.write(r.content)
	else:
		print("No DL necessary.")
		
if __name__ == "__main__":
	main()