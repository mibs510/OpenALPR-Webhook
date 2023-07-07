import logging
import time

import requests
from requests.auth import HTTPDigestAuth


class Dahua:
    label = ""
    id = ""
    proto = ""
    username = ""
    password = ""
    ip_hostname = ""
    port = ""
    focus = ""
    zoom = ""

    def __init__(self, label, id, username: str, password: str, ip_hostname: str, port, focus: str, zoom: str,
                 https=False):
        if https:
            self.proto = "https://"
        else:
            self.proto = "http://"  # noqa

        self.label = label
        self.id = id
        self.username = username
        self.password = password
        self.ip_hostname = ip_hostname
        self.port = str(port)
        self.focus = focus
        self.zoom = zoom

    def auto_focus(self) -> bool:
        """
        Forces the camera to focus automatically.
        :return: True if no exception raised.
        """

        try:
            url = self.proto + self.ip_hostname + ":" + self.port + "/cgi-bin/devVideoInput.cgi?action=autoFocus"
            response = requests.get(url, auth=HTTPDigestAuth(self.username, self.password))
            logging.debug("Camera {}/{} HTTP response status code: {}".format(self.label, self.id,
                                                                              response.status_code))
            if response.text == "OK\r\n":
                return True
            else:
                return False
        except Exception as ex:
            logging.exception(ex)
            raise ex

    def _convert_to_dict(self, text: str) -> dict:
        """
        Converts a return/new line string containing keys and values into a dictionary of strings.
        :param text: A return/new line string containing keys and values.
        :return: A dictionary of strings.
        """

        dictionary = {}
        new_lines = text.split('\n')
        new_lines.remove('')

        for line in new_lines:
            key_value = line.replace('\r', '')
            key_value = key_value.split('=')
            dictionary[key_value[0]] = key_value[1]

        return dictionary

    def _getFocusStatus(self) -> dict:
        """
        Calls getFocusStatus from the camera to get the following values: status.Focus, status.FocusMotorSteps,
        status.LenAdjustStatus, status.ResetResult, status.Status, status.Zoom, and status.ZoomMotorSteps
        :return: A dictionary containing the keys previously mentioned
        """
        try:
            url = self.proto + self.ip_hostname + ":" + self.port + "/cgi-bin/devVideoInput.cgi?action=getFocusStatus"
            return self._convert_to_dict(requests.get(url, auth=HTTPDigestAuth(self.username, self.password)).text)
        except Exception as ex:
            raise ex

    def get_focus_zoom_values(self) -> str:
        try:
            values = self._getFocusStatus()
            return "Focus: " + values['status.Focus'] + " Zoom: " + values['status.Zoom']
        except Exception as ex:
            raise ex

    def set_focus_and_zoom(self) -> bool:
        """
        Forces the camera to zoom and focus to the specified values by calling adjustFocus&focus=X&zoom=Y 5 times.
        autoFocus is not used because focusing at night with little to no reference points causes the camera to unfocus.
        :return: True if current focus & zoom match the specified focus & zoom values, else False.
        """

        try:
            values = self._getFocusStatus()
            # Return if it's already in focus and zoomed.
            if values['status.Focus'] == self.focus and values['status.Zoom'] == self.zoom:
                logging.debug("Camera {}/{} already focused and zoomed".format(self.label, self.id))
                return True

            url = self.proto + self.ip_hostname + ":" + self.port + \
                  "/cgi-bin/devVideoInput.cgi?action=adjustFocus&focus=" + self.focus + "&zoom=" + self.zoom
            try:
                for i in range(5):
                    response = requests.get(url, auth=HTTPDigestAuth(self.username, self.password))
                    time.sleep(1)
                    logging.debug("Camera {} (ID: {}) HTTP response status code: {}".format(self.label, self.id,
                                                                                      response.status_code))
            except Exception as ex:
                logging.exception(ex)

            # Check to see if it's focused and zoomed
            values = self._getFocusStatus()
            if values['status.Focus'] == self.focus and values['status.Zoom'] == self.zoom:
                return True
            else:
                logging.error("Could not set focus and zoom. focus={}, zoom={}, status.Focus={}, status.Zoom={}".
                              format(self.focus, self.zoom, values['status.Focus'], values['status.Zoom']))
                return False
        except Exception as ex:
            raise Exception(ex)
