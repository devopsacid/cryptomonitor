import pytest
import os
from unittest.mock import patch, mock_open, MagicMock
import cryptomonitor  # replace with the actual name of your script

@pytest.fixture
def setup_env_vars():
    os.environ['DEBUG'] = 'true'
    os.environ['WORKDIR'] = '.'
    os.environ['FILE_ARCHIVE'] = 'true'
    os.environ['INFLUX_ARCHIVE'] = 'true'

def test_load_yaml(setup_env_vars):
    m = mock_open(read_data="some_yaml_data")
    with patch("cryptomonitor.open", m):
        result = cryptomonitor.load_yaml("filename.yml")
        assert result == "some_yaml_data"


def test_load_cg_coins(setup_env_vars):
    with patch("cryptomonitor.CoinGeckoAPI") as MockCGAPI:
        MockCGAPI().get_price.return_value = {"bitcoin": {"usd": 45000}}
        result = cryptomonitor.load_cg_coins("bitcoin", "usd")
        assert result == {"bitcoin": {"usd": 45000}}


def test_archive_data_file(setup_env_vars):
    m = mock_open()
    with patch("cryptomonitor.open", m):
        cryptomonitor.archive_data_file(".", {"bitcoin": {"usd": 45000}})
        m.assert_called_once_with("./jsons/.../coins_....json", 'w')  # simplify this line in actual test


def test_load_data_file(setup_env_vars):
    m = mock_open(read_data='{"bitcoin": {"usd": 45000}}')
    with patch("cryptomonitor.open", m):
        result = cryptomonitor.load_data_file(".", "some_datetime")
        assert result == '{"bitcoin": {"usd": 45000}}'


def test_archive_data_influx(setup_env_vars):
    with patch("cryptomonitor.InfluxDBClient") as MockInfluxDB:
        cryptomonitor.archive_data_influx({"bitcoin": {"usd": 45000}})
        MockInfluxDB.assert_called()
