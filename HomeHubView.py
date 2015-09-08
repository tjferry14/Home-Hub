# coding: utf-8
import console, dialogs, feedparser, location, twitter, ui
import config
from requests import get

console.show_activity('Loading')

twitter_err = "You don't have any Twitter accounts (or haven't given permission to access them)."
weather_fmt = 'http://api.openweathermap.org/data/2.5/{}?lat={}&lon={}&mode=json&units=imperial'

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
        if config.twitter_mode:
          self.update_tweets()
        else:
          self['timeline'].hidden = True
          self['label1'].hidden = True
        self.update_weather()

    def update_news(self):
        self['rss_view'].data_source.items = [entry for entry in feedparser.parse(config.feed_1)['entries']] + [entry for entry in feedparser.parse(config.feed_2)['entries']]

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
        weather_dict = get(weather_fmt.format('weather', lat, lon)).json()
        if 'main' in weather_dict:
            for key in 'temp_max temp_min temp'.split():
                self[key].text = '{}°'.format(round(weather_dict['main'][key]))

    def tableview_did_select(self, tableview, section, row):
        selected = tableview.data_source.items[row]
        webview = ui.WebView(name = selected['title'] if isinstance(selected, dict) else selected)
        webview.load_url(selected['link'] if isinstance(selected, dict) else selected)
        webview.present()
        
    def updatepy(self, feed1, feed2, mode):
        s = open("config.py").read()
        update_feed1 = s.replace(config.feed_1, feed1)
        update_feed2 = s.replace(config.feed_2, feed2)
        update_mode = s.replace(str(config.twitter_mode), str(mode))
        f = open("config.py", 'w')
        f.write(update_feed)
        f.seek(0)
        f.write(update_mode)
        f.close()
        s = open("config.py").read()
        if 'Truee' in s: # weird bug found
          s = s.replace('Truee', 'True')
          f = open("config.py", 'w')
          f.write(s)
        
    def settings_action(self, sender):
        Dialog_List =[{'type':'text','title':'RSS Feed 1','key':'feed1', 'value': config.feed_1},
        {'type':'text','title':'RSS Feed 2','key':'feed2', 'value': config.feed_2},
{'type': 'switch', 'title': 'Twitter Feed', 'key':'twitter', 'value': config.twitter_mode},]
        settings = dialogs.form_dialog(title='Settings', fields=Dialog_List)
        console.show_activity()
        if settings == None:
          print 'Cancelled'
        else:
          self.updatepy(settings['feed1'], settings['feed2'], settings['twitter'])
        self.update_news()
        console.hide_activity()

ui.load_view().present()
console.hide_activity()
