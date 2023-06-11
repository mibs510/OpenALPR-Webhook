import os


def get_camera_manufacturers() -> "[list]":
    """
    Get a list of camera manufacturers based from the objects found in
    apps/alpr/routes/settings/cameras/manufacturers/<manufacturer>.py
    :return: Returns a list of strings containing manufacturers.
    """
    manufacturers = []
    files = os.listdir("apps/alpr/routes/settings/cameras/manufacturers")

    # Remove non-manufacturers
    files.remove("__init__.py")
    files.remove("__pycache__")

    # Remove file extensions
    for file in files:
        file = file.split('.')
        manufacturers.append(file[0])

    return manufacturers
