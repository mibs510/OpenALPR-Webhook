import json
import time

import pycountry
from markupsafe import Markup


def datetime(epoch: int) -> str:
    """ Convert time. Example: 1655785225334 (epoch) => Sep 29 01:22:14 PM """
    return time.strftime('%b %d %Y %I:%M:%S %p', time.localtime(epoch / 1000))


def round_percentage(percent, symbol=True) -> str:
    """ Round a percentage to two decimal places. Example: 93.25465393 => 93.25% """
    if symbol:
        return "{}%".format(round(float(percent), 2))
    else:
        return "{}".format(round(float(percent), 2))


def direction(degree: float) -> str:
    degree = float(degree)
    """ Converts a degree (0-360) to a graphical direction icon in html. Example: 261.566467285156 => mdi-arrow-down"""
    class_tag = "mdi-help"

    if 0 <= degree <= 10 or 350 < degree <= 360:
        class_tag = "up"
    elif 10 < degree <= 80:
        class_tag = "top-right"
    elif 80 < degree <= 100:
        class_tag = "right"
    elif 100 < degree <= 170:
        class_tag = "bottom-right"
    elif 170 < degree <= 190:
        class_tag = "down"
    elif 190 < degree <= 260:
        class_tag = "bottom-left"
    elif 260 < degree <= 280:
        class_tag = "left"
    elif 280 < degree <= 350:
        class_tag = "top-left"

    return class_tag


def country(iso3166: str) -> str:
    return "N/A" if iso3166 == "N/A" else pycountry.subdivisions.get(code=iso3166).name


def get_flag_uri(iso3166: str) -> str:
    uri = "/img/flags"
    iso3166 = str(iso3166)

    if iso3166.split("-")[0] == 'us':
        return uri + "/us/" + iso3166.split("-")[1] + ".svg"
    else:
        return uri + "/4x3/" + iso3166.split("-")[0] + ".svg"


# Thanks to rtaft @stackoverflow.com
# https://stackoverflow.com/a/45846841
def human_format(num: int) -> str:
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


# Thanks to @hostingutilities.com at stackoverflow.com
# https://stackoverflow.com/a/43750422
def human_size(bytes: int, units=[' bytes','KB','MB','GB','TB', 'PB', 'EB']) -> str:
    """ Returns a human readable string representation of bytes """
    return str(bytes) + units[0] if bytes < 1024 else human_size(bytes >> 10, units[1:])


def get_negative_mtm_svg_html_arrow() -> Markup:
    return Markup('<svg class="icon icon-xs text-danger" fill="currentColor" viewBox="0 0 20 20" '
                  'xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" '
                  'd="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 '
                  '0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>')


def get_positive_mtm_svg_html_arrow() -> Markup:
    return Markup('<svg class="icon icon-xs text-success" fill="currentColor" viewBox="0 0 20 20" '
                  'xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" '
                  'd="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 '
                  '0l4 4a1 1 0 010 1.414z" clip-rule="evenodd"></path></svg>')


def name(ugly_name: str) -> str:
    stage1 = ugly_name.replace("_", " ").replace("-", " ")
    words = stage1.split(" ")
    stage2 = ""
    i = 0
    for word in words:
        if word.__len__() <= 3 and word != "yes" and word != "no":
            stage2 += word.upper() + " "
        else:
            stage2 += word.capitalize() + " "
    return stage2.rstrip()


def print_json(json_obj: str) -> None:
    print(json.dumps(json_obj, ensure_ascii=False, indent=4))
