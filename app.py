"""
app.py's purpose is to monitor the coherencey of all the steps in the web application. In app.py the libraries are first uploaded to allow for
handling a variety of things. Importing os and load_dotenv serve the purpose of providing access to the env file with the api keys. The openai and time
libraries deal with the handling of the chatgpt request. The get_team_data import creates a detailed png image utilizing the data of a team from
a year that the user provided. get_team_data also provides a sorted_players list and team_info dictionary. Flask is imported to manage the functionality of the 
system. After the libraries are imported, budget variables are listed for monitoring the cost of the chatgpt requests. Then this module is made the flask application, the
environment variable is loaded in and a client is made utilizing an openai api key. The route signfies that when a user navigates to http://127.0.0.1:5000/,
the home function should handle GET and POST methods since the home function follows the decorator. Until a user submits a form, flask will render
the index.html template. Once a user submits a form, flask will handle the request and retrieve the team and year. The sorted_players list and team_info 
dictionary are also retrieved. Then some error checking begins to make sure that the function was in fact able to retrieve data from the user provided team
in the user provided year and to make sure any other error doesn't exist such as going over the budget limit for the api requests after the chatgpt request
is made. The chatgpt request is made utilizing a function that includes my budgeting tactics for requests made to the chatgpt api account access that I pay for and
the function inlcudes the ability to make a request to retrieve info for the specified team in the specified year. There is also a max_tokens amount set to ensure that chatgpt does not provide 
too long of a response. The formatting of the chatgpt request was made available on chatgpt's website and stack overflow, which made the request a smoother process 
and allowed for me to understand the chatgpt error checking. Given a response was received from the chatgpt request and no other issues persist, flask will render 
the results.html template to the user. The user is then given some info about the data and flasks's url_for function is used to navigate to a route that retrieves the football 
field png image. The detailed football image the user asked for will then be portrayed and chatgpt will offer even more info on 
the user's football team in a specified year below the football field.
"""
import os
from dotenv import load_dotenv
import openai
from flask import Flask, request, render_template, send_file
from obtaindata import get_team_data
import time

load_dotenv()
client= openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
app= Flask(__name__)

budget_lim= 5.00
cost_per_1000_input_tokens= 0.005
cost_per_1000_output_tokens= 0.015
total_cost_used= 0

@app.route('/', methods=['GET', 'POST'])
def home():
    global total_cost_used
    if request.method == 'POST':
        team = request.form['team']
        year= request.form['year']
        sorted_players, team_info= get_team_data(year,team)
        if sorted_players and team_info:
            remaining_budget= budget_lim - total_cost_used
            if remaining_budget > 0:
                chatgpt_response, cost_used = get_chatgpt_response(team,year)
                if cost_used > 0:
                    total_cost_used += cost_used
                    return render_template('results.html', players=sorted_players, team_info=team_info, chatgpt_response=chatgpt_response, year=year)
                else:
                    return render_template('index.html', error="Unable to get a response from ChatGPT.")
            else:
                return render_template('index.html', error="Budget limit exceeded.")
        else:
            return render_template('index.html', error="Unable to retrieve data for specified team and year.")
    return render_template('index.html')

def get_chatgpt_response(team, year):
    attempt= 0
    max_attempts= 5
    max_tokens= 750
    while attempt < max_attempts:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an extremely useful assistant."},
                    {"role": "user", "content": f"Tell me about {team} football team's performance in the {year} season."}
                ],
                max_tokens=max_tokens
            )
            prompt_tokens_used= response.usage.prompt_tokens
            completion_tokens_used= response.usage.completion_tokens

            cost_used= (prompt_tokens_used / 1000) * cost_per_1000_input_tokens + (completion_tokens_used/1000) * cost_per_1000_output_tokens

            return response.choices[0].message.content.strip(), cost_used
        except openai.RateLimitError as e:
            attempt+=1
            print("An 429 error has occured")
            print(f"Retrying in {2 ** attempt} seconds..")
            time.sleep(2 ** attempt)
            pass
        except openai.APIConnectionError as e:
            print("An API connection error has occured")
            print(e.__cause__)
            break
        except openai.APIError as e:
            print("Another non-200-range status code was received")
            print(e.http_status)
            time.sleep(e.response)
            break
        except openai.OpenAIError as e:
            print(f"OpenAI returned an API Error: {e}")
            break
    return "Error: Could not produce response due to rate limit or other errors", 0

if __name__ == '__main__':
    app.run(debug=True) 
