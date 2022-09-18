import logging
from ibmsecurity.isam.appliance import commit

logger = logging.getLogger(__name__)

# URI for this module
uri = "/wga/kerberos/config/capaths"
requires_modules = ['wga']
requires_version = None
import ibmsecurity.isam.web.kerberos_configuration.ca_paths as ca_paths


def add(isamAppliance, client_realm, server_realm, intermediate_realm, check_mode=False, force=False):
    """
    Add a client realm entry property
    """
    if ca_paths.search(isamAppliance, client_realm) == {}:
        return isamAppliance.create_return_object(
            warnings="Client Realm {0} not found, skipping add property: {1}.".format(client_realm, server_realm))

    ret_obj = ca_paths.get(isamAppliance, client_realm, check_mode=False, force=False)
    warnings = ret_obj["warnings"]

    found_server_realm = any(
        obj['name'] == server_realm for obj in ret_obj['data']
    )

    if force is True and check_mode is not True and found_server_realm:
        return isamAppliance.invoke_put(
            "Update a specified client realm property ",
            "{0}/{1}/{2}".format(uri, client_realm, server_realm),
            {"id": "capaths/{0}/{1}".format(client_realm, server_realm),
             "value": intermediate_realm}, requires_modules=requires_modules,
            requires_version=requires_version)
    elif (
        force is True
        and check_mode is not True
        or force is not True
        and not found_server_realm
        and check_mode is not True
    ):
        return isamAppliance.invoke_post(
            "Create an Kerberos Configuration Client realm entry property", "{0}/{1}".format(uri, client_realm),
            {
                "name": server_realm,
                "value": intermediate_realm
            }, requires_modules=requires_modules, requires_version=requires_version, warnings=warnings)

    elif force is True or not found_server_realm:
        return isamAppliance.create_return_object(changed=True, warnings=warnings)
    return isamAppliance.create_return_object(warnings=warnings)


def delete(isamAppliance, client_realm, server_realm, check_mode=False, force=False):
    """
    Delete an client realm entrie's particular property item
    """
    ret_obj = ca_paths.get(isamAppliance, client_realm, check_mode=check_mode, force=force)
    warnings = ret_obj["warnings"]

    if client_realm == {}:
        logger.info("Client Realm {0} not found, skipping delete.".format(client_realm))
    else:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True, warnings=warnings)
        # check if the server realm property to be deleted exists
        for obj in ret_obj['data']:
            if obj['name'] == server_realm:
                return isamAppliance.invoke_delete(
                    "Delete an Kerberos Configuration Client Realm entries Property",
                    "{0}/{1}/{2}".format(uri, client_realm, server_realm), requires_modules=requires_modules,
                    requires_version=requires_version, warnings=warnings)

    return isamAppliance.create_return_object(warnings=warnings)


def update(isamAppliance, client_realm, server_realm, intermediate_realm, check_mode=False, force=False):
    """
    Update a specified Client Realm entry property, client_realm and server_realm passed in argument list needs to exist
    """
    if ca_paths.search(isamAppliance, client_realm) == {}:
        return isamAppliance.create_return_object(
            warnings="Client Realm {0} not found, skipping update.".format(client_realm))

    ret_obj = ca_paths.get(isamAppliance, client_realm)

    found_server_realm = any(
        obj['name'] == server_realm for obj in ret_obj['data']
    )

    if not found_server_realm:
        return isamAppliance.create_return_object(
            warnings="Server Realm {0} to be updated under client realm:{1} not found, skipping update.".format(
                server_realm, client_realm))

    int_realm = ca_paths.get(isamAppliance, "{0}/{1}".format(client_realm, server_realm))['data']
    needs_update = intermediate_realm != int_realm[0]
    if force is True or needs_update:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True)
        else:
            return isamAppliance.invoke_put(
                "Update a specified client realm property ",
                "{0}/{1}/{2}".format(uri, client_realm, server_realm),
                {"id": "capaths/{0}/{1}".format(client_realm, server_realm),
                 "value": intermediate_realm}, requires_modules=requires_modules,
                requires_version=requires_version)

    return isamAppliance.create_return_object()


def set(isamAppliance, client_realm, server_realm=None, intermediate_realm=None, check_mode=False, force=False):
    """
        Creating or Modifying an Kerberos Configuration client realm Property,
    """
    # check for an input of intermediate realm if server realm being set is not None

    if server_realm is not None and intermediate_realm is None:
        return isamAppliance.create_return_object(
            warnings="a non null Intermediate Realm needs to be passed as input, when Server realm :{0} is being set".format(
                server_realm))

    if ca_paths.search(isamAppliance, name=client_realm)['data'] == {}:
        return isamAppliance.create_return_object(
            warnings="Client_realm: {0}, does not exist".format(client_realm))
    logger.info("Client Realm {0} exists, requesting to update its property.".format(client_realm))
    ret_obj = ca_paths.get(isamAppliance, client_realm)
    found_server_realm = any(
        obj['name'] == server_realm for obj in ret_obj['data']
    )

    return (
        update(
            isamAppliance,
            client_realm,
            server_realm,
            intermediate_realm,
            check_mode=check_mode,
            force=force,
        )
        if found_server_realm
        else add(
            isamAppliance,
            client_realm,
            server_realm,
            intermediate_realm,
            check_mode=check_mode,
            force=force,
        )
    )
