import re
from requests import request

class URLParser:
    endpoint = "https://shazam.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-host": "shazam.p.rapidapi.com",
        "x-rapidapi-key": "9fcd883b3fmsh746113fe5da7b2fp19b2e3jsn5a01a7483b93"
    }
    
    def __init__(self, url) -> None:
        self.url = url
        self.song_id = None
    
    def process(self):
        self.song = {
            "url": self.url
        }
        req_params = {
            "term": self.processURL(self.url),
            "locale": "en-US",
            "offset": 0,
            "limit": 20
        }
        res = request("GET", self.endpoint, params=req_params, headers=self.headers)
        self.processResponse(res.json(), True if "single" in self.url else False)
        return self.song

    def processResponse(self, res, single):
        hits = res["tracks"]["hits"]
        for track_obj in hits:
            track = track_obj["track"]
            if single:
                title = track["title"].strip().lower()
                stripped_title = re.compile("[,\.!?']").sub("", title).casefold()
                if stripped_title == self.song["album"]:
                    self.song["artwork"] = track["images"]["coverart"]
                    self.song["title"] = track["title"]
                    self.song["artist"] = track["subtitle"]
                    self.song["url"] = self.url
                    return 1
            else:
                track_id = track["hub"]["actions"][0]["id"]
                if track_id == self.song["songId"]:
                    self.song["artwork"] = track["images"]["coverart"]
                    self.song["title"] = track["title"]
                    self.song["artist"] = track["subtitle"]
                    self.song["url"] = self.url
                    return 1
        return 0
        

    def processURL(self, url):
        # res = re.match(re.compile(r"https://music\.apple\.com/\w+/album/((\w+\W+)+)\/?(\d+)$"), url)
        url = (url.split("/"))[-1:-3:-1]
        album_name = " ".join(url[1].split("-"))
        if "single" in album_name:
            album_name = album_name.replace("single", "")
            print(album_name)
        song_id = (url[0].split("="))[1]
        self.song["songId"] = song_id.strip()
        self.song["album"] = album_name.strip()
        return album_name

if __name__=="__main__":
    u = URLParser("https://music.apple.com/us/album/california-dreamin-single/1440795791?i=1440796325")
    print(u.process())
    print(u.song)
    # print(u.processURL("https://music.apple.com/us/album/not-for-long-feat-trey-songz/924502453?i=924502475"))