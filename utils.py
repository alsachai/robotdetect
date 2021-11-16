import requests
from logzero import logger
import base64
import cv2
import numpy as np
import json

replay_config = {
    "left_bottom": [300, 0],
    "right_top": [150, 65],
    "screen_left_bottom": [39, 633],
    "screen_right_top": [282, 38],
    "offset": 5
}

def coordinate_fix(x, y, config):
    left_bottom = config['left_bottom']
    right_top = config['right_top']
    screen_left_bottom = config['screen_left_bottom']
    screen_right_top = config['screen_right_top']
    offset = config['offset']

    left_padding = screen_left_bottom[0]
    top_padding = screen_right_top[1]
    true_screen_length = left_bottom[0] - right_top[0]
    true_screen_width = right_top[1] - left_bottom[1]
    screen_length = screen_left_bottom[1] - screen_right_top[1]
    screen_width = screen_right_top[0] - screen_left_bottom[0]
    x_coor = right_top[0] + int(((y - top_padding) / screen_length) * true_screen_length)  # x_coor from 150 to 300
    y_coor = int(((x - left_padding) / screen_width) * true_screen_width)  # y_coor from 0 to 65
    return x_coor - offset, y_coor - offset

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

def search_contain_box(x, y, pairs, img_path):
    logger.debug(pairs)
    ratio = 2.88
    pairs = json.loads(pairs)['ele_pairs']
    logger.debug(f"{x} {y}")
    img1 = cv2.imread(img_path)
    for pair in pairs:
        ele = pair['ele_1']
        if ele['category'] == 'Compo':
            col_min = int(ele['col_min'] * ratio)
            col_max = int(ele['col_max'] * ratio)
            row_min = int(ele['row_min'] * ratio)
            row_max = int(ele['row_max'] * ratio)
            cv2.rectangle(img1, (col_min, row_min), (col_max, row_max), (255, 0, 0), 4)
            if x >= col_min and x <= col_max and y <= row_max and y >= row_min:
                logger.debug('find pair')
                ele_2 = pair['ele_2']
                x_min, x_max, y_min, y_max = ele_2['col_min'], ele_2['col_max'], ele['row_min'], ele['row_max']
                return int((x_min + x_max)/2), int((y_min + y_max)/2)
    cv2.imwrite(img_path + ".png", img1)
    logger.debug('pair not found')