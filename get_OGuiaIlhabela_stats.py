from bs4 import BeautifulSoup
import requests
import json

import humanize

import milestones

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

def save_stats(list_of_stats):
	with open("previous_stats.json", "w") as f:
		channel_data = {}
		
		videos = []

		for i in list_of_stats:
			if "channel" in i:
				channel_data["channel"] = i["channel"]
				channel_data["subscribers_count"] = i["subscribers_count"]
				channel_data["total_views_count"] = i["total_views_count"]
				channel_data["url"] = i["url"]

			else:
				videos.append({
					"title": i["title"],
					"views_count": i["views_count"],
					"url": i["url"]
				})

		channel_data["videos"] = videos
		
		f.write(json.dumps(channel_data, indent=4))

def highlight_milestone(views=None, subscribers=None, milestone_type="channel"):
	with open("previous_stats.json") as f:
		channel_data = json.load(f)
		
		if views is not None:
			for video in channel_data["videos"]:
				for milestone in milestones.views_milestones:
					if views >= milestone and videos["total_views"] < milestone:
						return f"{{ {friendly_numbers(views)} }} (New Milestone)"

		if subscribers is not None:
			for video in channel_data["videos"]:
				for milestone in milestones.subscribers_milestones:
					if subscribers >= milestone and [] < milestone:
						return f"{{ {friendly_numbers(subscribers)} }} (New Milestone)"

		return None

def print_channel_stats(channel_stats):
	print(f"{channel_stats['channel']}:\n ~ {highlight_milestone(subscribers=channel_stats['subscribers_count'])} Subscribers\n ~ {highlight_milestone(views=channel_stats['total_views_count'])} Views")
	print("-"*50)

def print_video_stats(video_stats):
	print(f"{video_stats['title']}:\n ~ {friendly_numbers(video_stats['views_count'])} Views")
	print("-"*50)
#-----------------------------------------------------------------------------------------------------------------------
# Running

o_guia_ilhabela = get_channel_stats("https://www.youtube.com/OGuiaIlhabela")

praia_do_curral = get_video_stats("https://www.youtube.com/watch?v=UI17HoheqmU")
praia_dos_castelhanos = get_video_stats("https://www.youtube.com/watch?v=2iL3m2dxHGo")
ilha_das_cabras = get_video_stats("https://www.youtube.com/watch?v=-K5xfQ-R4yA")
pico_do_baepi = get_video_stats("https://www.youtube.com/watch?v=o8kStoOhZ5M")

videos = [praia_do_curral, praia_dos_castelhanos, ilha_das_cabras, pico_do_baepi]
print_channel_stats(o_guia_ilhabela)

for video in sorted(videos, key=lambda video: video["views_count"], reverse=True):
	# Removing "O Guia Ilhabela" from the videos' titles
	video["title"] = video["title"].replace(" - O Guia Ilhabela", "")

	# Formatted Prints
	print_video_stats(video)

save_stats([o_guia_ilhabela] + videos)

input("\nPress enter to exit.")