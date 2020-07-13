import json
import ast

def search_bar_data():
  """
  Get the results (tickers) for the search bar results  
      
  Returns:
      search_bar: Json format of the search bar results 
  """
  search_bar = list()
  with open('search_bar_data.txt') as f:
      for line in f:
          data = ast.literal_eval(line)
          search_bar.append(data)

  search_bar = json.dumps(search_bar)
  return search_bar

