import json
import re

from utils.other_utils import flatten_list


import json
import re
from utils.other_utils import flatten_list


class JsonStrToDict:
    def __init__(self, max_attempts: int = 3):
        """
        Initialize with a maximum number of attempts to fix a JSON string.
        """
        self.max_attempts = max_attempts

    def json_to_dict(self, json_str: str) -> list:
        """
        Converts a JSON array within a string to a list of dictionaries.
        Tries to fix malformed JSON strings recursively.

        :param json_str: Input JSON string.
        :return: List of dictionaries.
        """
        if json_str is None:
            print("Input string is None. Returning empty list.")
            return []

        json_str = self._prefix_json_str(json_str)
        match_all = re.findall(r"\[.*?]", json_str)
        json_list = []

        if match_all:
            for element in match_all:
                try:
                    json_list.extend(json.loads(element))
                except json.JSONDecodeError as e:
                    if self.max_attempts > 0:
                        print(f"JSON decoding failed: {e}. Attempting to fix...")
                        fixed_json_str = self.fix_json_string(str(match_all))
                        return self.json_to_dict(fixed_json_str)
        return json_list

    def fix_json_string(self, json_str: str) -> str:
        """
        Attempts to fix a malformed JSON string by extracting key-value pairs.

        :param json_str: Malformed JSON string.
        :return: Fixed JSON string.
        """
        json_str = self._remove_invalid_characters(json_str)
        potential_objects = self._extract_json_objects(json_str)

        if not potential_objects:
            return "[]"

        fixed_data_list = self._process_potential_objects(potential_objects)
        return json.dumps(fixed_data_list)

    def rebuild_json_string(self, json_str: str) -> str:
        """
        Rebuilds a JSON string by splitting, cleaning, and reassembling key-value pairs.

        :param json_str: Input JSON string.
        :return: Rebuilt JSON string.
        """
        split_string = self._split_and_clean_string(json_str)
        keys, values = self._extract_keys_and_values(split_string)
        return str(dict(zip(keys, values)))

    @staticmethod
    def _prefix_json_str(json_str: str) -> str:
        """
        Fixes common JSON string mistakes such as single quotes and newlines.

        :param json_str: JSON string.
        :return: Fixed JSON string.
        """
        return json_str.replace("\n", "").replace("'", '"')

    @staticmethod
    def _remove_invalid_characters(json_str: str) -> str:
        """
        Removes invalid characters not part of the JSON structure.

        :param json_str: JSON string.
        :return: Cleaned JSON string.
        """
        return re.sub(r'[^\{\}\[\]\,\"\:\w\s\.\-]', "", json_str)

    @staticmethod
    def _extract_json_objects(json_str: str) -> list:
        """
        Extracts JSON-like objects (curly braces or square brackets).

        :param json_str: JSON string.
        :return: List of extracted JSON objects.
        """
        objects = re.findall(r"\{.*?}", json_str)
        return objects or re.findall(r"\[.*?]", json_str)

    def _process_potential_objects(self, potential_objects: list) -> list:
        """
        Processes potential JSON objects, fixing common issues.

        :param potential_objects: List of JSON-like strings.
        :return: List of fixed JSON dictionaries.
        """
        data_list = []
        for obj_str in potential_objects:
            fixed_obj_str = self._fix_common_json_issues(obj_str)
            try:
                data_list.append(json.loads(fixed_obj_str))
            except json.JSONDecodeError as e:
                rebuilt_str = self.rebuild_json_string(fixed_obj_str)
                try:
                    data_list.append(json.loads(rebuilt_str))
                except json.JSONDecodeError:
                    print(f"Failed to fix object: {fixed_obj_str} due to {e}")
        return data_list

    @staticmethod
    def _fix_common_json_issues(json_str: str) -> str:
        """
        Fixes common JSON syntax issues like missing quotes.

        :param json_str: JSON string.
        :return: Fixed JSON string.
        """
        json_str = re.sub(r"'", '"', json_str)  # Replace single quotes
        json_str = re.sub(r"(\w+)\s*:", r'"\1":', json_str)  # Quote keys
        return re.sub(r':\s*([^,"\{\}\[\]]+)\s*(,|\})', r': "\1"\2', json_str)  # Quote values

    @staticmethod
    def _split_and_clean_string(json_str: str) -> list:
        """
        Splits JSON strings by separators and removes unwanted characters.

        :param json_str: JSON string.
        :return: Cleaned list of split components.
        """
        split_string = json_str.split(",")
        split_string = [s.split('"') for s in split_string]
        split_string = flatten_list(split_string)
        split_string = [s.split(":") for s in split_string]
        split_string = flatten_list(split_string)
        return [s for s in split_string if not JsonStrToDict.has_only_special_chars(s)]

    @staticmethod
    def _extract_keys_and_values(split_string: list) -> (list, list):
        """
        Extracts keys and values from a split JSON string.

        :param split_string: List of JSON string components.
        :return: Tuple of keys and values.
        """
        keys = [x for i, x in enumerate(split_string) if i % 2 == 0]
        values = [x for i, x in enumerate(split_string) if i % 2 != 0]
        return keys, values

    @staticmethod
    def has_only_special_chars(s: str) -> bool:
        """
        Checks if a string contains only special characters.

        :param s: Input string.
        :return: True if only special characters, False otherwise.
        """
        return not any(c.isalnum() for c in s)


if __name__ == "__main__":
    # Example JSON strings
    json_strings = [
        '[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]',
        'Random text before [{"name": "Charlie", "age": "35"}] and after',
        'Malformed JSON [{"name": "Dana", "age": 40,] Missing bracket',
        '{"name": "Eve", "age": 28}',  # Not in an array
        None,
        'No JSON here',
        '[{"name": "Frank", "age": 33}], [{"name": "Grace", "age": "25"}]',
        '[{"name": "Heidi", "age": 45}, {"name": "Ivan", "age":, "city": "Berlin"}]',
        '[{"name": "Judy", "age": 29}, {"name": "Karl", "age": 31,}]',
        'Invalid JSON [{name: "Leo", age: 22}, {name: "Mona", age: 27}]',
    ]
    dict_list = []
    parser = JsonStrToDict()
    for s in json_strings:
        print(f"\nProcessing string: {s}")
        result = parser.json_to_dict(s)
        if len(result) > 0:
            dict_list.append(result)
    dict_list = flatten_list(dict_list)
