import svn.remote as sr
import os
from server import logger
from config.directory_config import SOURCE_IN_DIRECTORY, LDAP_USERNAME, LDAP_PASSWORD
from utility.file_utils import check_directory_exists

def _get_svn_client(svn_file: str) -> sr.RemoteClient:
    """Helper function to create an SVN client."""
    try:
        svn = sr.RemoteClient(
            svn_file,
            username=LDAP_USERNAME,
            password=LDAP_PASSWORD
        )
        return svn
    except Exception as e:
        logger.error(f"Error connecting to SVN: {e}", exc_info=True)
        raise

def check_svn_correctness(svn_file: str, template: str) -> bool | str:
    """Check svn file path correctness"""
    try:
        svn = _get_svn_client(svn_file)
        entries = svn.list()
        for filename in entries:
            if filename == template:
                return True
        return False
    except Exception as e:
        logger.error(f"Error in check_svn_correctness: {e}", exc_info=True)
        return False
    
def checkout_svn_file(svn_file: str, template: str, platform: str ,app_name: str) -> bool | str:
    """Get svn file and save to local directory"""
    store_path = os.path.join(SOURCE_IN_DIRECTORY, platform, app_name)
    check_directory_exists(store_path)
    
    try:
        svn = _get_svn_client(svn_file)
        file_content = svn.cat(template)
        with open(os.path.join(store_path, template), 'wb') as file:
            file.write(file_content)
        return True
    except Exception as e:
        logger.error(f"Error in checkout_svn_file: {e}", exc_info=True)
        return False
