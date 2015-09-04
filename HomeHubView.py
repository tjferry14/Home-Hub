# coding: utf-8
import console, dialogs, feedparser, location, requests, twitter, ui

twitter_err = "You don't have any Twitter accounts (or haven't given permission to access them)."
weather_fmt = 'http://api.openweathermap.org/data/2.5/{}?lat={}&lon={}&mode=json&units=imperial'

with open('feed.txt') as f:
    for line in f.readlines():
        news_url = line

with open('modes.txt') as mode:
    for line in mode.readlines():
        twitter_mode = line

def make_button_item(image_name, action):
    button_item = ui.ButtonItem()
    button_item.image = ui.Image.named(image_name)
    button_item.action = action
    return button_item

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
        settings_but = make_button_item('iob:settings_32', self.settings_action)
        self.right_button_items = [settings_but]

    def did_load(self):
        self['rss_view'].delegate = self
        self.update_all()

    def update_all(self):
        self.update_news()
        if twitter_mode:
          self.update_tweets()
        else:
          pass
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
        webview = ui.WebView(name = selected['title'] if isinstance(selected, dict) else selected)
        webview.load_url(selected['link'] if isinstance(selected, dict) else selected)
        webview.present()
        
    def settings_action(self, sender):
        global news_url, twitter_mode
        Dialog_List =[{'type':'text','title':'RSS Feed','key':'feed', 'value': news_url},
{'type': 'switch', 'title': 'Twitter Feed', 'key':'twitter', 'value': twitter_mode},]
        settings = dialogs.form_dialog(title='Settings', fields=Dialog_List)
        console.show_activity()
        news_url = settings['feed']
        twitter_mode = str(settings['twitter'])
        self.update_news()
        console.hide_activity()
        with open('feed.txt', 'w') as f:  
            f.write(news_url)
        with open('modes.txt', 'w') as mode:
            mode.write(twitter_mode)

ui.load_view().present()
