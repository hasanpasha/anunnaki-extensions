from requests import Request, Response, Session
from anunnaki_source.models import MediasPage, Media, Kind, Episode, Season, Video, Resolution, Subtitle, FileExtension
from anunnaki_source.online.http_source import HttpSource


class Cinemana(HttpSource):
    def __init__(self, session: Session = None) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,ar-EG;q=0.8,ar;q=0.7",
            "Connection": "keep-alive"
        }

        if not session:
            self.session = Session()
            self.session.headers = self.headers

    name = "cinemana"
    base_url = "https://cinemana.shabakaty.com"
    id = "shabakaty.cinemana"
    lang = "en"
    api_url = "https://cinemana.shabakaty.com/api/android"

    def search_media_request(self, query: str, page: int, filters: dict = None) -> Request:
        return Request('GET', f"{self.api_url}/AdvancedSearch?videoTitle={query}&page={page - 1}")

    def search_media_parse(self, response: Response) -> MediasPage:
        medias = self.__media_parser(response)
        return MediasPage(medias=medias, has_next=len(medias) > 0)

    def popular_media_request(self, page: int) -> Request:
        return Request(
            'GET', f"{self.api_url}/banner/level/0")

    def popular_media_parse(self, response: Response) -> MediasPage:
        medias = self.__media_parser(response)
        return MediasPage(medias=medias, has_next=False)

    def media_detail_request(self, media: Media) -> Request:
        return Request('GET', f"{self.api_url}/allVideoInfo/id/{media.slang}")

    def media_detail_parse(self, response: Response) -> Media:
        json = response.json()
        return Media(
            title=json['en_title'],
            url=f"{self.base_url}/video/{self.lang}/{json['nb']}"
        )

    def season_list_request(self, media: Media) -> Request:
        return Request('GET', f"{self.api_url}/videoSeason/id/{media.slang}")

    def season_list_parse(self, response: Response) -> list[Season]:
        json = response.json()
        un_episodes = self.__get_episodes(json=json)

        return [
            Season(season=str(s_nm), episodes=[
                Episode(
                    episode=f"season={s_nm} episode={ep_nm}",
                    slang=ep['nb'],
                    has_next=ep_nm != len(s),
                    is_special=ep['isSpecial'] == '1'
                )
                for ep_nm, ep in sorted(s.items())
            ], has_next=s_nm != len(un_episodes))
            for s_nm, s in sorted(un_episodes.items())
        ]

    def __get_episodes(self, json) -> dict[dict]:
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

    def video_list_request(self, episode: Episode) -> Request:
        return Request('GET', f"{self.api_url}/transcoddedFiles/id/{episode.slang}")

    def video_list_parse(self, response: Response) -> list[Video]:
        json = response.json()
        return [
            Video(url=s_json['videoUrl'],
                  resolution=Resolution(s_json['resolution']))
            for s_json in json
        ]

    def subtitle_list_request(self, episode: Episode) -> Request:
        return Request('GET', f"{self.api_url}/translationFiles/id/{episode.slang}")

    def subtitle_list_parse(self, response: Response) -> list[Subtitle]:
        try:
            subtitles = response.json()['translations']
        except:
            return []
        else:
            return [
                Subtitle(
                    url=subtitle['file'],
                    language=subtitle['type'],
                    extension=FileExtension(subtitle['extention'])
                )
                for subtitle in subtitles
            ]

    def __media_parser(self, response: Response) -> list[Media]:
        json = response.json()
        medias = [
            Media(
                title=media_json['en_title'],
                slang=media_json['nb'],
                # thumbnail_url=media_json['imgThumbObjUrl'],
                kind=Kind.MOVIES if media_json['kind'] == '1' else Kind.SERIES
            )
            for media_json in json
        ]
        return medias
