import requests
import json
import logging
from typing import List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class TwitterClient:
    def __init__(self, auth_token: str, ct0: str):
        self.auth_token = auth_token
        self.ct0 = ct0
        self.headers = {
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "x-csrf-token": ct0,
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-client-language": "en",
            "x-twitter-active-user": "yes",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "cookie": f"auth_token={auth_token}; ct0={ct0}"
        }
        # Note: This ID is for ListLatestTweetsTimeline. It may change.
        # If it fails, you need to find the new QueryID for ListLatestTweetsTimeline
        self.graphql_id = "naCjgapXCSCsbZ7qnnItQA" 
        
    def extract_list_id(self, url: str) -> str:
        """Extracts list ID from a Twitter List URL."""
        if url.isdigit():
            return url
        
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")
        
        # Case: https://x.com/i/lists/12345678
        if "lists" in path_parts:
            idx = path_parts.index("lists")
            if idx + 1 < len(path_parts):
                potential_id = path_parts[idx + 1]
                if potential_id.isdigit():
                    return potential_id
        
        # If it's a named list, we might need to fetch the page to get the ID, 
        # but for now let's assume the user provides the ID or the numeric URL.
        return None

    def get_list_tweets(self, list_id: str, count: int = 20) -> List[Dict[str, Any]]:
        url = f"https://twitter.com/i/api/graphql/{self.graphql_id}/ListLatestTweetsTimeline"
        
        variables = {
            "listId": list_id,
            "count": count,
            "includePromotedContent": False,
            "withSuperFollowsUserFields": True,
            "withDownvotePerspective": False,
            "withReactionsMetadata": False,
            "withReactionsPerspective": False,
            "withSuperFollowsTweetFields": True
        }
        
        features = {
            "rweb_lists_timeline_redesign_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": False,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_media_download_video_enabled": False,
            "responsive_web_enhance_cards_enabled": False
        }

        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(features)
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return self._parse_response(response.json())
        except Exception as e:
            logger.error(f"Failed to fetch list tweets for {list_id}: {e}")
            return []

    def _parse_response(self, data):
        tweets = []
        try:
            # Navigate the complex GraphQL response
            # This path is fragile and depends on Twitter's API structure
            instructions = data.get('data', {}).get('list', {}).get('tweets_timeline', {}).get('timeline', {}).get('instructions', [])
            
            for instruction in instructions:
                if instruction['type'] == 'TimelineAddEntries':
                    for entry in instruction['entries']:
                        if entry['entryId'].startswith('tweet-'):
                            item_content = entry.get('content', {}).get('itemContent', {})
                            tweet_results = item_content.get('tweet_results', {}).get('result', {})
                            
                            # Handle retweets or simple tweets
                            if 'tweet' in tweet_results: # Sometimes it's nested
                                tweet_results = tweet_results['tweet']
                                
                            if 'legacy' in tweet_results:
                                legacy = tweet_results['legacy']
                                user_result = tweet_results.get('core', {}).get('user_results', {}).get('result', {})
                                user_legacy = user_result.get('legacy', {})
                                
                                # Try to get full text from note_tweet if available (for long tweets)
                                full_text = legacy['full_text']
                                if 'note_tweet' in tweet_results:
                                    try:
                                        note_text = tweet_results['note_tweet']['note_tweet_results']['result']['text']
                                        if note_text:
                                            full_text = note_text
                                    except (KeyError, TypeError):
                                        pass
                                
                                # Handle Quoted Tweet
                                if 'quoted_status_result' in tweet_results:
                                    try:
                                        quoted_result = tweet_results['quoted_status_result']['result']
                                        # Handle nested tweet object if present
                                        if 'tweet' in quoted_result:
                                            quoted_result = quoted_result['tweet']
                                            
                                        if 'legacy' in quoted_result:
                                            quoted_legacy = quoted_result['legacy']
                                            quoted_text = quoted_legacy['full_text']
                                            
                                            # Check for note tweet in quoted tweet
                                            if 'note_tweet' in quoted_result:
                                                try:
                                                    note_text = quoted_result['note_tweet']['note_tweet_results']['result']['text']
                                                    if note_text:
                                                        quoted_text = note_text
                                                except (KeyError, TypeError):
                                                    pass
                                            
                                            quoted_author = quoted_result.get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {}).get('screen_name', 'unknown')
                                            full_text += f"\n\n[引用 @{quoted_author}]: {quoted_text}"
                                    except Exception as e:
                                        # logger.warning(f"Failed to extract quoted tweet: {e}")
                                        pass

                                tweets.append({
                                    'id': legacy['id_str'],
                                    'text': full_text,
                                    'created_at': legacy['created_at'],
                                    'author_name': user_legacy.get('name'),
                                    'author_handle': user_legacy.get('screen_name')
                                })
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            
        return tweets
