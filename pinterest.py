try:
    import argparse
    from fake_headers import Headers
    import requests
    import json
except ModuleNotFoundError:
    print("Please download dependencies from requirement.txt")
except Exception as ex:
    print(ex)

class Pinterest:
    '''This class scraps pinterest and returns a dict containing all user data'''
    @staticmethod
    def _generate_url(username):
      return "https://pinterest.com/resource/UserResource/get/?source_url=%25{}%2F&data=%7B%22options%22%3A%7B%22field_set_key%22%3A%22profile%22%2C%22username%22%3A%22{}%22%2C%22is_mobile_fork%22%3Atrue%7D%2C%22context%22%3A%7B%7D%7D&_=1640428319046".format(username, username)


    @staticmethod
    def _make_request(url):
      headers = Headers().generate()
      response = requests.get(url,headers=headers)
      return response

    @staticmethod
    def scrap(username):
        try:

            try:
                url = Pinterest._generate_url(username)
                response = Pinterest._make_request(url)
                if response.status_code == 200:
                  response = response.json()
                else:
                  print("Failed to get Data!")
                  exit()
            except Exception as ex:
                print("Error",ex)
                exit()



            json_data = response

            data = json_data['resource_response']['data']
            id = data['id']
            is_verified_merchant = data['is_verified_merchant']
            full_name = data['full_name']
            impressum_url = data['impressum_url']
            pin_count = data['pin_count']
            website_url = data['website_url']
            profile_image = data['image_xlarge_url']
            bio = data['about']
            board_count = data['board_count']
            is_indexed = data['indexed']
            follower = data['follower_count']
            following = data['following_count']
            country = data['country']
            location = data['location']
            profile_views = data['profile_views']
            interest_following_count = data['interest_following_count']
            has_published_pins = data['has_published_pins']
            video_pin_count = data['video_pin_count']
            profile_data = {
                "id" : id,
                'full_name' : full_name,
                'profile_image' : profile_image,
                'followers' : follower,
                'followings' : following,
                'bio' : bio,
                'country' : country,
                'impressum_url' : impressum_url,
                'website': website_url,
                'board_count' : board_count,
                "is_indexed" : is_indexed,
                'location' : location,
                'pin_count' : pin_count,
                'is_verified' : is_verified_merchant,
                "profile_view" : profile_views,
                "interest_following_count" : interest_following_count,
                "has_published_pins" : has_published_pins,
                "video_pin_count" : video_pin_count
            }

            return json.dumps(profile_data)
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("username",help="username to search")

    args = parser.parse_args()
    print(Pinterest.scrap(args.username))

#last updated - 25th December,2021