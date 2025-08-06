# -*- coding: utf-8 -*-
import json
import base64


class JsonConverter:

    def __init__(self) -> None:
        pass

    def loads(self, input):
        try:
            output = json.loads(input)
            return output
        except Exception as e:
            raise Exception(e)

    def decode(self, input):
        try:
            output = json.JSONDecoder().decode(input)
            return output
        except Exception as e:
            raise Exception(e)

    def encode(self, input):
        try:
            output = json.JSONEncoder().encode(input)
            return output
        except Exception as e:
            raise Exception(e)

    def pretty(self, input):
        if isinstance(input, str):
            try:
                json_input = json.loads(input)
                return json.dumps(json_input, indent=4)
            except Exception as e:
                pass
        return None


class Base64Converter:
    """
    A class for encoding and decoding Base64 strings.

    Attributes:
        None

    Methods:
        encode_base64(input_string): Encode a string into Base64 format.
        decode_base64(encoded_string): Decode a Base64 encoded string back into its original format.
        check_base64_format(input_string): Check if the input string is in Base64 format.
    """

    @staticmethod
    def encode(input_string):
        """
        Encode a string into Base64 format.

        Args:
            input_string (str): The string to be encoded.

        Returns:
            str: The encoded string in Base64 format.

        Raises:
            TypeError: If the input is not a string.
        """
        if not isinstance(input_string, str):
            raise TypeError("Input must be a string")

        try:
            encoded_string = base64.b64encode(input_string.encode("utf-8"))
            return encoded_string.decode("utf-8")
        except Exception as e:
            print(f"An error occurred during encoding: {e}")
            return None

    @staticmethod
    def decode(encoded_string):
        """
        Decode a Base64 encoded string back into its original format.

        Args:
            encoded_string (str): The Base64 encoded string to be decoded.

        Returns:
            str: The decoded string in its original format.

        Raises:
            TypeError: If the input is not a string.
        """
        if not isinstance(encoded_string, str):
            raise TypeError("Input must be a string")

        try:
            decoded_bytes = base64.b64decode(encoded_string)
            return decoded_bytes.decode("utf-8")
        except Exception as e:
            print(f"An error occurred during decoding: {e}")
            return None

    @staticmethod
    def check_base64_format(input_string):
        """
        Check if the input string is in Base64 format.

        Args:
            input_string (str): The string to be checked.

        Returns:
            bool: True if the input string is in Base64 format, False otherwise.
        """
        try:
            base64.b64decode(input_string)
            return True
        except Exception as e:
            print(f"Error checking Base64 format: {e}")
            return False
