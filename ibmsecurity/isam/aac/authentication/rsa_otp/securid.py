import logging
from ibmsecurity.isam.aac.authentication.rsa_otp.all import get

logger = logging.getLogger(__name__)

uri = "/iam/access/v8/otp/config/rsa"
requires_modules = ["mga"]
requires_version = "8.0.0.0"


def import_file(isamAppliance, node, filename, check_mode=False, force=False):
    """
    Import securid file for a node

    """

    return (
        isamAppliance.create_return_object(changed=True)
        if check_mode is True
        else isamAppliance.invoke_post_files(
            "Import securid file for a node",
            "{0}/securid/{1}".format(uri, node),
            [
                {
                    'file_formfield': 'file',
                    'filename': filename,
                    'mimetype': 'application/file',
                }
            ],
            {},
            requires_modules=requires_modules,
            requires_version=requires_version,
        )
    )


def delete(isamAppliance, node, check_mode=False, force=False):
    """
    Delete the securid file from a node

    """

    ret_obj = get(isamAppliance)
    delete_required = any(
        obj['fileName'] == "securid" and 'importTimestamp' in obj
        for obj in ret_obj['data']
    )

    if force is True or delete_required:
        if check_mode is True:
            return isamAppliance.create_return_object(changed=True)
        else:

            return isamAppliance.invoke_delete(
                "Delete the securid file from a node",
                "{0}/securid/{1}".format(uri, node),
                requires_modules=requires_modules, requires_version=requires_version
            )

    return isamAppliance.create_return_object()
