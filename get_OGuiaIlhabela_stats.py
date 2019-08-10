from bs4 import BeautifulSoup
import requests
import json

import humanize

#-----------------------------------------------------------------------------------------------------------------------
# Utility

def friendly_numbers(number, short_form=True):
	if len(str(number)) > 3 and len(str(number)) < 7:
		number_plus_k = str(number)[:len(str(number)) - 3] + "k"
		return number_plus_k

	elif len(str(number)) > 6:
		if short_form:
			items = humanize.intword(number).split(" ")
			return f"{items[0]} {items[1][:2]}"

		else:
			return humanize.intword(number)

	elif len(str(number)) < 4:
		return str(number)

#-----------------------------------------------------------------------------------------------------------------------

def get_channel_stats(url):
	page = requests.get(f"{url}/about").text

	parsed_page = BeautifulSoup(page, "html.parser")

	stats_elements = parsed_page.find_all(class_="about-stat")

	stats_list = []

	for element in stats_elements:
		try:
			stats_list.append(int(element.b.get_text().replace(".", "")))

		except AttributeError:
			pass
	
	return {
		"channel": parsed_page.meta["content"],
		"subscribers_count": stats_list[0],
		"total_views_count": stats_list[1],
		"url": url
	}

def get_video_stats(url):
	page = requests.get(f"{url}/about").text

	parsed_page = BeautifulSoup(page, "html.parser")

	views_element = parsed_page.find(class_="watch-view-count")

	views_count = int(views_element.get_text().split()[0].replace(".", ""))

	return {
		"title": parsed_page.meta["content"],
		"views_count": views_count,
		"url": url
	}

def print_channel_stats(channel):
	print(f"{channel['channel']}:\n ~ {friendly_numbers(channel['subscribers_count'])} Subscribers\n ~ {friendly_numbers(channel['total_views_count'])} Views")
	print("-"*50)

def print_video_stats(video):
	print(f"{video['title']}:\n ~ {friendly_numbers(video['views_count'])} Views")
	print("-"*50)
#-----------------------------------------------------------------------------------------------------------------------
# Running

# Get channel and videos stats
o_guia_ilhabela = get_channel_stats("https://www.youtube.com/OGuiaIlhabela")

praia_do_curral = get_video_stats("https://www.youtube.com/watch?v=UI17HoheqmU")
praia_dos_castelhanos = get_video_stats("https://www.youtube.com/watch?v=2iL3m2dxHGo")
ilha_das_cabras = get_video_stats("https://www.youtube.com/watch?v=-K5xfQ-R4yA")
pico_do_baepi = get_video_stats("https://www.youtube.com/watch?v=o8kStoOhZ5M")

videos = [praia_do_curral, praia_dos_castelhanos, ilha_das_cabras, pico_do_baepi]

# Print channel and videos stats
print_channel_stats(o_guia_ilhabela)
for video in sorted(videos, key=lambda video: video["views_count"], reverse=True):
	# Removing "O Guia Ilhabela" from the videos' titles
	video["title"] = video["title"].replace(" - O Guia Ilhabela", "")

	# Formatted Prints
	print_video_stats(video)

# Update previous_stats.json
with open("previous_stats.json", "w") as file:
	o_guia_ilhabela["videos"] = [video for video in videos]
	
	file.write(json.dumps(dict(o_guia_ilhabela), indent=4))

input("\nPress enter to exit.")