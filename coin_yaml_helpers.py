import sys
import yaml

def get_coin_list(coin_yaml):
  '''
  Returns list of coins from yaml structure which should be loaded from a yaml configuration file.

      Parameters:
          coin_yaml (dict): yaml compounded dictionary structure where a list exists under coins key. Currently
                            the list item should be another dictionary but it's possible to extend this function
                            to support a simple string entry, if needed.

      Returns:
          result (list): List of coins as a simple list
  '''
  coins_yaml_list = coin_yaml['coins']
  result = []
  if type(coins_yaml_list) is list:
    for item in coins_yaml_list:
      if type(item) is dict and len(item)==1:
        for coin_key in item:
          result.append(coin_key)
      else:
        print('Error: "item" should be a dictionary with one key only', file=sys.stderr)
        print('Current value of "item" is:', file=sys.stderr)
        print(item, file=sys.stderr)
        sys.exit(1)
  else:
    print('Error: "coins_yaml_list" is not a list type', file=sys.stderr)
    print('Current value of "coins_yaml_list" is:', file=sys.stderr)
    print(coins_yaml_list, file=sys.stderr)
    sys.exit(1)
  return result




def get_tags_for_coin(coin_yaml, coin):
  '''
  Returns dictionary of tags for a given coin from yaml structure which should be loaded from a yaml configuration file.

      Parameters:
          coin_yaml (dict): yaml compounded dictionary structure where a list exists under coins key.

          coin (string): name of coin for which the tags dictionary should be returned

      Returns:
          result (dict): Dictionary of tags for given coin. If no tags are defined it will return an empty dictionary
  '''
  coins_yaml_list = coin_yaml['coins']
  if type(coins_yaml_list) is list:
    for item in coins_yaml_list:
      if type(item) is dict and len(item)==1:
        for coin_key in item:
          if coin_key == coin:
            coin_values = item[coin_key]
            if type(coin_values) is dict and 'tags' in coin_values and type(coin_values['tags']) is dict:
              return coin_values['tags']
            else:
              return {}
      else:
        print('Error: "item" should be a dictionary with one key only', file=sys.stderr)
        print('Current value of "item" is:', file=sys.stderr)
        print(item, file=sys.stderr)
        sys.exit(1)
  else:
    print('Error: "coins_yaml_list" is not a list type', file=sys.stderr)
    print('Current value of "coins_yaml_list" is:', file=sys.stderr)
    print(coins_yaml_list, file=sys.stderr)
    sys.exit(1)
  return {}


