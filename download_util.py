#
#   File: download_util.py
#   Author: Lawrence Buckingham, Donna Kingsbury, Colin Fidge
#   Copyright: Queensland University of Technology (QUT) 2024
#
#   This file defines three utility functions which may be used to download
#   data via HTTP, HTTPS, or FTP.
#
#   download_bytes
#       Attempts to download a resource, and if successful returns the raw
#       binary representation of the resource as a sequence of bytes.
#
#   download_string
#       Attempts to download a resource, and if successful returns the content
#       of the resource decoded into a string.
#
#   download_file
#       Attempts to download a resource, and if successful saves the raw
#       binary representation to a file.
#

def download_bytes(url: str) -> bytes:
    '''
    Attempts to download the resource specified by parameter url.

    Parameters:
    url (str): A string which specifies the URL of the resource.

    Returns:
    bytes: A sequence of bytes which contains the downloaded content.
    
    Raises:
    HTTPError: If access to the requested resource is denied
    ValueError: If requested resource does not exist
    '''
    import urllib.request as rq

    try:
        # First attempt: try to download the page without identifying our user 
        # agent
        request = rq.Request(url)
        binary_data = rq.urlopen(request).read()

    except rq.HTTPError:
        # Second attempt: if access is denied, try (just once) again with a 
        # widely-used user agent string. If the second attempt fails, give up.
        request = rq.Request(url) 
        request.add_header("User-Agent", "Mozilla/5.0")
        binary_data = rq.urlopen(request).read()
    
    # If we reach this point, one of the download attempts worked.
    return binary_data


def download_string( url: str, character_encoding: str = 'UTF-8' ) -> str:
    '''
    Download the contents of a resource as a string.

    Parameters:
    url (str): The URL of the resource.

    character_encoding (str): The name of a character encoding.

    Returns:
    str: A string containing the downloaded text.
    
    Raises:
    HTTPError: If access to the requested resource is denied
    ValueError: If requested resource does not exist
    '''
    binary_data = download_bytes(url)
    return binary_data.decode(character_encoding)


def download_file(url: str, save_file_name: str) -> None:
    '''
    Saves the content of resource identified by *url* into the file 
    indicated by *save_file_name*.

    Parameters:
    url (str): The address of the resource to download.
    save_file_name: The name of a file which will be overwritten with the 
        downloaded data.

    Returns:
    None.
    
    Raises:
    HTTPError: If access to the requested resource is denied.
    ValueError: If requested resource does not exist.
    '''
    content = download_bytes(url)
    file = open(save_file_name, 'wb')
    file.write(content)
    file.close()

pass


