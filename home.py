# coding: utf-8
import urllib2, json, location
import ui, console, time
import twitter, urllib, feedparser

v = ui.load_view()
timeline = v['timeline']
rss_view = v['rss_view']

all_accounts = twitter.get_all_accounts()
if len(all_accounts) >= 1:
	account = all_accounts[0]
else:
	print 'You don\'t have any Twitter accounts (or haven\'t given permission to access them).'
	
feed = feedparser.parse('http://rss.cnn.com/rss/cnn_topstories.rss')
entries = feed['entries']

def get_tweets(sender):
	global tlist
	tlist = []
	tweets = twitter.get_home_timeline(account)
	console.show_activity('Refreshing')
	time.sleep(1)
	for t in tweets:
		tlist.append(t.get('text'))
	timeline.data_source = ui.ListDataSource(items=tlist)
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
	feed_entries = []
	for entry in entries:
		feed_entries.append(entry['title'])

	v['rss_view'].data_source = ui.ListDataSource(items=feed_entries)

sender = 0
place()
get_tweets(sender)
v.present('full_screen')
