# Robot Controller

This is a framework designed as a GUI controller for uarm robot arms and internet cameras.

## Requirements

* python3
* other packages

```python
pip install logzero \
    PIL \
    threading \
    opencv-python
```

## How to use

#### Run controller panel

```python
python3 camera_control_tk.py
```

After you run the script `camera_control_tk.py`, you will see the controller panel:

!()[tmp.jpg]

#### Buttons on the panel
* Record. The `Record` button can control the start and the end of your record. To start recording, just click this button once. After you start recording, your behaviors on the streaming panel will be recorded. To end record, you need to click this button again. After you end recording, the step information will be saved in the following format in `steps.json` file.
```json
{
  "steps": [
    {
      "action": "Click", // the action of your operation
      "x": 254, // x coordinate in the streaming panel
      "y": 580, // y coordinate in the streaming panel
      "x_fix": 215, // x coordinate for the uarm arms
      "y_fix": 15, // y coordinate for the uarm arms
      "screenshot_name": "step-1127102651.jpg" // name of corresponding screenshot
    }
  ]
}
```
**Note**: After you start recording, the screenshot of streaming panel will be saved each time you start an operation. 
* Replay. The `Replay` button is for guiding robot arms to replay the previously recorded steps. However, due to some disclosure issues, we don't have plans to open our replay code. You can try your own replay service with replacing the address of replay service at line 51 in file `utils.py`. The format of replaying request is listed in the following:
```json
{
  "figure1": base64_figure_1, // The recorded screenshot
  "figure2": base64_figure_2  // The screenshot in replaying
}
```
* Reset. Reset all recorded steps. This button is now **deprecated**.
* Reload. Reload the calibration configurations. 

#### Calibration

