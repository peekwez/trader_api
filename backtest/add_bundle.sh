#!/bin/bash

function _info () {
      tput setaf 6
      tput bold
      echo -ne '-- '
      tput smul
      echo $1
      echo
      tput sgr0
}

# get market from command line
#-----------------------------
market="CA"
if [[ "$1" != "" ]]; then
    market=$1
fi


# create symbolic link of bundle python file
_info "creating symbolic link to bundle script..."
export ZIPLINE=$VIRTUAL_ENV/lib/python2.7/site-packages/zipline
bundle_script="shawshank.py"
bundle_link=$ZIPLINE/data/bundles/$bundle_script
ln -sf $bundle_script $bundle_link


# get write unique symbols
# -------------------------
_info "writing symbols to temporary file..."
tickers="_tmp_data/symbols_$market.csv"
tickers_command="\copy (SELECT DISTINCT(symbol) AS symbol, ticker_id FROM \
prices INNER JOIN tickers ON prices.ticker_id=tickers.id WHERE \
market='$market' AND type='security' ORDER BY symbol, ticker_id) \
TO '$tickers' WITH DELIMITER ',' CSV HEADER;"
psql shawshank -c "$tickers_command"


# get prices for bundle
# ----------------------
_info "writing prices to temporary file..."
prices="_tmp_data/prices_$market.csv"
prices_command="\copy (SELECT date, open, high, low, close, volume, \
0.0 AS dividend, 1.0 AS split, symbol FROM prices INNER JOIN tickers \
ON prices.ticker_id=tickers.id WHERE market='$market' AND type='security' \
ORDER BY ticker_id ASC, date ASC) TO '$prices' WITH DELIMITER ',' CSV HEADER;"
psql shawshank -c "$prices_command"


# zipline upload
# ---------------
_info "ingesting bundle data into zipline..."
if [[ "$market" == "CA" ]]; then
    bundle_name="trader-canada"
elif [[ "$market" == "US" ]]; then
    bundle_name="trader-states"
fi
zipline clean -b $bundle_name --after 2000-01-01
zipline ingest -b $bundle_name

# clean up
# -------------
_info "cleaning up..."
unlink $bundle_link
rm -fr $prices $tickers
