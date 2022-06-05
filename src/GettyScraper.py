from bs4 import BeautifulSoup as BS
import sys
import json
import requests as rq

params_without_groupbevent = {
    "photographer?photographer": "katelyn mulcahy",
    "family": "editorial",
    "assettype": "image",
}
params = params_without_groupbevent.copy()
params["groupbyevent"] = "true"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/102.0.5005.61 Safari/537.36"
    )
}
katelyn_url = "https://www.gettyimages.com/search/"
katelyn_url_without_groupbyevent = "https://www.gettyimages.com/search/"

for i, key in enumerate(params):
    add_str = key + "=" + params[key].replace(" ", "+")
    if i != len(params) - 1:
        add_str += "&"
    katelyn_url += add_str
for i, key in enumerate(params_without_groupbevent):
    add_str = key + "=" + params_without_groupbevent[key].replace(" ", "+")
    if i != len(params_without_groupbevent) - 1:
        add_str += "&"
    katelyn_url_without_groupbyevent += add_str

r = rq.get(katelyn_url, headers=headers)
print("Getting data from {}".format(r.url))
soup = BS(r.content, "lxml")

page_json_str = soup.find("main", "search-main").find("script").string

page_gallery = json.loads(page_json_str)["search"]["gallery"]
# print(page_gallery.keys())
# print(page_gallery)

# These dictionaries will store all the data.
# uiid_to_data will store images by their unique image ID to all the image data
# that Getty has.
# event_uiid_to_data will first group images by event, then by unique image ID
# to all data
uiid_to_data = {}
event_to_uiid_to_data = {}

# Some global info that can be retrieved from the first page
total_images = page_gallery["groupByEventTotalAssets"]
total_events = page_gallery["groupByEventCount"]
total_search_results = page_gallery["totalNumberOfResults"]
total_pages = page_gallery["lastPage"]

print()
print("Total images = {}".format(total_images))
print("Total events = {}".format(total_events))
print("Total pages of events = {}\n".format(total_pages))

print("Looping over all events")
for i in range(1, total_pages + 1):
    print(" Getting data for event page {}".format(i), end=". ")
    page_url = katelyn_url + "&page={}".format(i)
    soup = BS(rq.get(page_url, headers=headers).content, "lxml")

    page_json_str = soup.find("main", "search-main").find("script").string
    event_gallery = json.loads(page_json_str)["search"]["gallery"]

    current_page = event_gallery["page"]
    if current_page != i:
        sys.exit(
            "Page index {} is not equal to the current page number {}".format(
                i, current_page
            )
        )

    events = event_gallery["assets"]
    events_on_this_page = len(events)
    print("There are {} events on this page.".format(events_on_this_page))
    print(" url = {}".format(page_url))

    print(" Looping over events on this page...")
    for j in range(events_on_this_page):
        event = events[j]
        event_id = event["eventId"]
        event_url = katelyn_url_without_groupbyevent + "&events={}".format(
            event_id
        )
        print(
            "  Parsing images from event {} with id {}".format(j + 1, event_id)
        )

        if event_id in event_to_uiid_to_data:
            print("   Already saw event id {} before".format(event_id))

        event_soup = BS(
            rq.get(event_url + "&page=1", headers=headers).content, "lxml"
        )

        event_json_str = (
            event_soup.find("main", "search-main").find("script").string
        )
        image_gallery = json.loads(event_json_str)["search"]["gallery"]

        event_total_search_results = image_gallery["totalNumberOfResults"]
        event_total_pages = image_gallery["lastPage"]

        images = image_gallery["assets"]
        images_on_this_page = len(images)

        for k in range(images_on_this_page):
            image = images[k]
            uiid = image["id"]
            uiid_to_data[uiid] = image
            if event_id in event_to_uiid_to_data:
                event_to_uiid_to_data[event_id][uiid] = image
            else:
                event_to_uiid_to_data[event_id] = {uiid: image}

        # If there's only one page, go to next event because we already parsed it
        if not event_total_pages > 1:
            continue

        # Loop through the rest of the pages for this event
        for m in range(1, event_total_pages):
            event_soup = BS(
                rq.get(
                    event_url + "&page={}".format(m), headers=headers
                ).content,
                "lxml",
            )

            event_json_str = (
                event_soup.find("main", "search-main").find("script").string
            )
            image_gallery = json.loads(event_json_str)["search"]["gallery"]
            images = image_gallery["assets"]
            images_on_this_page = len(images)

            for k in range(images_on_this_page):
                image = images[k]
                uiid = image["id"]
                uiid_to_data[uiid] = image
                # This event_id is guaranteed to exist because we aren't on the
                # first page anymore
                event_to_uiid_to_data[event_id][uiid] = image

print("Finished parsing Katelyn's images! :)")
