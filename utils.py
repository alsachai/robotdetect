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

SAVED_SCREENSHOT_RESO = [2340,1080]

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
    screen_length = screen_right_bottom[0] - screen_left_top[0]
    screen_width = screen_right_bottom[1] - screen_left_top[1]

    # x_coor = screen_left_top[0] + int(((x - left_padding) / screen_length) * true_screen_length)  # x_coor from 150 to 300
    # y_coor = screen_left_top[1] + int(((y - top_padding) / screen_width) * true_screen_width)  # y_coor from 0 to 65

    # screen ratio caculate
    x_coor = (abs(x-340)/344)*110 + 192
    y_coor = (y/508)*157-78
    print(x_coor, y_coor)
    return x_coor - offset, y_coor - offset

def replay_coordinate_fix(x, y):
    ratio = 2340/900
    x_full_screen = int(x*ratio)
    y_full_screen = int(y*ratio)
    x_ratio = round((1080/618), 4)
    y_ratio = round((2340/618), 4)
    new_x = int(x_full_screen / x_ratio)
    new_y = int(y_full_screen / y_ratio)
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
    post_url = "http://10.6.1.180:59785/guimatching"
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
    pairs = json.loads(raw_pairs)['ele_pairs']
    ratio = json.loads(raw_pairs)['ratio']
    # ratio_2 = 900/618
    ratio_2 = 1.456
    img1 = cv2.imread(img_path)
    img2 = cv2.imread("tmp.jpg")
    is_found = False
    rel_x = 0
    rel_y = 0
    for pair in pairs:
        ele = pair['ele_1']
        cv2.circle(img1, (int(x), int(y)), 20, (0, 255, 0), 5)
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
            if x >= col_min and x <= col_max and y <= row_max and y >= row_min and is_found is False:
                logger.debug('find pair')
                logger.debug(f"found pair:{pair}")
                logger.debug("write image")
                ele_2 = pair['ele_2']
                # cv2.rectangle(img2, (int(x_min * ratio), int(y_min * ratio)), (int(x_max * ratio), int(y_max * ratio)), (0, 0, 255), 4)
                x_min, x_max, y_min, y_max = ele_2['col_min'], ele_2['col_max'], ele_2['row_min'], ele_2['row_max']
                cv2.rectangle(img2, (int(x_min * ratio), int(y_min * ratio)), (int(x_max * ratio), int(y_max * ratio)), (0, 0, 255), 4)
                cv2.imwrite(img_path + "_2.png", img2)
                logger.debug(f"{x} {y} colmin: {ele_2['col_min']} colmax: {ele_2['col_max']} rowmin: {ele_2['row_min']} rowmax: {ele_2['row_max']}")
                rel_x = int((x_min + x_max)/2)
                rel_y = int((y_min + y_max)/2)
                is_found = True
            else:
                logger.warning("pair missing")
    
    cv2.imwrite(img_path + "_1.png", img1)
    if is_found:
        return rel_x, rel_y
    else:
        logger.debug('pair not found')