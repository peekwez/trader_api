# _*_ coding: utf-8 -*-

import pandas as pd
import requests

from constants import TICKER_LIST, VALUATION_LIMIT

class TickerReader(object):
    def __init__(self,url,vendor="yahoo"):
        self.__url = url
        self.__df = self.__get_tickers(vendor)
        self.__dt = self.__df_to_dict()

    def get(self,exchange,dataframe=True):
        if dataframe:
            return self.__get_df(exchange)
        else:
            return self.__get_dict(exhange)

    def post(self,exchange):
       resp =  self.__post(exchange)
       return resp

    def __post(self,exchange):
        data = self.__dt[exchange]
        resp = requests.post(
            self.__url,
            json=data
        )
        return resp

    def __get_df(self,exchange):
        return self.__df[exchange]

    def __get_dict(self,exchange):
        return self.__dt[exchange]

    def __get_tickers(self,vendor="yahoo"):
        filename = TICKER_LIST.get("filename")
        sheets = TICKER_LIST.get("sheets")
        columns = TICKER_LIST.get("columns")

        df = dict()
        for sheet in sheets:

            # read excel data
            tmp = pd.read_excel(filename,sheet_name=sheet)

            # select columns needed
            usecol = tmp.columns.intersection(columns)
            tmp = tmp[usecol]

            # lower cases for column names
            tmp.columns = map(str, tmp.columns)
            tmp.columns = map(str.lower, tmp.columns)

            # drop duplicate companies
            tmp.drop_duplicates(subset=("name"),inplace=True)

            # drop companies below valuation limit
            limit = VALUATION_LIMIT.get(sheet)
            tmp = tmp[tmp.value >= limit]

            # drop income funds from tmx
            if sheet == "tmx":
                tmp = tmp[tmp.sector != "Closed-End Funds"]
                if vendor == "yahoo":
                    tmp['symbol'] = tmp.apply(
                        lambda row:self.__modify_symbols(row),
                        axis=1,
                    )
                tmp["market"] = "CA"

            # remove duplicates alread on NYSE from NASDAQ
            elif sheet == "nasdaq":
                on_nyse = (
                    "AMOV","EGHT","GOLD","MSG","NCLH",
                    "PGTI","QGEN","RRD","SAVE","UNFI"
                )
                tmp = tmp[~tmp.symbol.isin(on_nyse)]
                tmp["market"] = "US"
            else:
                tmp["market"] = "US"

            # drop valuation and append security
            tmp.drop("value",axis=1,inplace=True)
            tmp["type"] ="security"

            # drop NaNs to None
            tmp.where(pd.notnull(tmp),None,inplace=True)

            # set data frame
            df[sheet] = tmp


        return df

    def __modify_symbols(self,row):
        sym = str(row["symbol"]).strip()
        if row["exchange"] == "TSX":
            sym = sym.replace(".","-") + ".TO"
        elif row["exchange"] == "TSXV":
            sym = sym.replace(".","-") + ".V"
        return sym

    def __df_to_dict(self):
        dt = dict()
        for key, val in self.__df.items():
            tmp = val.to_dict(orient="index").values()
            dt[key] = tmp
        return dt



tickers = TickerReader(
    "http://localhost:5000/trader/api/v1/tickers"
)
