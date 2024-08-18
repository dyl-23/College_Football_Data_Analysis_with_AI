"""
Overview: The following code utilizes CollegeFootballData's API to retrieve player and team data. HTTP
get requests are utilized to retrieve data from the requested url endpoint, along with an authentication token
and parameters that are given to filter the data requested. A football field that contains text of the data is then
created and saved through the contributions of numerous functions that are assigned to specific data filtering
tasks.
"""
"""
The following code refers to the libraries imported into the python file. For any user know of all
necessary library imports, a requirements.txt file was created. Matplotlib is imported to allow for the creation
of a football field with annotations consisting of the top 5 players based on usage rate along with their predicted
points added plus other data analytics. Agg is a non interactive backend that enables the writing of files
such as png. An alias is made for the pyplot module as plt. This is within the same matplotlib library. os is imported as
well to allow the os to access env variables(from dotenv import load_dotenv). Requests is imported for the purpose
of making api requests and concurrent features imports ThreadPoolExecutor and as_completed for concurrent api requests.
This promotes more efficent run times.
"""
import matplotlib
matplotlib.use('Agg')
import os
from dotenv import load_dotenv
import requests
import matplotlib.pyplot as plt
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

"""
The purpose of this function is to make http requests to the api in order to pull the requested data. The requested data is specified through endpoints
and parameters that pull the data wanted. If the api request is succesful, a 200 code is received. Then the JSON response is a list of dictionaries
consisting of data. If the request is unsuccessful, an error is returned along with details regarding the error.
"""
def request_the_api(endpoint, headers, params):
    api_url= 'https://api.collegefootballdata.com/'
    requested_url= api_url + endpoint
    print(f"API Request URL: {requested_url}")
    the_response= requests.get(requested_url, headers=headers, params=params)
    if the_response.status_code==200:
        return the_response.json()
    else:
        print(f"Error: {the_response.status_code} - {the_response.text}")
        return None
"""
The following victoryformation function will utilize matplotlib's library to open a football field jpg and edit it into becoming an edited png image. 
First the original football image is opened and then converted into a 12 by 8 figure. Then the player count and spacing(to create y coords for each player's data)
is figured out. Next for every player in the players_data list that consists of the top 5 players in usage rate, each player has data pulled from their dictionary in players_data. 
A marker for the player is placed following the pulling of some data. Then for each player a main_info text line consisting of the player name, usage rate and
ppa is made. A text piece is next made called ydtd_info, which stores the player stat category and stats for that player(yds and tds only). The main_info and ydtd_info
text pieces are then stored near the player's respective marker and are spaced along the x axis of the figure. After each player has been looked at in
players_data, a team annotation is created from team_info. The team_annotation is then placed in the top right corner of the figure to display the team name,
team record and conference of the team. The figure then sets limits and is saved as a png image.
"""
def victoryformation(players_data, team_info):
    plt.figure(figsize=(12,8))
    field_img= Image.open('static/football.jpg')
    plt.imshow(field_img)

    player_num= len(players_data)
    space= field_img.height/(player_num+1)

    for i, player in enumerate(players_data):
        usage_rate= player.get('usage', {}).get('overall', 0.0)
        ppa= player.get('averagePPA', 0.0)
        y_coord= field_img.height - (i+1) * space
        plt.scatter(100, y_coord, color='red', s=50, marker='o')
        
        main_info= f"{player.get('name', 'Unknown')}\nUsage Rate: {usage_rate:.4f}\nAvg. PPA: {ppa:.4f}"
        player_position= player.get('position', 'Unknown')
        player_category= obtain_playerST_category(player_position)
        ydtd_info= generate_stats_info(player, player_category)

        plt.text(125, y_coord, main_info, fontsize=10, color='black', ha='left', va='center', fontweight='bold')
        plt.text(350, y_coord, ydtd_info, fontsize=10, color='black',  ha='left', va='center', fontweight='bold')
    team_annotation= f"Team: {team_info.get('team', 'Unknown')}\nConference: {team_info.get('conference', 'Unknown')}\nRecord: {team_info.get('total', {}).get('wins', 'Unknown')}-{team_info.get('total', {}).get('losses', 'Unknown')}-{team_info.get('total', {}).get('ties', 'Unknown')}"
    plt.text(field_img.width - 10, field_img.height-10, team_annotation, fontsize=10, color='black', ha='right', va='top', fontweight='bold')
    plt.xlim(0, field_img.width)
    plt.ylim(0, field_img.height)
    plt.savefig('static/field_plot.png')
    plt.close()
"""
The purpose of generate stats is to obtain the yds and tds from a specific player. In this process the player category, yds and stats are
seperated line by line for the detailing of the football field. Throughout the duration of this process it is also ensured that the data filtering done
in gather_ppa_and_stats was correct by double checking if there are in fact stats, if the player category filtering was done and if the player names
match. A string consisting of a player category, statype(yds) plus a stat (# of yards) and statype(tds) plus a stat (# of tds).
"""
def generate_stats_info(player, player_category):
    if 'stats' in player:
        stats_text= "\n".join([f"{stat['statType']}: {stat['stat']}"for stat in player['stats'] if
                               stat['statType'] in ['YDS', 'TD'] and
                               stat['category'] == player_category and
                               stat['player']== player['name']])
        return f"{player_category.capitalize()}\n{stats_text}"
    else:
        return f"{player_category.capitalize()}\nNo stats available"
"""
The following function below will take in headers, a year and a team to return a sorted list of the top 5 players on a team by usage rate. In the function
a request is made to the api with the usage rate endpoints and parameters. If the request is unsuccesful an error should be returned. If the request is
successful, a list of dictionaries of each player from a certain season is made as usage_data. Usage_data is then filtered through to make players_from_team,
which just makes the list of dictionaries consist of all players from a certain team in a certain year. If no players are found on the team, none is returned.
Next the top 5 players based on usage rate are stored as a list of dictionaires in sorted_players and then returned.
"""
def get_top5_usage_players(headers, year, team):
    endpoint_usage= 'player/usage'
    parameters_usage= {'year': year}
    usage_data= request_the_api(endpoint_usage, headers=headers, params=parameters_usage)
    if not usage_data:
        return None
    
    players_from_team= [player for player in usage_data if player.get('team') == team]
    if not players_from_team:
        print(f"No players found on team {team} in {year}")
        return None
    sorted_players= sorted(players_from_team, key=lambda x: x.get('usage', {}).get('overall', 0.0), reverse=True)[:5]
    return sorted_players
"""
The function concurrent_assigning_of_player_data has headers, year, team and sorted_players as parameters. This function also contains the nested function
gather_ppa_and_stats. The function's purpose is to update the dictionaries of each player in the sorted_players list with a ppa value and a stats category.
Initially the endpoints are set up for the ppa and stats api requests. Then comes the usage of threads to complete tasks concurrently. Through searching the
web I learned about threads and was able to use them in this project. Threads are the smallest unti of execution within a process. A collection of threads
ready to be assigned to a task is called a thread pool. A ThreadPoolExecutor allows for each task to be completed by assigning tasks to each thread in the
thread pool. The ThreadPoolExecutor itself manages the number of threads and provides ways to handle the lifecycle of these threads for the user. In this
code below ThreadPoolExecutor is utilized as the executor to enforce the concurrent execution of tasks by threads. Then futures= {executor.submit(gather_ppa_and_stats, player): player for player in sorted_players}
submits the gather_ppa_and_stats function to the thread pool for each player. The futures dictionary then stores each key as a future object and the value
of each object is the corresponding player. Then as each future completes, it is returned in as_completed(futures). The player_name and results are obtained
from the result of that future or thread execution of a given player's fetch_ppa_and_stats. Then we look through each player in sorted players, to see if their
name matches the returned player name from the future result. Then the player's dictionary is updated with the future's returned results(dictionary of stats).
The gather_ppa_and_stats function is what makes api requests for the ppa and stats for each player. The data collected is placed in that player's results dictionary and both the player_name and
results dictionary are returned. The understanding gather_ppa_and_stats function is the simpler part of this function process.
"""
def concurrent_assigning_of_player_data(headers, year, team, sorted_players):
    endpoint_ppa= 'ppa/players/season'
    endpoint_stats= 'stats/player/season'

    def gather_ppa_and_stats(player):
        player_name= player.get('name')
        results={}

        parameters_ppa={'year': year, 'team': team, 'player': player_name}
        ppa_data= request_the_api(endpoint_ppa, headers=headers, params=parameters_ppa)
        if ppa_data:
            player_ppa= next((item for item in ppa_data if item.get('name') == player_name), {})
            results['averagePPA']= player_ppa.get('averagePPA', {}).get('all', 0.0)
        else:
            print(f"Failed to obtain predicted points added for {player.get('name', 'Unknown')}")

        player_category= obtain_playerST_category(player['position'])
        parameters_stats= {'year': year, 'team': player['team'], 'category': player_category}
        player_stats= request_the_api(endpoint_stats, headers=headers, params=parameters_stats)
        if player_stats:
            individual_player_stats= [item for item in player_stats if item.get('player') == player_name]
            results['stats']= individual_player_stats
        else:
            print(f"Failed to obtain stats for {player.get('name', 'Unknown')}")
        return player_name, results
    
    with ThreadPoolExecutor() as executor:
        futures= {executor.submit(gather_ppa_and_stats, player): player for player in sorted_players}
        for future in as_completed(futures):
            player_name, results= future.result()
            for player in sorted_players:
                if player['name'] == player_name:
                    player.update(results)
                    break
"""
The following code below refers to the get_team_data function that builds the detailed football field image of the top 5 players sorted by usage rate on a given team
in a given year. The function also returns a sorted_players list and team_info dictionary. First the function loads the CFBD api key from the environment variable.
The headers are then set for the api request utilizing the authorization the api key provides(this only happens if an api key existed for CFBD). Next the sorted_players 
list is made from the get_top5_usage_players function. If no such players exist, none is returned. Following the guarantee that the sorted_player list exists,
the concurrent_assigning_of_player_data function is called to add new data such as ppa and stats to each players dictionary in sorted_players. Then 
the request is made for the team records data utilzing the unique records endpoint and parameters. Given that records_data was able to be pulled from
the api, then victoryformation is called to detail and customize the field according to the data analytics that were retrieved from CFBD. Sorted_players
is then returned along with records_data[0] to allow for the data in those data structures to be passed to app.py where get_team_data will be called.
Now if records_data couldn't be found, an error is returned and none is returned.
"""
def get_team_data(year, team):
    load_dotenv()
    api_key= os.getenv('CFBD_API_KEY')
    if api_key is None:
        print("API_Key env variable has not been created yet")
        return None, None
    headers= {'Authorization': f'Bearer {api_key}'}
    sorted_players= get_top5_usage_players(headers, year, team)
    if not sorted_players:
        return None,None
    concurrent_assigning_of_player_data(headers, year, team, sorted_players)
    endpoint_records= 'records'
    parameters_records= {'year': year, 'team': team}
    records_data= request_the_api(endpoint_records, headers=headers, params=parameters_records)
    if records_data:
        victoryformation(sorted_players, records_data[0])
        return sorted_players, records_data[0]
    else:
        print(f"Unable to retrieve team info for {team}")
        return None, None
"""
The following function obtains the stat category I want returned based on the postion passed into the function. If the player is a WR or TE I want 
receiving stats, if the player is a QB I want passing stats, if the player is a RB I want rushing stats and if no position matches unknown is returned.
The stat category that is returned will allow me to pull the correct stats to display for each player based on their position on the football field
image.
"""
def obtain_playerST_category(position):
    if position in ('WR', 'TE'):
        return 'receiving'
    elif position == 'QB':
        return 'passing'
    elif position =='RB':
        return 'rushing'
    else:
        return 'unknown'
    
