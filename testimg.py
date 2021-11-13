import cv2
import json

steps = json.loads(open('steps.json').read())
step_1 = steps['steps'][0]
step_2 = steps['steps'][1]

img_1 = cv2.imread(step_1['screenshot_name'])
# img_1_rec = cv2.rectangle(img_1, (int(step_1['x']) - 30, int(step_1['y']) + 30), (int(step_1['x'] + 30), int(step_1['y']) - 30), (255,0,0),2)
x = int(int(step_1['x']) * 3.34)
y = int(int(step_1['y']) * 3.34)

img_2 = cv2.imread(step_2['screenshot_name'])
# img_1_rec = cv2.rectangle(img_1, (int(step_1['x']) - 30, int(step_1['y']) + 30), (int(step_1['x'] + 30), int(step_1['y']) - 30), (255,0,0),2)
x = int(int(step_2['x']) * 3.34)
y = int(int(step_2['y']) * 3.34)

img_2_rec = cv2.circle(img_2, (x, y), 20, (0,255,0), 5)

frame = cv2.resize(img_2_rec, (348, 696), interpolation=cv2.INTER_CUBIC)

cv2.imshow("", frame)
cv2.waitKey(0)