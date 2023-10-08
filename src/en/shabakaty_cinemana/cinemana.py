from aiohttp import ClientSession, ClientResponse

from anunnaki_source.models import (
    MediasPage, Media, Kind, Episode, Season, SeasonList,
    Video, VideoList, Resolution, Subtitle, SubtitleList, FileExtension, FilterList
)
from anunnaki_source.online.http_source import HttpSource
from anunnaki_source.network import Request
from typing import List, Dict, Any


class Cinemana(HttpSource):
    name = "cinemana"
    pkg = "shabakaty_cinemana"
    lang = "en"
    id = 6766468217767473    
    base_url = "https://cinemana.shabakaty.com"
    api_url = "https://cinemana.shabakaty.com/api/android"
    support_latest = False

    def __init__(self, session: ClientSession = None, headers: Dict[str, Any] = None) -> None:
        self.headers = {}
        
        if session is not None:
            self.session = session

        if headers is not None:
            self.headers = headers

    async def search_media_request(self, query: str, page: int, filters: FilterList = None) -> Request:
        return Request('GET', url=f"{self.api_url}/AdvancedSearch?videoTitle={query}&page={(page-1)}")

    async def search_media_parse(self, response: ClientResponse) -> MediasPage:
        medias = await self.__media_parser(response)
        return MediasPage(medias=medias, has_next=len(medias) > 0)

    async def popular_media_request(self, page: int, filters: FilterList = None) -> Request:
        return Request(
            'GET', f"{self.api_url}/banner/level/0")

    async def popular_media_parse(self, response: ClientResponse) -> MediasPage:
        medias = await self.__media_parser(response, is_popular=True)
        return MediasPage(medias=medias, has_next=False)

    async def latest_media_request(self, page: int, filters: FilterList = None) -> Request:
        ...

    async def latest_media_parse(self, response: ClientResponse) -> MediasPage:
        ...

    async def media_detail_request(self, media: Media) -> Request:
        return Request('GET', f"{self.api_url}/allVideoInfo/id/{media.slug}")

    async def media_detail_parse(self, response: ClientResponse) -> Media:
        json = await response.json
        return Media(
            title=json['en_title'],
            url=f"{self.base_url}/video/{self.lang}/{json['nb']}",
            description=json[f'{self.lang}_content'],
            tags=[c[f'{self.lang}_title'] for c in json['categories']],
            thumbnail_url=json['imgObjUrl'],
        )

    async def season_list_request(self, media: Media) -> Request:
        return Request('GET', f"{self.api_url}/videoSeason/id/{media.slug}")

    async def season_list_parse(self, response: ClientResponse) -> SeasonList:
        json = await response.json
        un_episodes = self.__get_episodes(json=json)

        seasons = [
            Season(season=str(s_nm), episodes=[
                Episode(
                    episode=f"season={s_nm} episode={ep_nm}",
                    slug=ep['nb'],
                    has_next=ep_nm != len(s),
                    is_special=ep['isSpecial'] == '1'
                )
                for ep_nm, ep in sorted(s.items())
            ], has_next=s_nm != len(un_episodes))
            for s_nm, s in sorted(un_episodes.items())
        ]

        return SeasonList(root=seasons)

    def __get_episodes(self, json) -> dict[int, dict]:
        episodes = {}
        for episode in json:
            season_nm = int(episode['season'])
            episode_nm = int(episode['episodeNummer'])

            try:
                episodes[season_nm]
            except KeyError:
                episodes[season_nm] = {}
            finally:
                episodes[season_nm][episode_nm] = episode

        return episodes

    async def video_list_request(self, episode: Episode) -> Request:
        return Request('GET', f"{self.api_url}/transcoddedFiles/id/{episode.slug}")

    async def video_list_parse(self, response: ClientResponse) -> VideoList:
        json = response.json()
        videos = [Video(
                    url=s_json['videoUrl'],
                    resolution=Resolution(s_json['resolution']))
                    for s_json in json]
        return VideoList(root=videos)

    async def subtitle_list_request(self, episode: Episode) -> Request:
        return Request('GET', f"{self.api_url}/translationFiles/id/{episode.slug}")

    async def subtitle_list_parse(self, response: ClientResponse) -> SubtitleList:
        json = await response.json
        if 'translations' in json.keys():
            subtitles = [
                Subtitle(
                    url=subtitle['file'],
                    lang=subtitle['type'],
                    extension=FileExtension(subtitle['extention'])
                )
                for subtitle in json['translations']
            ]
        else:
            subtitles = []

        return SubtitleList(root=subtitles) 


    async def __media_parser(self, response: ClientResponse, is_popular: bool = False) -> List[Media]:
        json = await response.json()
        medias = [
            Media(
                title=media_json['en_title'],
                slug=media_json['nb'],
                thumbnail_url=f"https://cnth2.shabakaty.com/{media_json['imgMediumThumbObjUrl']}"
                if is_popular else media_json['imgMediumThumbObjUrl'],
                year=media_json['year'],
                kind=Kind.MOVIES if media_json['kind'] == '1' else Kind.SERIES
            )
            for media_json in json
        ]
        return medias
