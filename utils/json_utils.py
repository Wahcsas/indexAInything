import json
import re
import pandas as pd


def json_to_dataframe(json_str: str, attempts: int = 3) -> pd.DataFrame:
    """
    Converts a JSON array within a string to a pandas DataFrame.
    Tries to fix malformed JSON strings recursively using final_attempt_fix.
    """
    if json_str is None:
        print('Input string is None. Returning empty DataFrame.')
        return pd.DataFrame()
    json_str = prefix_json_str(json_str=json_str)
    # Extract JSON array from the string
    match = re.search(r"\[.*?]", json_str)

    if isinstance(match, re.Match):
        flat_array_str = match.group(0)
    elif isinstance(match, list):
        json_list = [json.loads(json_list_element) for json_list_element in match]
        flat_array_str = str([lv2_el for lv1_list in json_list for lv2_el in lv1_list])
    else:
        print("No JSON array found in the string.")
        return pd.DataFrame()

    try:
        # Parse the JSON string and convert to DataFrame
        data = json.loads(flat_array_str)
        return pd.DataFrame(data)
    except json.JSONDecodeError as e:
        if attempts > 0:
            print(f"JSON decoding failed due to: {e}. Attempting to fix...")
            fixed_json_str = rebuild_json_string(flat_array_str)
            return json_to_dataframe(fixed_json_str, attempts - 1)
        else:
            print("Failed to parse JSON after multiple attempts.")
            return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()


def prefix_json_str(json_str: str) -> str:
    """
    prefixe common mistake in a json str
    :param json_str:
    :return: fixed json_st
    """
    json_str = json_str.replace('\n', '')
    json_str = json_str.replace('\'', '\"')
    return json_str


def rebuild_json_string(json_str: str) -> str:
    """
    Attempts to fix a malformed JSON string by extracting key-value pairs
    and rebuilding the JSON array.
    """
    # Remove any characters that are not part of the JSON structure
    json_str = re.sub(r'[^\{\}\[\]\,\"\:\w\s\.\-]', '', json_str)
    # Find all JSON-like objects
    potential_objects = re.findall(r'\{.*?\}', json_str)
    data_list = []
    for obj_str in potential_objects:
        # Try to fix common issues
        obj_str = re.sub(r'\'', '"', obj_str)  # Replace single quotes with double quotes
        obj_str = re.sub(r'(\w+)\s*:', r'"\1":', obj_str)  # Ensure keys are quoted
        obj_str = re.sub(r':\s*([^,"\{\}\[\]]+)\s*(,|\})', r': "\1"\2', obj_str)  # Ensure values are quoted
        try:
            data = json.loads(obj_str)
            data_list.append(data)
        except json.JSONDecodeError as e:
            print(f"Failed to fix object: {obj_str} due to {e}")
    if data_list:
        return json.dumps(data_list)
    else:
        return '[]'


def has_only_special_chars(s: str) -> bool:
    """
    Checks if the input string consists only of special characters.
    """
    return not any(c.isalnum() for c in s)

