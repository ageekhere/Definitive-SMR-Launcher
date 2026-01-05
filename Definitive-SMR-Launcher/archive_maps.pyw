import __main__ # Import the __main__ module so we can access variables and functions defined in the main script

def archive_maps():
    """
    Fetches metadata from Internet Archive for the given identifier
    and returns a list of downloadable .7z files.
    """

    # Build the Internet Archive metadata API URL
    # ginternetArchiveIdentifier must exist in __main__
    api_url = f"https://archive.org/metadata/{__main__.ginternetArchiveIdentifier}"

    try:
        # Send a GET request to the Internet Archive API
        resp = __main__.requests.get(api_url)

        # Raise an exception if the HTTP status is not 200 OK
        resp.raise_for_status()

        # Parse the JSON response into a Python dictionary
        data = resp.json()

    except Exception as e:
        # Log any errors (network issues, JSON parsing, etc.)
        __main__.error_logs("[archive_maps] Error fetching metadata: " + str(e),"error")
        # Return an empty list if something goes wrong
        return []

    # This list will store tuples of (filename, download_url)
    urls = []

    # Loop through all files listed in the metadata response
    for fileinfo in data.get("files", []):
        # Get the file name
        name = fileinfo.get("name")

        # Check if the file exists and is a .7z archive
        if name and name.lower().endswith(".7z"):
            # Build the direct download URL for the file
            download_url = (f"https://archive.org/download/"f"{__main__.ginternetArchiveIdentifier}/{name}")

            # Add the filename and its download URL to the list
            urls.append((name, download_url))

    # Return the list of (.7z filename, download URL) tuples
    return urls