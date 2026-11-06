def chooseMode(temp, occupied, previousMode):
    if not occupied:
        targetMode = "ECO"
    elif temp > 26:
        targetMode = "COOL"
    elif temp < 20:
        targetMode = "WARM"
    else:
        targetMode = "IDLE"

    if targetMode == previousMode:
        return targetMode, False
    return targetMode, True


sensorData = [(30, True), (30, True), (26, True), (20, True), (18, True), (18, False)]

previousMode = None


for temp, occupied in sensorData:
    targetMode, sendCommand = chooseMode(temp, occupied, previousMode)


    print("Mode before:", previousMode)
    print("Temperature:", temp, "| Room occupied:", occupied)
    print("Mode chosen:", targetMode)

    if sendCommand:
        print("Result: command sent")
    else:
        print("Result: same as before, no command")

    print('\n')
    previousMode = targetMode
