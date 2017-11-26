import urllib.request
from bs4 import BeautifulSoup, Comment #https://www.crummy.com/software/BeautifulSoup/
import re
import csv
# takes a team abbreviation and a dictionary and returns the most up to date abbreviation for that franchise
def check_abbr (abbreviation, dictionary):
	if abbreviation not in dictionary: #if a new abbreviation is used, navigate to franchise page to get most recent abbreviation
		url = 'https://www.basketball-reference.com/teams/' + abbreviation
		page = urllib.request.urlopen(url)
		s = BeautifulSoup(page, 'html.parser')
		test = s.find('meta', {'http-equiv':'refresh'})
		if test is not None: #handle possible redirect when going to franchise page
			ref = test.get('content')[6:]
			url = 'https://www.basketball-reference.com' + ref
			page = urllib.request.urlopen(url)
			s = BeautifulSoup(page, 'html.parser')
		table = s.find('table', class_='stats_table')
		tm_id = table.tbody.tr.th.a.get('href')[7:10]
		dictionary[abbreviation] = tm_id #add abbreviation to dictionary for future use
	return dictionary[abbreviation]
start_year = 2012 #seasons starting in those years
end_year = 2016
done = 0
base_url = 'https://www.basketball-reference.com'
abbr_dict = {}
total_wins = {} #not actually used
win_percent = {}
first_rd_ws = {}
top_five_ws = {}
lottery_ws = {}
non_lottery_ws = {}
second_rd_ws = {}
undrafted_ws = {}
domestic_ws = {}
international_ws = {}
overseas_ws = {}
drafted_ws = {}
traded_ws = {}
signed_ws = {}
no_college_ws = {}
high_school_ws = {}
freshman_ws = {}
soph_ws = {}
junior_ws = {}
senior_ws = {}
total_ws = {}
# get team winning percentages
url = "https://www.basketball-reference.com/teams/"
teams_page = urllib.request.urlopen(url)
team_soup = BeautifulSoup(teams_page, 'html.parser')
team_table = team_soup.find('table', id = 'teams_active')
teams = team_table.tbody.find_all('a')
for team in teams:
	team_abbr = check_abbr(team.get('href')[7:10], abbr_dict)
	team_url = base_url + team.get('href')
	team_page = urllib.request.urlopen(team_url)
	soup = BeautifulSoup(team_page, 'html.parser')
	table = soup.find('table')
	rows = table.tbody.find_all('tr')
	wins = 0
	losses = 0
	for row in rows:
		season = int(row.th.a.string[:4])
		if start_year <= season <= end_year:
			wins = wins + int(row.find('td', {'data-stat':'wins'}).string)
			losses = losses + int(row.find('td', {'data-stat':'losses'}).string)
	total_wins[team_abbr] = wins
	win_percent[team_abbr] = wins / (wins + losses)
	# initialize dictionaries for keeping track of win share stats
	first_rd_ws[team_abbr] = 0
	top_five_ws[team_abbr] = 0
	lottery_ws[team_abbr] = 0
	non_lottery_ws[team_abbr] = 0
	second_rd_ws[team_abbr] = 0
	undrafted_ws[team_abbr] = 0
	domestic_ws[team_abbr] = 0
	international_ws[team_abbr] = 0
	overseas_ws[team_abbr] = 0
	drafted_ws[team_abbr] = 0
	traded_ws[team_abbr] = 0
	signed_ws[team_abbr] = 0
	high_school_ws[team_abbr] = 0
	no_college_ws[team_abbr] = 0
	freshman_ws[team_abbr] = 0
	soph_ws[team_abbr] = 0
	junior_ws[team_abbr] = 0
	senior_ws[team_abbr] = 0
	#print(team_abbr)
# url is for player finder, which returns a list of all players who played within the year range
url = "https://www.basketball-reference.com/play-index/psl_finder.cgi?request=1&match=combined&per_minute_base=36&per_poss_base=100&type=advanced&season_start=1&season_end=-1&lg_id=NBA&age_min=0&age_max=99&is_playoffs=N&height_min=0&height_max=99&year_min=" + str(start_year+1) + "&year_max=" + str(end_year+1) + "&birth_country_is=Y&as_comp=gt&as_val=0&pos_is_g=Y&pos_is_gf=Y&pos_is_f=Y&pos_is_fg=Y&pos_is_fc=Y&pos_is_c=Y&pos_is_cf=Y&order_by=ws"
while done == 0:
	page = urllib.request.urlopen(url)
	soup = BeautifulSoup(page, 'html.parser')
	p = (soup.find('div', class_='p402_premium')).p #used in finding next page
	players = soup.find_all('td', {'data-stat':'player'}) 
	for player in players:
		player_url = base_url + player.a.get('href')
		#print(player.a.get('href'))
		player_page = urllib.request.urlopen(player_url)
		player_soup = BeautifulSoup(player_page, 'html.parser')
		pick_overall = 'Undrafted'
		team_drafted = ''
		draft_year = ''
		draft_round = ''
		teams_ws = {} # keep track of winshares per team played for
		teams_acquisition = {} # keep track of how player was acquired by each team played for
		stats_table = player_soup.find('table', id='per_game')
		col_div = player_soup.find('div', id='all_all_college_stats')
		advanced_div = player_soup.find('div', id='all_advanced')
		transaction_div = player_soup.find('div', id='all_transactions')
		info = player_soup.find('div', id='meta')
		lines = info.find_all('p')
		# find basic info such as draft year, draft round, country of origin from top of page
		for line in lines:
			if line.strong is not None and line.strong.string is not None:
				#get draft info, if any
				if line.strong.string == '\n  Draft:\n  ':
					#print(line.getText())
					reg = re.compile('\d*\d\D\D overall')
					s = reg.search(line.getText())
					pick_overall = int(line.getText()[s.start():s.end()-10])
					reg = re.compile('\d\d\d\d')
					s = reg.search(line.getText())
					draft_year = int(line.getText()[s.start():s.end()])
					reg = re.compile('\d*\d\D\D round')
					s = reg.search(line.getText())
					draft_round = int(line.getText()[s.start():s.end()-8])
				#get country origin info
				if line.strong.string == 'Born:':
					href = (line.find('span',{'itemprop':'birthPlace'})).a.get('href')
					reg = re.compile('country=US')
					if reg.search(href) is not None:
						origin = "USA"
					else:
						origin = "International"
		# get number of years of college, if any, by counting rows in college stats table
		if(col_div is not None):
			col_div_comment = col_div.find(text=lambda text:isinstance(text, Comment))
			soup = BeautifulSoup(col_div_comment, 'html.parser')
			rows = soup.tbody.find_all('tr')
			college_years = len(rows)
		else:
			college_years = 0
		# get win share statistics from advanced stats table
		if(advanced_div is not None):
			advanced_comment = advanced_div.find(text=lambda text:isinstance(text, Comment))
			soup = BeautifulSoup(advanced_comment, 'html.parser')
			rows = soup.tbody.find_all('tr')
			for row in rows:
				year = int(row.th.a.string[:4])
				ws = float(row.find('td', {'data-stat':'ws'}).string)
				team_id_div = row.find('td', {'data-stat':'team_id'})
				if(team_id_div.a is not None and 2012 <= year <= 2016):
					team_id = check_abbr(team_id_div.a.string, abbr_dict)
					teams_acquisition[team_id] = '' #transactions may have missing info
					if team_id in teams_ws.keys():
						teams_ws[team_id] += ws
					else:
						teams_ws[team_id] = ws
		# find out how player was acquired by teams played for using the transaction section
		if(transaction_div is not None):
			transaction_comment = transaction_div.find(text=lambda text:isinstance(text, Comment))
			soup = BeautifulSoup(transaction_comment, 'html.parser')
			transactions = soup.find_all('p', class_='transaction')
			prev_team = ""
			prev_year = 0
			prev_type = ""
			for trans in transactions:
				team_id = trans.select('a[data-attr-to]')
				if len(team_id) > 0:
					team_to = check_abbr(team_id[0].get('data-attr-to'), abbr_dict)
					text = trans.getText()
					trans_type = ((re.findall(r'\b(\w+d)\b',text))[0])
					trans_type = "%s%s" % (trans_type[0].upper(),trans_type[1:])
					year = int(((re.findall('\d\d\d\d',text))[0]))
					if year == prev_year and prev_type == "Drafted" and (trans_type == "Traded" or trans_type == "Sold"): #handles draft day deals (and Wiggins deal) (sold means traded for cash)
						teams_acquisition[team_to] = "Drafted"
						team_drafted = team_to
					elif team_to != prev_team or trans_type == "Drafted": #ignores resigning and the pick being traded before the draft
						teams_acquisition[team_to] = trans_type
						if trans_type == 'Drafted':
							team_drafted = team_to
					prev_team = team_to
					prev_year = year
					prev_type = trans_type
				else: #handles situations where a player was waived but it doesn't say how he was originally acquired
					team_id = trans.select('a[data-attr-from]')
					if len(team_id) > 0:
						team_from = check_abbr(team_id[0].get('data-attr-from'), abbr_dict)
						if team_from not in teams_acquisition.keys() or teams_acquisition[team_from] == "": #if a player was waived but there is no acquistion info, mark as a signing
							teams_acquisition[team_from] = "Signed"
							prev_team = team_from
							prev_type = "Signed"
		# printing for testing purposes
		#print('Pick %d' %pick_overall)
		#for key in teams_ws:
		#	print("%s: %f, %s" %(key, teams_ws[key], teams_acquisition[key]))
		# assign win share statistics to proper categories
		for key in teams_ws:
			if pick_overall == "Undrafted":
				undrafted_ws[key] += teams_ws[key]
			elif draft_round == 1:
				first_rd_ws[key] += teams_ws[key]
				if 0 < pick_overall <= 5:
					top_five_ws[key] += teams_ws[key]
				elif 5 < pick_overall <= 14:
					lottery_ws[key] += teams_ws[key]
				elif 14 < pick_overall <= 30:
					non_lottery_ws[key] += teams_ws[key]
			elif draft_round == 2:
				second_rd_ws[key] += teams_ws[key]
			if origin == "USA":
				domestic_ws[key] += teams_ws[key]
			elif origin == "International":
				international_ws[key] += teams_ws[key]
			if teams_acquisition[key] == "Drafted":
				drafted_ws[key] += teams_ws[key]
			elif teams_acquisition[key] == "Traded":
				traded_ws[key] += teams_ws[key]
			elif teams_acquisition[key] == "Signed" or teams_acquisition[key] == "Claimed":
				signed_ws[key] += teams_ws[key]
			if college_years == 0:
				no_college_ws[key] += teams_ws[key]
				if origin == "International": #account for true international prospects (no college in the US)
					overseas_ws[key] += teams_ws[key]
				elif origin == "USA": #account for players who declared right out of HS (also includes cases like Brandon Jennings)
					high_school_ws[key] += teams_ws[key]
			elif college_years == 1:
				freshman_ws[key] += teams_ws[key]
			elif college_years == 2:
				soph_ws[key] += teams_ws[key]
			elif college_years == 3:
				junior_ws[key] += teams_ws[key]
			elif college_years == 4:
				senior_ws[key] += teams_ws[key]
	# check if there is a next page to go to, otherwise it is done
	done = 1
	buttons = p.find_all('a')
	for button in buttons:
		if button.string == "Next page":
			url = base_url + button.get('href')
			done = 0
# output results to csv file
with open('ws_stats.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Team', 'Winning Percentage', 'Total Win Shares', 'First Round Win Shares', 'Top 5 Win Shares', '5-14 Win Shares', '15-30 Win Shares', 'Second Round Win Shares', 'Undrafed Win Shares', 
    				'Domestic Win Shares', 'International Win Shares', 'Overseas Prospect Win Shares', 'High School Win Shares', 'No College Win Shares', '1 College Year Win Shares',
    				'2 College Years Win Shares', '3 College Years Win Shares', '4 College Years Win Shares',
    				'Drafted Win Shares', 'Traded Win Shares', 'Signed Win Shares'])
    for key in win_percent:
    	total_ws[key] = domestic_ws[key] + international_ws[key] #calculate total win shares for each team (any category can be used)
    	writer.writerow([key, win_percent[key], total_ws[key], first_rd_ws[key], top_five_ws[key], lottery_ws[key], non_lottery_ws[key], second_rd_ws[key], undrafted_ws[key], 
    					domestic_ws[key], international_ws[key], overseas_ws[key], high_school_ws[key], no_college_ws[key], freshman_ws[key], 
    					soph_ws[key], junior_ws[key], senior_ws[key],
    					drafted_ws[key], traded_ws[key], signed_ws[key]])