import cv2
import json

# steps = json.loads(open('steps.json').read())
eles = json.loads(open('test.json', encoding = 'utf-8').read())
# step_1 = steps['steps'][0]
# step_2 = steps['steps'][1]

img_1 = cv2.imread("step-1127102651.jpg")
# img_1_rec = cv2.rectangle(img_1, (int(step_1['x']) - 30, int(step_1['y']) + 30), (int(step_1['x'] + 30), int(step_1['y']) - 30), (255,0,0),2)
# x = int(int(step_1['x']))
# y = int(int(step_1['y']))
# print(f"{x}, {y}")

# img_2 = cv2.imread(step_2['screenshot_name'])
# img_1_rec = cv2.rectangle(img_1, (int(step_1['x']) - 30, int(step_1['y']) + 30), (int(step_1['x'] + 30), int(step_1['y']) - 30), (255,0,0),2)
# x = int(int(step_2['x']) * 3.34)
# y = int(int(step_2['y']) * 3.34)
#
# x = int(step_2['x'])
# y = int(step_2['y'])

# x = 850
# y = 900
#
# img_1_rec = cv2.circle(img_1, (211, 590), 20, (0,255,0), 5)
ratio = 2.4
#
for i in eles['ele_pairs']:
    ele = i['ele_1']
    col_min = int(ele['col_min'] * ratio)
    col_max = int(ele['col_max'] * ratio)
    row_min = int(ele['row_min'] * ratio)
    row_max = int(ele['row_max'] * ratio)
    if ele['category'] == 'Compo':
        cv2.rectangle(img_1, (col_min, row_min), (col_max, row_max), (255,0,0),2)
    else:
        cv2.rectangle(img_1, (col_min, row_min), (col_max, row_max), (0, 255, 0), 2)

frame = img_1
frame = cv2.resize(img_1, (348, 618), interpolation=cv2.INTER_CUBIC)

cv2.imshow("", frame)
cv2.waitKey(0)