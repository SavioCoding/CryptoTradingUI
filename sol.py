import solara
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from get_data import get_currorders_df, get_returns_df, generate_return
from testnet_api import testnet_api_key, testnet_secret_key


@solara.component
def PnL():
    directory = "../trading/symToUnits"
    return_dict = get_returns_df(directory)
    with solara.ColumnsResponsive(small=12, medium=[6,6],large=[6, 6]):
        for strategy, df in return_dict.items():
            df["Date"] = df.index
            with solara.Card(title=strategy, margin = 1):
                fig = px.line(df, x="Date", y="total units (usdt)", markers=True)
                solara.FigurePlotly(fig)


@solara.component
def Positions():
    orderDirectory = '../trading/currOrders'
    symToUnitsDirectory = '../trading/symToUnits'
    data_dict = get_currorders_df(orderDirectory, symToUnitsDirectory, testnet_api_key, testnet_secret_key)
    with solara.ColumnsResponsive(small=12, medium=[6,6],large=[6, 6]):
        for strategy, df in data_dict.items():
            with solara.Card(title=strategy, margin = 1):
                fig = go.Figure(data=[go.Table(header=dict(values=['Symbol', 'Side','Entry-Time', 'Price (Entry)', 'Bought (usdt)', 'Price (Now)',
                                'Profit (usdt)', 'Return'], fill_color=['rgb(240, 240, 240)'], line_color=['rgb(0, 0, 0)'],align=['center'],),
                                cells=dict(values=[df["symbol"],df['side'],df['time'], df['entry_price'], df['quote_units'], df['currentPrice'],
                                                   df['Profit(usdt)'], df['return(%)']], line_color=['rgb(0, 0, 0)'],
                                           fill_color=[['rgb(204, 235, 197)' if float(x)>0 else 'rgb(183,201, 226)' if float(x)== 0 else 'rgb(255, 204, 203)' for x in list(df['Profit(usdt)'])]*7]))])
                fig.update_layout()
                solara.FigurePlotly(fig)

routes = [
    solara.Route(path="pnl", component=PnL, label="Profit and Loss"),
    solara.Route(path="positions", component=Positions, label = "Current Positions"),
]