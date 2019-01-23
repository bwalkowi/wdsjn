from copy import deepcopy
from functools import lru_cache


class Device:
    def __init__(self, name, desc):
        self.name = name
        self.states = desc['states']
        self.state = desc['default']
        self.commands = desc['commands']

    def __str__(self):
        return '\n        {}: {}'.format(self.name, self.state)

    def set_state(self, new_state):
        self.state = new_state


class Room:
    def __init__(self, name, desc, devices):
        self.name = name
        self.devices = {dev_name: deepcopy(devices[dev_name]) 
                        for dev_name in desc['devices']}

    def __str__(self):
        devices = ''.join(str(dev) for dev in self.devices.values())
        return '\n    {}:'.format(self.name) + devices

    def match_command(self, tokens):
        possible_matches = []
        for dev in self.devices.values():
            for cmd, new_state in dev.commands.items():
                cmd_tokens = cmd.split() + [self.name]
                if len(cmd_tokens) == len(tokens):
                    total_dist = 0
                    for token1, token2 in zip(cmd_tokens, tokens):
                        dist = levenshtein_dist(token1, token2)
                        if dist > 3:
                            break
                        total_dist += dist
                    else:
                        possible_matches.append((total_dist, cmd + ' w ' + self.name,
                                                 lambda d=dev, ns=new_state: d.set_state(ns)))
        return possible_matches


class Home:
    def __init__(self, desc):
        self.devices = {device_name: Device(device_name, device_desc) 
                        for device_name, device_desc in desc['devices'].items()}
        self.rooms = {room_name: Room(room_name, room_desc, self.devices)
                      for room_name, room_desc in desc['rooms'].items()}

    def __str__(self):
        rooms = ''.join(str(room) for room in self.rooms.values())
        return '\nHome:' + rooms

    def match_command(self, tokens):
        possible_matches = []
        for room in self.rooms.values():
            possible_matches.extend(room.match_command(tokens))
        possible_matches.sort(key=lambda x: x[0])
        return possible_matches


@lru_cache(maxsize=2**16)
def levenshtein_dist(a, b):
    if a == '':
        return len(b)
    elif b == '':
        return len(a)
    else:
        cost = 0 if a[-1] == b[-1] else 1
       
        return min(levenshtein_dist(a[:-1], b) + 1, 
                   levenshtein_dist(a, b[:-1]) + 1, 
                   levenshtein_dist(a[:-1], b[:-1]) + cost)
