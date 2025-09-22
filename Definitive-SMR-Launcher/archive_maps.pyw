import __main__
import requests
def archive_maps():
    """
    Fetch a list of .7z map download URLs from an Internet Archive item.

    Parameters:
        identifier (str): The Internet Archive identifier (from the /details/ URL).

    Returns:
        List of tuples: [(filename, download_url), ...] for all .7z files in the item.
    """
    api_url = f"https://archive.org/metadata/{__main__.ginternetArchiveIdentifier}"
    try:
        resp = requests.get(api_url)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        __main__.error_logs(f"[archive_maps] Error fetching metadata: {e}", "error")
        return []

    urls = []
    for fileinfo in data.get("files", []):
        name = fileinfo.get("name")
        if name and name.lower().endswith(".7z"):
            download_url = f"https://archive.org/download/{__main__.ginternetArchiveIdentifier}/{name}"
            urls.append((name, download_url))

    return urls