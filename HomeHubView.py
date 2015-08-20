# coding: utf-8
import console, feedparser, location, requests, twitter, ui

news_url = 'http://rss.cnn.com/rss/cnn_topstories.rss'
twitter_err = "You don't have any Twitter accounts (or haven't given permission to access them)."
weather_fmt = 'http://api.openweathermap.org/data/2.5/{}?lat={}&lon={}&mode=json&units=imperial'

def get_first_twitter_account():
    try:
        return twitter.get_all_accounts()[0]
    except IndexError:
        console.hud_alert(twitter_err, 'error', 3)
        return None

def get_lat_lon():
    location.start_updates()
    loc_dict = location.get_location()
    location.stop_updates()
    return (loc_dict['latitude'], loc_dict['longitude'])

class HomeHubView(ui.View):
    def __init__(self):
        self.twitter_account = get_first_twitter_account()

    def did_load(self):
        self['rss_view'].delegate = self  # these could get...
        self['timeline'].delegate = self  # moved into the .pyui
        self.update_all()

    def update_all(self):
        self.update_news()
        self.update_tweets()
        self.update_weather()

    def update_news(self):
        self['rss_view'].data_source.items = [entry for entry in feedparser.parse(news_url)['entries']]

    def update_tweets(self):
        if not self.twitter_account:
            return
        fmt = '{text} | {user[screen_name]}'
        try:
            self['timeline'].data_source.items = [fmt.format(**tweet) for tweet
                in twitter.get_home_timeline(self.twitter_account)]
        except TypeError:  # too many Twitter API calls
            pass

    def update_weather(self):
        lat, lon = get_lat_lon()
        weather_dict = requests.get(weather_fmt.format('weather', lat, lon)).json()
        if 'main' in weather_dict:
            for key in 'temp_max temp_min temp'.split():
                self[key].text = '{}°'.format(round(weather_dict['main'][key]))

    def tableview_did_select(self, tableview, section, row):
        selected = tableview.data_source.items[row]
        console.hud_alert(selected['title'] if isinstance(selected, dict) else selected)

ui.load_view().present()
