try:
    import argparse
    import requests
    import json
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex)


class Medium:

    @staticmethod
    def build_payload(username):
        query = ''
        with open('medium_graphql_query.graphql', 'r', encoding='utf-8') as file:
            query = file.read()
        json_data = [
            {
                'operationName': 'UserProfileQuery',
                'variables': {
                    'includeDistributedResponses': True,
                    'id': None,
                    'username': '@{}'.format(username),
                    'homepagePostsLimit': 1,
                },
                'query': query
            },
        ]
        return json_data

    @staticmethod
    def make_request(URL, json_data):
        try:
            response = requests.post(URL, json=json_data)
            if response.status_code == 200:
                return response.json()
        except Exception as ex:
            print('Error at Make Request: {}'.format(ex))

    @staticmethod
    def scrap(username):
        """scrap medium's profile"""
        try:
            URL = "https://medium.com/_/graphql"
            payload = Medium.build_payload(username)
            response = Medium.make_request(URL, payload)
            if response:
                return json.dumps(response)
            else:
                print("Failed to make response!")
        except Exception as ex:
            return {"error": ex}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="username to search")

    args = parser.parse_args()
    print(Medium.scrap(args.username))

# last modified on : 24th October, 2022
