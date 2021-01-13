#import mysql, dash, pandas and plotly
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector

#connecting a database
try:
    connection = mysql.connector.connect(host = 'localhost',
                                        user = 'root',
                                        passwd = 'qwertyc1',
                                        db = 'coffeeschema')
    df = pd.read_sql('SELECT * FROM coffeedata', connection)
except:
    print("Handled Error")
finally:
    connection.close()
    print("MySQL connection is closed")
bs = 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'

#Formatting the date for aesthetics
df['gradingDate'] = pd.to_datetime(df['gradingDate'], errors='coerce')
df['gradingDate'] = df['gradingDate'].dt.strftime("%d.%m.%Y.")

#defining colors
colors = {
    'background': '#cafcd6',
    'text': '#4a1b00'
}

#creating the dash app/choosing a stylesheet
app = dash.Dash(__name__, external_stylesheets=[bs])

#adding html elements as well as graphs we will need
app.layout = html.Div([
    html.Div(
            [
                #Title
                html.H1('Coffee Data', style={'textAlign':'center'} , id='title'),
                html.P('Select a cathegory from the dropdown to display a different graph. Hover over to display information about one instance. Click on the data instance, or select multiple, for detailed information inside world graph and pie chart', style={'marginLeft':100,'marginRight':100,'fontSize':20} , id='paragraph')
            ]
        ),
    dbc.Row(
            [
                #Main Dropdown
                dbc.Col(dcc.Dropdown(id='dropdown',
                                    options=[
                                        {'label':'Aroma','value':'aroma'},
                                        {'label':'Flavour','value':'flavor'},
                                        {'label':'Aftertaste','value':'aftertaste'},
                                        {'label':'Acidity','value':'acidity'},
                                        {'label':'Body','value':'body'},
                                        {'label':'Balance','value':'balance'},
                                        {'label':'Uniformity','value':'uniformity'},
                                        {'label':'Clean Cup','value':'cleanCup'},
                                        {'label':'Sweetness','value':'sweetness'},
                                        {'label':'Cupper Points','value':'cupperPoints'},
                                        {'label':'Total Cup Points','value':'totalCupPoints'},
                                        {'label':'Moisture %','value':'moisture'},
                                        {'label':'Altitude','value':'altitude'}],
                                     style={'color': colors['text'], 'height':40, 'marginBottom':15},
                                     optionHeight=30,
                                     searchable=True,
                                     clearable=False,
                                     value='aroma'
                                    ),
                        width={"size": 10, "offset": 1}
                        
                        )
            ]
        ),
    dbc.Row(
            [
                #Main chart
                dbc.Col(dcc.Graph(id='main_chart'),
                        width={"size": 10, "offset": 1}
                        )
            ]
        ),
    dbc.Row(
            [
                #World chart
                dbc.Col(dcc.Graph(id='world_chart',
                  config={'modeBarButtonsToRemove': ['toImage']}),
                        width=5
                        ),
                #Pie chart
                dbc.Col(dcc.Graph(id='pie_chart'),
                        width=5
                        ),
                #Pie dropdown
                dbc.Col(dcc.Dropdown(id='dropdownP',
                                    options=[
                                        {'label':'Year','value':'harvestYear'},
                                        {'label':'Country','value':'countryOfOrigin'},
                                        {'label':'Distributor','value':'distributor'}],
                                     style={'color': colors['text'], 'height':40, 'marginBottom':15},
                                     optionHeight=30,
                                     searchable=True,
                                     clearable=False,
                                     value='harvestYear'
                                    ),
                        width=2
                        )
                
            ]
        )
],
style={'backgroundColor':colors['background']})

#////////////////DASH CALLBACKS//////////////////

#Main chart callback
@app.callback(
    Output('main_chart','figure'),
    Input('dropdown','value')
)
def build_main(d_value):
    #creating a plotly express figure
    fig = px.line(df,
                  x='place',
                  y=d_value,
                  custom_data=['countryOfOrigin','region','distributor','harvestYear','gradingDate'] #for hover data
        
    )
    #details/ custom hover template
    fig.update_traces(
                        mode='lines+markers',
                        marker=dict(size=4),                        
                        hovertemplate=
                        "<b>Place:%{x}</b><br><br>" +
                        "Country of Origin: %{customdata[0]}<br>" +
                        "Region: %{customdata[1]}<br>" +
                        "Distributor: %{customdata[2]}<br>" +
                        "Harvest Year: %{customdata[3]}<br>" +
                        "Grading Date: %{customdata[4]}<br>" +#:%d.%b.%Y. later
                        d_value+": %{y:,.1f}" +
                        "<extra></extra>"
                     )
    fig.layout.plot_bgcolor = colors['background']
    fig.layout.paper_bgcolor = colors['background']
    return fig

#Pie chart callback
@app.callback(
    Output('pie_chart','figure'),
    Input('dropdownP','value'),
    Input('main_chart','clickData'),
    Input('main_chart','selectedData')
)
def build_pie(p_value,cData,sData):
    #getting values selected in dropdown
    data = df[p_value]
    #solution for getting the data out of cData format
    if p_value == 'harvestYear':  pNum = 3;
    elif p_value == 'distributor':  pNum = 2;
    else:  pNum = 0;
        
    if cData is not None and sData is None:      
        data = data[data == cData['points'][0]['customdata'][pNum]]
        
    elif sData is not None:
        tlist=[]
        for point in sData['points']:
            tlist.append(point['customdata'][pNum])
        data = pd.DataFrame(tlist,columns=[p_value])
    
    #creating a plotly express pie chart
    piechart=px.pie(
        data_frame=data,
        names=p_value,        
    )
    
    #details
    piechart.update_traces(textposition='inside',
                           marker=dict(line=dict(color='#000000', width=2)),
                           opacity=0.85,)
    piechart.update_layout(uniformtext_minsize=12,
                           uniformtext_mode='hide',
                           legend = dict(font = dict(size=15)))
    piechart.layout.plot_bgcolor = colors['background']
    piechart.layout.paper_bgcolor = colors['background']
    return piechart

#World chart callback
@app.callback(
    Output('world_chart','figure'),
    Input('main_chart','clickData'),
    Input('main_chart','selectedData')
)
def clickData(cData,sData):
    dic={}
    for index,row in df.iterrows():
        if row['countryOfOrigin'] not in dic.keys():
            dic.update({row['countryOfOrigin']:row['totalCupPoints']})
        else:
            #making the average value and updating the dictionary
            dic.update({row['countryOfOrigin']:(dic[row['countryOfOrigin']]+row['totalCupPoints'])/2})
    
    #formatting the dictionary to a dataframe for chart-use
    data = {'Countries':dic.keys(), 'Average Points':list(dic.values())}
    data = pd.DataFrame.from_dict(data)
    
    #checking for click data 
    if cData is not None and sData is None:
        country = cData['points'][0]['customdata'][0]
        data=data[data.Countries == country]
    #checking for select data 
    elif sData is not None:
        temp = data
        for point in sData['points']:
            temp = temp[temp.Countries != point['customdata'][0]]
        for index,row in temp.iterrows():
            data = data[data.Countries !=row.Countries]
    
    #creating world chart        
    fig=px.choropleth(data,locations='Countries',
              locationmode='country names',
              color='Average Points',
              title='World Map',
              hover_name='Countries',
              color_continuous_scale=px.colors.sequential.Bluered,
              projection='robinson'
             )
            
    #details    
    fig.update_layout(title=dict(font=dict(size=35),x=0.5,xanchor='center'))
    fig.layout.paper_bgcolor = colors['background']
    fig.update_layout(geo=dict(bgcolor= colors['background']))
    return fig

#Running the app
if __name__ == '__main__':
    app.run_server(debug=True)