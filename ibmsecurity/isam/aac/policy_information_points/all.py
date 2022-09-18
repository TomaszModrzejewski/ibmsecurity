import logging
from ibmsecurity.utilities import tools

logger = logging.getLogger(__name__)

# URI for this module
uri = "/iam/access/v8/pips"
requires_modules = ["mga"]
requires_version = None


def get_all(isamAppliance, filter=None, sortBy=None, check_mode=False, force=False):
    """
    Retrieve a list of Policy Information Points (PIPs)

    """
    return isamAppliance.invoke_get("Retrieve a list of policy information points (pips)",
                                    "{0}/{1}".format(uri, tools.create_query_string(filter=filter, sortBy=sortBy)),
                                    requires_modules=requires_modules, requires_version=requires_version)


def get(isamAppliance, name=None, check_mode=False, force=False):
    """
    Retrieve a specific Policy Information Point by name

    """
    ret_obj = search(isamAppliance, name, check_mode=False, force=False)
    id = ret_obj['data']

    if id != {}:
        return _get(isamAppliance, id)
    logger.info("PIP '{0}' had no match, skipping retrieval.".format(name))
    warnings = ["PIP '{0}' had no match, skipping retrieval.".format(name)]
    return isamAppliance.create_return_object(warnings=warnings)


def delete(isamAppliance, name=None, check_mode=False, force=False):
    """
    Delete a policy information point

    """
    ret_obj = search(isamAppliance, name, check_mode=False, force=False)
    id = ret_obj['data']

    if force is True or id != {}:
        return (
            isamAppliance.create_return_object(changed=True)
            if check_mode is True
            else isamAppliance.invoke_delete(
                "Delete a policy information point",
                "{0}/{1}".format(uri, id),
                requires_modules=requires_modules,
                requires_version=requires_version,
            )
        )

    logger.info("PIP '{0}' does not exists, skipping delete.".format(name))
    return isamAppliance.create_return_object()


def compare(isamAppliance1, isamAppliance2):
    """
    Compare access policies between two appliances
    """
    ret_obj1 = get_all(isamAppliance1)
    ret_obj2 = get_all(isamAppliance2)

    for obj in ret_obj1['data']:
        del obj['id']
    for obj in ret_obj2['data']:
        del obj['id']

    return tools.json_compare(ret_obj1, ret_obj2, deleted_keys=['id'])


def search(isamAppliance, name, force=False, check_mode=False):
    """
    Retrieve ID for named PIP
    """
    ret_obj = get_all(isamAppliance)

    ret_obj_new = isamAppliance.create_return_object()

    for obj in ret_obj['data']:
        if obj['name'] == name:
            logger.info("Found Policy '{0}' id: '{1}'".format(name, obj['id']))
            ret_obj_new['data'] = obj['id']

    return ret_obj_new


def _get(isamAppliance, id):
    return isamAppliance.invoke_get("Retrieve a specific PIP",
                                    "{0}/{1}".format(uri, id))


def _create_json(name, properties, attributes, description, type):
    return {
        "name": name,
        "type": type,
        'attributes': attributes if attributes is not None else [],
        'description': description if description is not None else '',
        'properties': properties if properties is not None else [],
    }
