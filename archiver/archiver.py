#!/usr/bin/env python3
import sys
import requests
from requests import RequestException


class ApiRequest:
    """
    Class to make API requests.

    Args:
        url (str): The URL of the API endpoint.
        username (str): The username for basic authentication.
        password (str): The password for basic authentication.

    Returns:
        None

    Raises:
        Exception: If any error occurs while making the request.
    """

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.headers = {
            "Content-Type": "application/json",
            "X-Requested-By": "GraylogCloud",
        }
        self.auth = (username, password)

    def get(self, params=None):
        """
        Make a GET request.

        Args:
            params (dict): The parameters to be sent in the query string.

        Returns:
            Response: The response from the API.

        Raises:
            RequestException: If any error occurs while making the request.
        """
        try:
            return requests.get(
                self.url, params=params, headers=self.headers, auth=self.auth
            )
        except RequestException as e:
            raise Exception(f"Error making GET request: {str(e)}")

    def post(self, data=None):
        """
        Make a POST request.

        Args:
            data (dict): The data to be sent in the request body.

        Returns:
            Response: The response from the API.

        Raises:
            RequestException: If any error occurs while making the request.
        """
        try:
            return requests.post(
                self.url, json=data, headers=self.headers, auth=self.auth
            )
        except RequestException as e:
            raise Exception(f"Error making POST request: {str(e)}")


def process_file(filename):
    """
    Process a file and archive indices.

    Args:
        filename (str): The name of the file to process.

    Returns:
        None

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If any error occurs while processing the file.
    """
    try:
        with open(filename, "r+") as file:
            lines = file.readlines()
        for line in lines:
            if not (
                line.lstrip().startswith("archived,")
                or line.lstrip().startswith("inprogress,")
            ):
                non_whitespace = line.strip()
                api = ApiRequest(
                    url=f"https://watchdog.graylog.cloud/api/plugins/org.graylog.plugins.archive/cluster/archives/{non_whitespace}",
                    username="rhDZJciRTAYT9UAzFzzz",
                    password="token",
                )

                if api.post():
                    print(f"Archiving {line}")
                    indices = []
                    for processed_line in lines:
                        indicie = processed_line
                        if processed_line == line:
                            indicie = f"archived,{line}"
                        indices.append(indicie)
                    data = "".join(indices)
                    with open(filename, "w") as fp:
                        fp.write(data)
                    break
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    """
    Main function to process a file.

    Args:
        None

    Returns:
        None

    Raises:
        SystemExit: If the usage message is printed.
    """
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
        sys.exit(1)
    process_file(sys.argv[1])
