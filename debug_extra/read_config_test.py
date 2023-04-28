with open('configDevice.txt') as mycfgfile:
    config = mycfgfile.read().splitlines()
    config.pop(0)
    

print(config)