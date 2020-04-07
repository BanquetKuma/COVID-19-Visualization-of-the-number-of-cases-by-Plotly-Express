import plotly_express as px
import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

# 感染者数読み込み
Confirmed_df = pd.read_csv("https://raw.githubusercontent.com/BanquetKuma/COVID-19-Visualization-of-the-number-of-cases-by-Plotly-Express\
                           /master/countries_codes_and_coordinates.csv?token=AKZOM364HFHDJBJ23WA4WLK6RR33A",header=1)


# 国名コード読み込み
ISO_alpha_3_df = pd.read_csv("https://github.com/BanquetKuma/COVID-19-Visualization-of-the-number-of-cases-by-Plotly-Express\
                            /blob/master/countries_codes_and_coordinates.csv",header=0)

# 列名を変更
Confirmed_df.rename(columns={'#adm1+name': 'State', '#country+name': 'Country',\
                             "#affected+infected+value+num":"Infected person(per day)"},inplace=True)

# "date"列をdatetimeのdtype='object' を dtype='datetime64[ns]' に変更
Confirmed_df["#date"] = pd.to_datetime(Confirmed_df["#date"], format='%Y-%m-%d')

# countryとiso_alphaの辞書を作る
dict_country = dict(zip(ISO_alpha_3_df["Country"], ISO_alpha_3_df["Alpha-3 code"]))

# 辞書に手動で追加
dict_country["US"]="USA"
dict_country["United Kingdom"]="GBR"
dict_country["Iran"]="IRN"
dict_country["Taiwan*"]="TWN"
dict_country["Korea, South"]="KOR"

# Confirmed_dfにiso_alpha列を作る
def func(x, dict_country=dict_country):
    if x in list(dict_country.keys()):
        return dict_country[x]
    else:
        return None

Confirmed_df["iso_alpha"] = Confirmed_df["Country"].apply(func)

# 'iso_alpha'列にNaNがある行を削除する
Confirmed_df.dropna(subset=['iso_alpha'], axis=0, inplace=True)

# 各国別のデータフレームを格納するリスト
dataframe_list = []

# インデックス（'pandas.core.indexes.datetimes.DatetimeIndex'をstr型に変更する)
# これは、Plotly Expressのanimation_frame指定する型はstr or int 型である必要があるため
f_strftime = lambda x:x.strftime('%Y-%m-%d')

# 国名をリストに格納する
country_list=list(set(Confirmed_df["Country"]))

# 各国のデータフレームを作る
for i in range(len(country_list)):
    df2 = Confirmed_df[Confirmed_df["Country"] == country_list[i]].sort_values(by="#date")
    df2 = pd.DataFrame(df2.groupby(['#date'])['Infected person(per day)'].sum())
    df2['Infected person(per day)'] = df2['Infected person(per day)'].diff()
    df2.dropna(subset=['Infected person(per day)'],inplace = True)
    df2["Date"] = df2.index.map(f_strftime)
    df2["Country"] = country_list[i]
    df2["iso_alpha"] = dict_country[country_list[i]]
    df2.reset_index(inplace=True, drop=True)
    dataframe_list.append(df2)

# すべてのデータフレームを縦に繋ぐ
df_all = pd.concat(dataframe_list, axis=0)

# 感染者数を対数変換する
df_all["log(Infected person(per day))"]=\
    np.log10(df_all["Infected person(per day)"]+1.0e-10)

fig = px.choropleth(df_all, locations="iso_alpha", color="log(Infected person(per day))",\
                        hover_name="Country", animation_frame="Date", range_color=[0, 4], width=1000, height=800)

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

app.run_server(debug=True,use_reloader=False)  # Turn off reloader if inside Jupyter
