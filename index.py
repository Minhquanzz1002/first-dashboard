from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# TẢI DỮ LIỆU TỪ FIRESTORE
cred = credentials.Certificate("iuh-20098151-firebase-adminsdk-wyb05-41ce913fdb.json")
appLoadData = firebase_admin.initialize_app(cred)

dbFireStore = firestore.client()

queryResults = list(dbFireStore.collection(u'tbl-20098151').where(u'DEALSIZE',u'==', 'Large').stream())
listQueryResult = list(map(lambda x: x.to_dict(), queryResults))

df = pd.DataFrame(listQueryResult)

df['YEAR_ID'] = df['YEAR_ID'].astype('str')
df['QTR_ID'] = df['QTR_ID'].astype('str')

df["PROFIT"] = df["SALES"] - (df["QUANTITYORDERED"] * df["PRICEEACH"])
dfGroupByYear = df.groupby("YEAR_ID").sum()
dfGroupByYear["YEAR_ID"] = dfGroupByYear.index

# TRỰC QUAN HÓA DỮ LIỆU WEB APP

app = Dash(__name__)
server = app.server
app.title = 'Trực quan hóa dữ liệu'

fig_sales_by_year = px.bar(dfGroupByYear, x='YEAR_ID', y="SALES",
                           title='Doanh số bán hàng theo năm', color='YEAR_ID',
                           labels={'YEAR_ID': 'Năm', 'SALES': 'Doanh số'})

fig_profit_by_year = px.line(dfGroupByYear, x='YEAR_ID', y="PROFIT",
                             title='Lợi nhuận bán hàng theo năm',
                             labels={'YEAR_ID': 'Năm', 'PROFIT': 'Lợi nhuận'})


fig_sales_ratio = px.sunburst(df, path=['YEAR_ID', 'CATEGORY'], values='SALES',
                              color='SALES',
                              labels={'parent': 'Năm', 'id': 'Danh mục','SALES': 'Doanh số', 'SALES_sum': 'Tổng doanh số'},
                              title='Tỉ lệ đóng góp của doanh số theo từng danh mục trong từng năm')

fig_profit_ratio = px.sunburst(df, path=['YEAR_ID', 'CATEGORY'], values='PROFIT',
                               color='PROFIT',
                               labels={'parent': 'Năm', 'id': 'Danh mục', 'PROFIT': 'Lợi nhuận', 'PROFIT_sum': 'Tổng lợi nhuận'},
                               title='Tỉ lệ đóng góp của lợi nhuận theo từng danh mục trong từng năm')

total_sales = "${:,.2f}".format(round(df["SALES"].sum(), 2))
total_profit = "${:,.2f}".format(round(df['PROFIT'].sum(), 2))
top_sales = "${:,.2f}".format(df.groupby('CATEGORY').sum()['SALES'].max())
top_profit = "${:,.2f}".format(round(df.groupby('CATEGORY').sum()['PROFIT'].max(), 2))

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=['XÂY DỰNG DANH MỤC SẢN PHẨM TIỀM NĂNG'],
                    className='header_title'
                ),
                html.Div(
                    children=['IUH - DHKTPM16B - 20098151 - NGUYỄN MINH QUÂN'],
                    className='header_title'
                )
            ],
            className='header'
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.H3('DOANH SỐ SALE'),
                                html.Div(total_sales)
                            ],
                            className='card_statistic'
                        ),
                        html.Div(
                            children=[
                                html.H3('LỢI NHUẬN'),
                                html.Div(total_profit)
                            ],
                            className='card_statistic'
                        ),
                        html.Div(
                            children=[
                                html.H3('TOP DOANH SỐ'),
                                html.Div(top_sales)
                            ],
                            className='card_statistic'
                        ),
                        html.Div(
                            children=[
                                html.H3('TOP LỢI NHUẬN'),
                                html.Div(top_profit)
                            ],
                            className='card_statistic'
                        )
                    ],
                    className='content_statistic'
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[dcc.Graph(id='doanhsotheonam', figure=fig_sales_by_year)],
                            className='card_chart'
                        ),
                        html.Div(
                            children=[dcc.Graph(id='tiledoanhso', figure=fig_sales_ratio)],
                            className='card_chart'
                        ),
                        html.Div(
                            children=[dcc.Graph(id='loinhuanthoenam', figure=fig_profit_by_year)],
                            className='card_chart'
                        ),
                        html.Div(
                            children=[dcc.Graph(id='tileloinhuan', figure=fig_profit_ratio)],
                            className='card_chart'
                        )
                    ],
                    className='content_chart'
                )
            ]
        )
    ],
    className='wrapper'
)


if __name__ == '__main__':
    app.run_server()
