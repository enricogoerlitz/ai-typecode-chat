# flake8: noqa

import re
import requests
import gvars

from exc import errors
from requests import Response
from bs4 import BeautifulSoup


def fetch_url_content(url: str) -> str:
    resp = requests.get(url)
    result_html = resp.text
    if resp.status_code != 200:
        result_html = "<p>no content<p>"

    soup = BeautifulSoup(result_html, features="html.parser")

    prep_result = re.sub(r'\n{3,}', '\n\n', soup.text)
    return prep_result


class SERPResponseObject:
    def __init__(self, resp: Response) -> None:
        self._resp = resp
        self.obj = self._parse_response(resp)

    def _parse_response(self, resp: Response) -> dict:
        relevant_fields = {
            "organic_results": ["position", "title", "link", "snippet", "sitelinks"],
            "knowledge_graph": ["title", "website", "source", "description"],
            "top_stories": ["title", "link", "date"]
        }

        if resp.status_code != 200:
            raise errors.RequestsException(resp)

        resp_obj: dict = resp.json()
        obj = {"organic_results": [], "knowledge_graph": {}, "top_stories": []}

        # Process organic results
        if "organic_results" in resp_obj:
            for result in resp_obj["organic_results"]:
                filtered_result = {key: result.get(key) for key in relevant_fields["organic_results"] if key in result}
                if filtered_result:
                    obj["organic_results"].append(filtered_result)

        # Process knowledge graph
        if "knowledge_graph" in resp_obj:
            for key in relevant_fields["knowledge_graph"]:
                if key in resp_obj["knowledge_graph"]:
                    obj["knowledge_graph"][key] = resp_obj["knowledge_graph"].get(key)

        # Process top stories
        if "top_stories" in resp_obj:
            for story in resp_obj["top_stories"]:
                filtered_story = {key: story.get(key) for key in relevant_fields["top_stories"] if key in story}
                if filtered_story:
                    obj["top_stories"].append(filtered_story)

        return obj

    def get_links(self) -> list[str]:
        organic_results_links = [
            result.get("link")
            for result in self.obj.get("organic_results", [])
            if result.get("link", None) is not None
        ]

        organic_results_side_links = [
            inline_link.get("link")
            for result in self.obj.get("organic_results", [])
            for inline_link in result.get("sitelinks", {})
                                     .get("inline", [])
            if inline_link.get("link", None) is not None
        ]

        knowledge_graph_link = self.obj.get("knowledge_graph", {}).get("website", None)
        knowledge_graph_links = [] if knowledge_graph_link is None else [knowledge_graph_link]

        top_stories_links = [
            story.get("link")
            for story in self.obj.get("top_stories", [])
            if story.get("link", None) is not None
        ]

        return organic_results_links \
               + organic_results_side_links \
               + knowledge_graph_links \
               + top_stories_links

    def set_deep_search_results(self, results: list[dict]) -> None:
        self.obj["deep_search_results"] = results

    def set_websearch_summary(self, summary: str) -> None:
        self.obj["websearch_summary"] = summary

    def as_result_string(self) -> str:
        return str(self.obj) if "websearch_summary" not in self.obj else self.obj["websearch_summary"]


class WebSearchSERPClient:
    def __init__(
            self,
            api_key: str
    ) -> None:
        self._api_key = api_key
        self._url = "https://api.scaleserp.com/search"

    def search(
            self,
            query: str,
            max_results: int,
            country: str = "de"
    ) -> SERPResponseObject:
        # DOCS:     https://app.scaleserp.com/playground
        # CREDITS:  https://app.scaleserp.com/account
        params = {
            "api_key": "2DE5AAC9B5AE4059A6543453957F8132",
            "q": query,
            "hl": country,
            "include_ai_overview": "false",
            "num": max_results
        }

        response = requests.get(self._url, params)
        serp_obj = SERPResponseObject(response)
        return serp_obj


serp_client = WebSearchSERPClient(api_key=gvars.SERP_API_KEY)
