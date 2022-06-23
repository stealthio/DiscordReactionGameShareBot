# Discord Reaction GameShare Bot

A bot that sends a message with reactions to a configurable channel. Each reaction is mapped to a configurable virtual XBox360 controller, this allows local multiplayer using Discord reactions and screen sharing.

![grafik](https://user-images.githubusercontent.com/20127926/175168716-53eae76e-9e2c-4a13-afe6-db1d0cd509e4.png)

Each reaction is mapped in a JSON to any amount of controller inputs to allow complex interactions.
```
"⏫": {
    "commands" : ["a", "wait_medium", "a"],
    "duration" : 0.5
},
```
Take a look at the included JSON files for reference.

Currently the following commands are implemented:

**Left Analogue Stick**
- left_stick_left
- left_stick_right
- left_stick_up
- left_stick_down
- left_stick_up_left
- left_stick_up_right
- left_stick_down_left
- left_stick_down_right

**Right Analogue Stick**
- right_stick_left
- right_stick_right
- right_stick_up
- right_stick_down
- right_stick_up_left
- right_stick_up_right
- right_stick_down_left
- right_stick_down_right

**Buttons**
- a
- b
- x
- y
- lb
- rb
- lt
- rt

**Misc**
- wait_short
- wait_medium

Uses [vgamepad](https://github.com/yannbouteiller/vgamepad)
