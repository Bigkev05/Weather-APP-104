
class LocalHtmlException(Exception):
    '''
    Custom exception type used to indicate problems with local file name
    '''
    def __init__(self, file_name: str, message: str ):
        super().__init__(f"Local file '{file_name}' is not valid: {message}")


def open_html_file(file_name: str) -> int:
    '''
    Opens a local html document with the system browser. 
    
    Parameters:
    file_name {str}: The name of a file which must existin in the present working
                     directory. The file name must also end with the suffix "html".
    '''
    import os
    import os.path as path
    
    if not file_name.endswith('.html'): 
        raise LocalHtmlException(file_name, 'must end with ".html"')
    
    # Confirm that the file is in the present working directory
    if not path.isfile(path.join(os.curdir,file_name)):
        raise LocalHtmlException(file_name, 'must exist in current directory')
    
    # Collect all the exit codes for each attempt
    exit_codes = []
    
    open_commands = (
        ("Windows", "start",    "{0}"    ),
        ("MacOS",   "open",     "'./{0}'"),
        ("Linux",   "xdg-open", "'./{0}'")
    )

    # Attempt to use each system-specific command to open the document
    for (system_name, command, format_string) in open_commands:
        code = os.system(f'{command} {format_string.format(file_name)}')

        if code != 0:
            # Failed: save diganostic information for later
            exit_codes.append(f'{system_name} -> {code}')
        else:
            # Succeeded: return from function
            return
    
    # If any attempt was successful, this point cannot be reached, so raise error.
    raise LocalHtmlException(file_name, f'open failed. Exit codes: {str(exit_codes)}')

