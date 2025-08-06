import argparse
from urllib.parse import urlparse

from opensearchpy import OpenSearch


def list_fields(opensearch_host, index_name):
    # Parse the host string to extract username, password, and host
    parsed_url = urlparse(f"https://{opensearch_host}")
    username = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname

    # Check if username and password are provided
    if username is None or password is None:
        raise ValueError(
            "Username and password must be provided in the format 'username:password@host'"
        )

    # Connect to the OpenSearch cluster
    client = OpenSearch(
        hosts=[{"host": host, "port": 9200}],
        http_auth=(username, password),
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
    )

    # Get the index mapping
    mapping = client.indices.get_mapping(index=index_name)

    # Extract and print the fields
    properties = mapping[index_name]["mappings"]["properties"]
    fields = properties.keys()
    print(f"Fields in index '{index_name}':")
    for field in fields:
        print(field)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List fields in an OpenSearch index.")
    parser.add_argument("opensearch_host", type=str, help="The OpenSearch host.")
    parser.add_argument("index_name", type=str, help="The name of the index.")

    args = parser.parse_args()
    list_fields(args.opensearch_host, args.index_name)
