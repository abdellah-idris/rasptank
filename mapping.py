CONTROLLER_ROBOT = {"00:E9:3A:68:C1:04": "DC:A6:32:BF:B2:82",
                    "D4:1B:81:3A:E1:AA": "DC:A6:32:BF:B2:4F",
                    "00:E9:3A:68:2F:0E": "DC:A6:32:BF:B2:19",
                    "00:E9:3A:68:2F:1C": "DC:A6:32:BF:B1:98",
                    "00:E9:3A:68:2F:26": "DC:A6:32:BF:B0:FF",
                    "00:E9:3A:68:C0:B4": "DC:A6:32:BF:91:CD"
                    }

# Inverting keys and values
ROBOT_CONTROLLER = {v: k for k, v in CONTROLLER_ROBOT.items()}
