from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPBindError
from server import app, logger

class Login(object):
    
    def ldap_auth(username: str, password: str) -> bool | str:
        """Authenticate user using LDAP."""
        ldap_server = f"ldap://{app.config['LDAP_HOST']}:{app.config['LDAP_PORT']}"
        
        user = f"{username}{app.config['LDAP_DOMAIN']}"
        
        server = Server(ldap_server, get_info=ALL)

        try:
            with Connection(server, user=user, password=password, auto_bind=True):
                return True
            
        except LDAPBindError as e:
            logger.error(f"LDAP bind failed for user {user}. Error: {e}")
            return "LDAP authentication failed"

        except Exception as e:
            logger.error(f"Unexpected error during LDAP authentication: {e}", exc_info=True)
            return f"Unexpected error: {e}"