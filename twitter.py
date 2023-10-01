try:
    import requests
    import argparse
    from fake_headers import Headers
    import json
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex)

AUTHORIZATION_KEY = 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'


class Twitter:

    @staticmethod
    def find_x_guest_token():
        try:
            headers = {
                'authorization': AUTHORIZATION_KEY,
            }
            response = requests.post(
                'https://api.twitter.com/1.1/guest/activate.json', headers=headers)
            return response.json()['guest_token']
        except Exception as ex:
            print("Error at find_x_guest_token: {}".format(ex))

    @staticmethod
    def make_http_request(URL, headers, params):
        try:
            response = requests.get(URL, headers=headers, params=params)
            if response and response.status_code == 200:
                return response.json()
        except Exception as ex:
            print("Error at make_http_request: {}".format(ex))

    @staticmethod
    def build_headers(x_guest_token, authorization_key, username):
        headers = {
          'authority': 'twitter.com',
          'accept': '*/*',
          'accept-language': 'en-US,en;q=0.9',
          'authorization': authorization_key,
          'content-type': 'application/json',
          'referer': f'https://twitter.com/{username}',
          'sec-ch-ua': '"Microsoft Edge";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
          'sec-ch-ua-mobile': '?1',
          'sec-ch-ua-platform': '"Android"',
          'sec-fetch-dest': 'empty',
          'sec-fetch-mode': 'cors',
          'sec-fetch-site': 'same-origin',
          'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36 Edg/117.0.2045.43',
          'x-client-transaction-id': 'Tpc50EvkhGl2dFlKgLRcZjIFdx1Uud7VqfulUTrUcdW6c+G/4kSNseH2g2p8LiqTIGFGhE6timLmbth+LVyIuB5wTcdoTw',
          'x-csrf-token': '7205feef3657d10f5b167cc42900ee3a',
          'x-guest-token': x_guest_token,
          'x-twitter-active-user': 'yes',
          'x-twitter-client-language': 'en',
        }
        return headers

    @staticmethod
    def build_params(username: str):
      return {
        'variables': '{"screen_name":"' + username + '","withSafetyModeUserFields":true}',
        'features': '{"hidden_profile_likes_enabled":true,"hidden_profile_subscriptions_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":true,"subscriptions_verification_info_is_identity_verified_enabled":true,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}',
        'fieldToggles': '{"withAuxiliaryUserLabels":false}',
      }

    @staticmethod
    def scrap(username):
        try:
            # generating URL according to the username
            guest_token = Twitter.find_x_guest_token()
            headers = Twitter.build_headers(guest_token, AUTHORIZATION_KEY, username)
            params = Twitter.build_params(username)
            response = Twitter.make_http_request(
                "https://twitter.com/i/api/graphql/G3KGOASz96M-Qu0nwmGXNg/UserByScreenName".format(username),
                headers=headers, params=params)
            if response:
              return json.dumps(response.get("data"))
            else:
              print("Failed to make Request!")
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="username to search")

    args = parser.parse_args()
    print(Twitter.scrap(args.username))

# last updated - 1st October, 2023
