"""
This type stub file was generated by pyright.
"""

class Bitbucket:
    """Bitbucket API main entrypoints"""
    def __init__(self, base_url=...) -> None:
        ...
    
    def open_basic_session(self, username, password): # -> None:
        """Connect to the API with basic au"""
        ...
    
    async def close_session(self): # -> None:
        """Clean up the session"""
        ...
    


