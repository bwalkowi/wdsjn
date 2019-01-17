from copy import deepcopy


class Device:
    def __init__(self, name, desc):
        self.name = name
        self.states = desc['states']
        self.state = desc['default']
        self.commands = desc['commands']

    def __str__(self):
        return '\n        {}: {}'.format(self.name, self.state)


class Room:
    def __init__(self, name, desc, devices):
        self.name = name
        self.devices = {dev_name: deepcopy(devices[dev_name]) 
                        for dev_name in desc['devices']}

    def __str__(self):
        devices = ''.join(str(dev) for dev in self.devices.values())
        return '\n    {}:'.format(self.name) + devices


class Home:
    def __init__(self, desc):
        self.devices = {device_name: Device(device_name, device_desc) 
                        for device_name, device_desc in desc['devices'].items()}
        self.rooms = {room_name: Room(room_name, room_desc, self.devices)
                      for room_name, room_desc in desc['rooms'].items()}

    def __str__(self):
        rooms = ''.join(str(room) for room in self.rooms.values())
        return '\nHome:' + rooms
