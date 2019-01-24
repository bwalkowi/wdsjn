# HOME ASSISTANT

![](tui.png?raw=true)

Project done for Introduction to Natural Language Semantics classes.

It simulates intelligent home assistant by translating voice commands into actual actions.

In order to enable more devices or rooms one need to modify `home.yaml`.

## Installing requirements:
```
pip install -r requirements.txt
```

## Running application
```
VL_PASSWD="<PASSWORD>" python -m main
```
Note that it is necessary to set password to VOICE LAB API as `VL_PASSWD` environment variable:
