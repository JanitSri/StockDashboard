import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import datetime 

def make_plot(chart_data='https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv'):
  """
  Renders the plot using a pandas dataframe 
  
  Parameters:
      chart_data: chart data to be used for the plot 
      
  Returns:
      graphJSON: Json format of the chart to be rendered by Plotly 
  """
  df = pd.DataFrame(chart_data, columns =['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'AdjClose'])
  df['Date'] = df['Date'].apply(lambda d: d.strftime(r'%Y-%m-%d'))

  data = [go.Scatter(
    x = df['Date'], 
    y= df['Close']
    )]

  graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

  return graphJSON
