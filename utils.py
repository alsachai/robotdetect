import requests
from logzero import logger
import base64
import cv2
import numpy as np
import json
import logzero
log_format = '%(color)s[%(levelname)1.1s %(module)s:%(lineno)d]%(end_color)s %(message)s'
formatter = logzero.LogFormatter(fmt=log_format)
logzero.setup_default_logger(formatter=formatter)

SAVED_SCREENSHOT_RESO = [1920,1080]

def coordinate_fix(x, y, config):
    left_top = config['left_top']
    right_bottom = config['right_bottom']
    screen_left_top = config['screen_left_top']
    screen_right_bottom = config['screen_right_bottom']
    offset = config['offset']

    left_padding = screen_left_top[0]
    top_padding = screen_left_top[1]
    true_screen_length = right_bottom[0] - left_top[0]
    true_screen_width = right_bottom[1] - left_top[1]
    screen_length = screen_right_bottom[1] - screen_left_top[1]
    screen_width = screen_right_bottom[0] - screen_left_top[0]

    x_coor = left_top[0] + int(((y - top_padding) / screen_length) * true_screen_length)  # x_coor from 150 to 300
    y_coor = left_top[1] + int(((x - left_padding) / screen_width) * true_screen_width)  # y_coor from 0 to 65
    return x_coor - offset, y_coor - offset

def replay_coordinate_fix(x, y):

    x_full_screen = int(x*2.4)
    y_full_screen = int(y*2.4)
    decrease_ratio = round((1920/618), 4)
    new_x = int(x_full_screen / decrease_ratio)
    new_y = int(y_full_screen / decrease_ratio)
    return new_x, new_y

def base64_encode(figure_path):
    if isinstance(figure_path, np.ndarray):
        # figure = cv2.fromarray(figure_path)
        figure = np.ascontiguousarray(figure_path)
        return base64.b64encode(figure).decode('utf8')
    with open(figure_path, "rb") as f:
        base64_figure = base64.b64encode(f.read()).decode('utf8')
        return base64_figure

def send_requests(base64_figure_1, base64_figure_2):
    post_url = "http://192.168.50.94:6785/guimatching"
    headers = {
        "Authorization": None,
        "Content-Type": "application/json"
    }

    form_data = json.dumps({
        "figure1": base64_figure_1,
        "figure2": base64_figure_2
    })

    # logger.debug("sending request")
    response = requests.post(url=post_url, headers=headers, data=form_data).text
    return response

def search_contain_box(x, y, raw_pairs, img_path):
    logger.debug(raw_pairs)
    pairs = json.loads(raw_pairs)['ele_pairs']
    ratio = json.loads(raw_pairs)['ratio']
    # ratio_2 = 900/618
    ratio_2 = 1.456
    img1 = cv2.imread(img_path)
    for pair in pairs:
        ele = pair['ele_1']
        cv2.circle(img1, (x, y), 20, (0, 255, 0), 5)
        if ele['category'] == 'Compo':
            logger.debug(f"before multi {x} {y} colmin: {ele['col_min']} colmax: {ele['col_max']} rowmin: {ele['row_min']} rowmax: {ele['row_max']}")
            col_min = int(ele['col_min'] * ratio)
            col_max = int(ele['col_max'] * ratio)
            row_min = int(ele['row_min'] * ratio)
            row_max = int(ele['row_max'] * ratio)
            if col_min == 0 or row_min == 0:
                logger.error("Coordinate Start From 0, Skip!")
                continue
            if int(ele['area']) > 100000:
                logger.error("Area Error, Skip!")
                continue
            cv2.rectangle(img1, (col_min, row_min), (col_max, row_max), (255, 0, 0), 4)
            logger.debug(f"after multi {x} {y} colmin: {col_min} colmax: {col_max} rowmin: {row_min} rowmax: {row_max}")
            if x >= col_min and x <= col_max and y <= row_max and y >= row_min:
                logger.debug('find pair')
                logger.debug("write image")
                ele_2 = pair['ele_2']
                x_min, x_max, y_min, y_max = ele_2['col_min'], ele_2['col_max'], ele_2['row_min'], ele_2['row_max']
                cv2.rectangle(img1, (x_min, y_min), (x_max, y_max), (0, 0, 255), 4)
                cv2.imwrite(img_path + ".png", img1)
                logger.debug(f"{x} {y} colmin: {ele_2['col_min']} colmax: {ele_2['col_max']} rowmin: {ele_2['row_min']} rowmax: {ele_2['row_max']}")
                return int((x_min + x_max)/2), int((y_min + y_max)/2)
            else:
                logger.error("pair miss")
    logger.debug("write image")
    cv2.imwrite(img_path + ".png", img1)
    # cv2.imwrite(img_path + ".png", img1)
    logger.debug('pair not found')