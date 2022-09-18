import logging
import json
from ibmsecurity.utilities import tools

logger = logging.getLogger(__name__)


def get_all(isamAppliance, check_mode=False, force=False):
    """
    Retrieving the complete list of SCIM configuration settings
    """
    return isamAppliance.invoke_get("Retrieving the complete list of SCIM configuration settings",
                                    "/mga/scim/configuration")


def get_user_profile(isamAppliance, check_mode=False, force=False):
    """
    Retrieve configuration of SCIM user profile settings
    """
    ret_obj = isamAppliance.invoke_get("Retrieve configuration of SCIM user profile settings",
                                       "/mga/scim/configuration/urn:ietf:params:scim:schemas:core:2.0:User")
    return ret_obj['data']['urn:ietf:params:scim:schemas:core:2.0:User']


def get_isam_user(isamAppliance, check_mode=False, force=False):
    """
    Retrieve configuration of SCIM ISAM user settings
    """
    ret_obj = isamAppliance.invoke_get("Retrieve configuration of SCIM ISAM user settings",
                                       "/mga/scim/configuration/urn:ietf:params:scim:schemas:extension:isam:1.0:User")
    return ret_obj['data']['urn:ietf:params:scim:schemas:extension:isam:1.0:User']


def update_user_profile(isamAppliance, ldap_connection, user_suffix, search_suffix, check_mode=False, force=False):
    """
    Update SCIM user profile settings
    """
    ret_obj = get_user_profile(isamAppliance)
    del ret_obj['ldap_connection']
    del ret_obj['user_suffix']
    del ret_obj['search_suffix']

    ret_obj['ldap_connection'] = ldap_connection
    ret_obj['user_suffix'] = user_suffix
    ret_obj['search_suffix'] = search_suffix
    return isamAppliance.invoke_put(
        "Update SCIM user profile settings",
        "/mga/scim/configuration/urn:ietf:params:scim:schemas:core:2.0:User",
        ret_obj)


def update_isam_user(isamAppliance, isam_domain, update_native_users, ldap_connection, check_mode=False, force=False):
    """
    Update SCIM ISAM user settings
    """
    ret_obj = get_isam_user(isamAppliance)
    del ret_obj['isam_domain']
    del ret_obj['update_native_users']
    del ret_obj['ldap_connection']

    ret_obj['isam_domain'] = isam_domain
    ret_obj['update_native_users'] = update_native_users
    ret_obj['ldap_connection'] = ldap_connection
    return isamAppliance.invoke_put(
        "Update SCIM ISAM user settings",
        "/mga/scim/configuration/urn:ietf:params:scim:schemas:extension:isam:1.0:User",
        ret_obj)


def set_all(isamAppliance, scim_configuration, check_mode=False, force=False):
    """
    Update entire SCIM settings
    """
    if scim_configuration is None or scim_configuration == '':
        return isamAppliance.create_return_object(
            warnings="Need to pass content for scim configuration")
    # Feature: Converting python string to dict (if required)
    # Attention: JSON strings must use " quotes according to RFC 8259
    # Example: '{"a":1, "b": 2, "c": 3}'
    if isinstance(scim_configuration, str):
        scim_configuration = json.loads(scim_configuration)
    if force is True or _check(isamAppliance, scim_configuration) is False:
        return (
            isamAppliance.create_return_object(changed=True)
            if check_mode is True
            else isamAppliance.invoke_put(
                "Update SCIM settings",
                "/mga/scim/configuration",
                scim_configuration,
            )
        )

    return isamAppliance.create_return_object()


def _check(isamAppliance, scim_configuration):
    """
    Check if scim configuration is identical with server
    """
    ret_obj = get_all(isamAppliance)
    logger.debug("Comparing server scim configuration with desired configuration.")
    # Converting python ret_obj['data'] and scim_configuration from type dict to valid JSON (RFC 8259)
    # e.g. converts python boolean 'True' -> to JSON literal lowercase value 'true'
    cur_json_string = json.dumps(ret_obj['data'])
    cur_sorted_json = tools.json_sort(cur_json_string)
    logger.debug("Server JSON : {0}".format(cur_sorted_json))
    given_json_string = json.dumps(scim_configuration)
    given_sorted_json = tools.json_sort(given_json_string)
    logger.debug("Desired JSON: {0}".format(given_sorted_json))
    if cur_sorted_json != given_sorted_json:
        return False
    logger.debug("Server configuration is identical with desired configuration. No change necessary.")
    return True
