import logging
from io import open

logger = logging.getLogger(__name__)

# URI for this module
uri = "/core/licenses"
requires_modules = None
requires_version = None


def install(isamAppliance, license, check_mode=False, force=False):
    """
    install license in the appliance
    license should be the filename of the license file
    """
    file = {"license": open(license, 'rb')}

    if _check_license(isamAppliance, license) == True and force == False:
        return isamAppliance.create_return_object(warnings=["License already installed"])
    if _check_license(isamAppliance, license) != False and force != True:
        return isamAppliance.create_return_object()
    # create the request header for the post first
    headers = {
        "Accept": "text/html"
    }

    return (
        isamAppliance.create_return_object(changed=True)
        if check_mode
        else isamAppliance.invoke_request(
            "Applying license to appliance",
            method="post",
            uri=uri,
            requires_modules=requires_modules,
            requires_version=requires_version,
            warnings=[],
            headers=headers,
            files=file,
        )
    )


def get_all(isamAppliance, check_mode=False, force=False):
    """
    Retrieve all licenses installed in the appliance
    """
    return isamAppliance.invoke_get("Retrieve all licenses installed in the appliance",
                                    "{0}".format(uri), requires_modules=requires_modules,
                                    requires_version=requires_version)


def _check_license(isamAppliance, license):
    """
    check if a particular license file is installed in the appliance
    """

    ret_obj = get_all(isamAppliance)

    if ret_obj['data'] == {}:
        return False  # no license installed in the appliance

    from xml.etree import ElementTree

    with open(license, 'rt') as f:
        tree = ElementTree.parse(f)

    for path in ['.//OCN']:
        node = tree.find(path)
        if node is None:
            return False  # does not look like a valid input license file

        ocnnumber = node.text
        for item, value in ret_obj['data'].items():
            if 'ocn' in value and value['ocn'] == ocnnumber:
                return True
    return False


def compare(isamAppliance1, isamAppliance2):
    """
    Compare license installed between two appliances
    """
    ret_obj1 = get_all(isamAppliance1)
    ret_obj2 = get_all(isamAppliance2)

    import ibmsecurity.utilities.tools
    return ibmsecurity.utilities.tools.json_compare(ret_obj1, ret_obj2, deleted_keys=['serial_number'])
