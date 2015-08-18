# coding: utf-8
import urllib2, json, location
import ui, console, time
import twitter, urllib, feedparser

v = ui.load_view()
timeline = v['timeline']

feed = feedparser.parse('http://rss.cnn.com/rss/cnn_topstories.rss')
entries = feed['entries']

def load_twitter_data():
	all_accounts = twitter.get_all_accounts()
	if len(all_accounts) >= 1:
		account = all_accounts[0]
		get_tweets(account)
	else:
		print 'You don\'t have any Twitter accounts (or haven\'t given permission to access them).'

def get_tweets(account):
	tweets = twitter.get_home_timeline(account)
	console.show_activity('Getting The Latest Data')
	tlist = []
	time.sleep(1)
	for t in tweets:
		tlist.append(t.get('text'))
		tlist.append(t.get('user').get('screen_name'))
	timeline.data_source = ui.ListDataSource(items=tlist)
	timeline.data_source.number_of_lines = 3
	timeline.reload()
	console.hide_activity()

def place():
	address_dict = location.get_location()
	location.start_updates()
	
	location.stop_updates()
	latitude = address_dict['latitude']
	longitude = address_dict['longitude']
	api(latitude, longitude)

def api(latitude, longitude):
	url = 'http://api.openweathermap.org/data/2.5/forecast/daily?lat={0}&lon={1}&mode=json&units=imperial' .format (latitude, longitude)
	api = urllib2.urlopen(url)
	forecastapi = json.load(api)
	url = 'http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&mode=json&units=imperial' .format (latitude, longitude)
	api = urllib2.urlopen(url)
	weatherapi = json.load(api)
	forecast(weatherapi, forecastapi)
	
def forecast(weatherapi, forecastapi):
	v['today_high_temp'].text = str(round(weatherapi['main']['temp_max'], 0)) + '°'
	v['today_low_temp'].text = str(round(weatherapi['main']['temp_min'], 0)) + '°'
	v['current_temp_temp'].text = str(round(weatherapi['main']['temp'], 0)) + '°'
	
def load_articles():
	feed_entries = []
	for entry in entries:
		feed_entries.append(entry['title'])
	
	v['rss_view'].data_source = ui.ListDataSource(items=feed_entries)

'''	
class TheDelegate(object):
	def tableview_did_select(self, tableview, section, row):
			print 'Print article'
			
v['rss_view'].delegate = TheDelegate()
'''

place()
load_twitter_data()
load_articles()

v.present('full_screen')
