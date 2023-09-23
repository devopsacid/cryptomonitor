#!/usr/bin/python3

import coin_yaml_helpers 
from yaml import safe_load, YAMLError
from pycoingecko import CoinGeckoAPI

from json import dumps
from sys import exit
import os 
from dotenv import load_dotenv

import datetime
import traceback
import logging
import time

# for version Influx 2.0+
# from influxdb_client import InfluxDBClient, Point, WriteOptions
# from influxdb_client.client.write_api import SYNCHRONOUS

# for version Influx 1.8
from influxdb import InfluxDBClient

def load_env():
    # load .env variables into environment
    if os.path.exists(".env"):
        load_dotenv(".env")
    else:
        print("No .env file found")
        exit(1)

# function to load yaml file
def load_yaml(filename):
    with open(filename, 'r') as stream:
        try:
              return safe_load(stream)
        except YAMLError as exc:
              logging.error(exc)

# function to load coins from coingecko
def load_cg_coins(coins,vs_currency):
    cg = CoinGeckoAPI()
    json = cg.get_price(ids=coins, vs_currencies=vs_currency, include_market_cap=True, include_24hr_vol=True, include_24hr_change=True)
    if logging.DEBUG:
        logging.debug("CoinGecko json:")
        logging.debug(json)
    return json

# function to archive data to json files on disk
def archive_data_file(dir,data):
    TODAY = datetime.datetime.now().strftime("%Y%m%d")
    NOW = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    if not os.path.exists(f"{dir}/jsons/{TODAY}"):
        logging.debug(f"Creating directory {dir}/jsons/{TODAY}")
        os.makedirs(f"{dir}/jsons/{TODAY}", exist_ok=True)
    with open(f"{dir}/jsons/{TODAY}/coins_{NOW}.json", 'w') as outfile:
        logging.debug(f"Writing to file {dir}/jsons/{TODAY}/coins_{NOW}.json")
        outfile.write(dumps(data))
    logging.debug("Archiving complete.")

def load_data_file(dir,datetime):
    with open(f"{dir}/jsons/{datetime}", 'r') as infile:
        logging.debug(f"Reading from file {dir}/jsons/{datetime}")
        return infile.read()

# function to archive data to InfluxDB
def archive_data_influx(data):
    # Set Influx to true to archive data to InfluxDB
    INFLUX_HOST=os.getenv("INFLUX_HOST", 'localhost')
    INFLUX_PORT=int(os.getenv("INFLUX_PORT", "8086"))
    INFLUX_DB=os.getenv("INFLUX_DB", 'maindb')
    INFLUX_USER=os.getenv("INFLUX_USER", 'coinarchiver')
    INFLUX_PASS=os.getenv("INFLUX_PASS", 'coinpass')
    INFLUX_BUCKET=os.getenv("INFLUX_BUCKET", 'cryptomon')
    INFLUX_ORG=os.getenv("INFLUX_ORG", 'cryptomon')
    influxURL=f"http://{INFLUX_HOST}:{INFLUX_PORT}"

    # open InfluxDB client connection
    try:  
        # client=InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_DB, INFLUX_USER, INFLUX_PASS)
        # INFLUXDB_V2_AUTH_BASIC=True
        
        # For InfluxDB 1.8
        with InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_DB, INFLUX_USER, INFLUX_PASS) as _client:
            logging.debug(f"Client connection to InfluxDB successful. {influxURL}")
            
        ### For InfluxDB 2.0+
        # with InfluxDBClient(url=influxURL, username=INFLUX_USER, password=INFLUX_PASS, org=INFLUX_ORG, debug=True) as _client:
        #     logging.debug(f"Client connection to InfluxDB successful. {influxURL}")

        # format output list
        output_list = []
        for coin in data:
            output_list.append(
            {
                "measurement": "coin",
                "tags": {
                "coin": coin
                },
                "fields": {
                "price": data[coin]['usd'],
                "market_cap": data[coin]['usd_market_cap'],
                "volume_24h": data[coin]['usd_24h_vol'],
                "percent_change_24h": data[coin]['usd_24h_change']
                }
            }
            )
            
        # write to InfluxDB 1.8
        with _client.create_database(INFLUX_DB) as _create_client:
            logging.debug(f"Client create database {INFLUX_DB} successful.")        
        with _client.write_points(output_list) as _write_client: 
            logging.debug("Client write to InfluxDB successful.")
        
        # write to InfluxDB 2.0+
        # with _client.write_api(write_options=SYNCHRONOUS) as _write_client: 
        #     _write_client.write(bucket=INFLUX_DB, record=output_list)
        #     logging.debug("Client write to InfluxDB successful.")

    except Exception as e: 
        logging.error(f"Problem with client connection to InfluxDB {influxURL}: {e}")
        logging.error(traceback.format_exc())

#
### main function
#
def main():
    # set environment
    targetEnv=os.getenv("TARGET_ENV", 'dev')
    # load .env variables into environment
    if targetEnv == 'dev' and os.path.exists(".env.dev"):
        load_dotenv(".env.dev")
    elif targetEnv == 'prod' and os.path.exists(".env.prod"):  
        load_dotenv(".env.prod")
    elif os.path.exists(".env"):
        load_dotenv(".env")
    else:
        print("TARGET_ENV not set to dev or prod")
        exit(1)

    # Debug mode
    if os.getenv("DEBUG", "False").lower() == "true":
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        
    sleep_time=int(os.getenv("SLEEP_TIME", "300"))

    # Set WORKDIR to the directory where the script is running
    WORKDIR=os.getenv("WORKDIR", '.')
    if WORKDIR == None:
        logging.error("WORKDIR not set")
        exit(1)
    elif not os.path.exists(WORKDIR):
        logging.error("WORKDIR does not exist")
        exit(1)
    else:
        os.chdir(WORKDIR)
        logging.info(f"WORKDIR set to {WORKDIR}")

    # load coins from yaml file
    logging.info("Loading coin list from yaml file.")
    coin_usd_yaml = load_yaml("coins_list_usd.yml")
    coins = coin_yaml_helpers.get_coin_list(coin_usd_yaml)
    if logging.DEBUG:
        logging.debug("Coin list:")
        logging.debug(coins)

    # load coins from coingecko
    logging.info("Loading CoinGecko data.")
    data = load_cg_coins(coins,'usd')

    # Set Archiver to true to archive data to json files on disk
    if os.getenv("FILE_ARCHIVE", "False").lower() == "true":
        logging.info(f"Archiving data to directory: {WORKDIR}/jsons")
        archive_data_file(dir=WORKDIR, data=data)
    else:
        logging.info("File archiving disabled.")

    # Set Influx to true to archive data to InfluxDB
    # INFLUX_ARCHIVE=os.getenv("INFLUX_ARCHIVE", 'false')
    if os.getenv("INFLUX_ARCHIVE", "False").lower() == "true":
        logging.info("Archiving data to InfluxDB.")
        archive_data_influx(data)
    else:
        logging.info("InfluxDB archiving disabled.")

if __name__ == "__main__":
    sleep_time=int(os.getenv("SLEEP_TIME", "60"))
    while True:
        main()
        logging.info(f"Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)            
    exit(0)
