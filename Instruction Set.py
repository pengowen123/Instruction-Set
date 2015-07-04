from mathbits import isnan

global memory
global temp
global functionReturn

def loadProgramFile(showMessages):

    global programs, programsRaw, memory

    print "Loading programs..."

    programLoad = open("programs.txt", "r")
    programList = programLoad.read()
    programsRaw = programLoad.read()
    programLoad.close()
    programs = []
    memory = [0 for x in range(1024)]
    if showMessages == True:
        try:
            print "Loading memory..."
            with open("memory.txt", "r") as mem:
                mem = mem.read().split("\n")
                for addr in range(len(mem)-1):
                    
                    memory[addr] = mem[addr][7:]
                    memory[addr] = int(memory[addr].replace(" ",""), 16)
        except:
            print "Failed to load memory from file"
            memory = [0 for x in range(1024)]

    try:
        if len(programList) > 0:
            programs = [[b for b in line.split(";") if ">" not in str(b)] for line in programList.split("//") if line[0] != "!"]
            for p in range(len(programs)):
                for l in range(len(programs[p])):
                    line_ = programs[p][l]
                    if "*" not in line_:
                        programs[p][l] = int(line_, 2)
        else:
            if showMessages == True:
                print "No programs were loaded"

    except Exception, e:
        for program in programList.split("//"):
            if type(program[0]) == int:
                noName = True
            else:
                noName = False
        if noName == True:
            if showMessages == True:
                print "One or more programs did not have a name"

    programsRaw = [p for p in programList.split("//")]

loadProgramFile(True)

temp = 0b0000
functionReturn = 0b0000
current = 0

def write_(paramType, address, data): # 0001
    global current
    memory[address] = data

    if memory[address] > 0:
        functionReturn = 0b0001
    else:
        functionReturn = 0b0000

def read_(paramType, address): # 0010
    global temp
    global current
    global functionReturn

    if paramType == 0b0000:
        temp = memory[address]
    else:
        temp = memory[memory[address]]

    if memory[address] == 0:
        functionReturn = 0b0000
    else:
        functionReturn = 0b0001

def writeFrom(address, address_2): # 0011
    global current
    if address == 0b0000:
        memory[address_2] = temp
    else:
        memory[address_2] = memory[address]

    if memory[address] > 0:
        functionReturn = 0b0001
    else:
        functionReturn = 0b0000

def toString(number):
    chars = bin(number)[2:]
    factor = 0
    
    while 8 * factor < len(chars):
        factor += 1

    chars = padding(int(chars,2),factor * 8)
        
    string = ""
    word = ""
        
    for x in range(len(chars)-1,1,-1):
        word += chars[x]
        if len(word) > 7:
            word = word[::-1]
            string += chr(int(word,2))
            word = ""

    return string[::-1]

def display(paramType, address): # 0100
    global current
    global temp
    global memory
    if paramType == 0b0000:
        print "Display: " + str(address)
    
    elif paramType == 0b0010:
        if memory[address] == 0:
            print "null"
        else:
            print toString(memory[address])

    elif paramType == 0b0011:
        response = raw_input("Input: ")
        current += 1
        if isnan(response) == False:
            temp = int(response)
        else:
            string = ""
            for char in response:
                string += padding(ord(char),8)[2:]
            temp = int(string,2)
    
    else:
        if address == 0b0000:
            print "Display (temp): " + str(temp)
        else:
            print "Display: " + str(memory[address])

        if memory[address] > 0:
            functionReturn = 0b0001
        else:
            functionReturn = 0b0000

def add_(paramType, address, address_2): # 0101
    global temp
    global current
    if paramType == 0b0000:
        result = memory[address] + address_2
    else:
        result = memory[address] + memory[address_2]
    temp = result

def subt_(paramType, address, address_2): # 1001
    global temp
    global current
    if paramType == 0b0000:
        result = memory[address] - address_2
    elif paramType == 0b0010:
        result = address - memory[address_2]
    else:
        result = memory[address] - memory[address_2]
    if result < 0:
        result = abs(result)
    temp = result

def div_(paramType, address, address_2): # 1010
    global temp
    global current
    if paramType == 0b0000:
        result = memory[address] / address_2
    elif paramType == 0b0010:
        try:
            result = address / memory[address_2]
        except:
            result = 0
    else:
        result = memory[address] / memory[address_2]
    temp = result

def mult_(paramType, address, address_2): # 1011
    global temp
    global current

    if paramType == 0b0000:
        result = memory[address] * address_2
    else:
        result = memory[address] * memory[address_2]
    temp = result

def greaterThan(paramType, address, address_2): # 0110
    global functionReturn
    global current

    if paramType == 0b0000:
        if memory[address] > address_2:
            functionReturn = 0b0001
        else:
            functionReturn = 0b0000
    else:
        if memory[address] > memory[address_2]:
            functionReturn = 0b0001
        else:
            functionReturn = 0b0000

def equalTo(paramType, address, address_2): # 1101
    global functionReturn
    if paramType == 0b0000:
        if memory[address] == address_2:
            functionReturn = 0b0001
        else:
            functionReturn = 0b0000
    else:
        if memory[address] == memory[address_2]:
            functionReturn = 0b0001
        else:
            functionReturn = 0b0000

def ifTrue(function): # 0111

    global program
    global current
    global functionReturn

    current += 1

    if function == greaterThan or function == 0b0110:
        function(program[current+1], program[current+2], program[current+3])
        if functionReturn == 0b0001:
            current += 4
            singleRun(program[current])
            current += linesToSkip(program[current])
            functionReturn = 0b0001
        else:
            current += 4
            current += linesToSkip(program[current])
            functionReturn = 0b0000

    elif function == equalTo or function == 0b1101:
        function(program[current+1], program[current+2], program[current+3])
        if functionReturn == 0b0001:
            current += 4
            singleRun(program[current])
            current += linesToSkip(program[current])
            functionReturn = 0b0001
        else:
            current += 4
            current += linesToSkip(program[current])
            functionReturn = 0b0000

    elif function == read_ or function == 0b0010:
        function(program[current+1], program[current+2])

        if functionReturn == 0b0001:
            current += 3
            singleRun(program[current])
            current += linesToSkip(program[current])
            functionReturn = 0b0001
        else:
            current += 3
            current += linesToSkip(program[current])
            functionReturn = 0b0000

    else:
        print "Error:"
        print "Invalid condition at function " + str(current)
        functionReturn = 0b0000

def userInput(): # 1100
    global current
    global functionReturn
    global temp

    response = raw_input("<Input> ")
    current += 1
    if isnan(response) == False:
        temp = int(response)
    else:
        string = ""
        for char in response:
            string += padding(ord(char),8)[2:]
        temp = int(string,2)

def singleRun(function):
    global current
    global functionReturn
    global program

    if True:
        if True:
            if function == 0b0001:
                    write_(program[current+1], program[current+2], program[current+3])
                    current += 4

            if function == 0b0010:
                    read_(program[current+1], program[current+2])
                    current += 3

            elif function == 0b0011:
                    writeFrom(program[current+1], program[current+2])
                    current += 3

            elif function == 0b0100:
                    display(program[current+1], program[current+2])
                    current += 3

            elif function == 0b0101:
                    add_(program[current+1], program[current+2], program[current+3])
                    current += 4

            elif function == 0b1001:
                    subt_(program[current+1], program[current+2], program[current+3])
                    current += 4

            elif function == 0b1010:
                    div_(program[current+1], program[current+2], program[current+3])
                    current += 4

            elif function == 0b1011:
                    mult_(program[current+1], program[current+2], program[current+3])
                    current += 4

            elif function == 0b0110:
                    greaterThan(program[current+1], program[current+2], program[current+3])
                    current += 4

            elif function == 0b1101:
                    equalTo(program[current+1], program[current+2], program[current+3])

            elif function == 0b0111:

                    if program[current+1] == 0b0110:
                            ifTrue(greaterThan)

                    elif program[current+1] == 0b0010:
                            ifTrue(read_)

                    elif program[current+1] == 0b1101:
                            ifTrue(equalTo)

                    else:
                         print "Error:"
                         print "Invalid condition at function " + str(current + 1)
                         print " "

            elif function == 0b1000:
                    run(program[current+1], program[current+2], False)

            elif function == 0b1100:
                    userInput()

def run(paramType, address, showMessages): # 1000
    global current
    global program
    global functionReturn

    if showMessages == True:
        if int(address) >= len(programs):
            print "Error:"
            print "Invalid address"
            print " "
        else:
            print " "
            print "Running program at address " + str(address)
            print "___________________________"
            print " "

    if paramType == 0b0000:
        program = programs[address]

    elif paramType == 0b0001:
        program = programs[memory[address]]

    current = 1

    while current < len(program):
        try:
            function = program[current]
            singleRun(function)
        except Exception, e:
            print "There was a problem while attempting to run your program, try the debugger"
            print "Last line being run: " + str(current)
            print " "
            menu("run")

    try:
        writeString = ""
        for addr in range(len(memory)-1):
            addrString = hex(addr)[2:]
            
            while len(addrString) < len("000"):
                addrString = "0" + addrString

            addrString = "0x" + addrString + ": "
            writeString += addrString
            
            binary = padding(memory[addr],128)
            
            binList = [binary[2:10], binary[10:18], binary[18:26], binary[26:34],
                       binary[34:42], binary[42:50], binary[50:58], binary[58:66],
                       binary[66:74], binary[74:82], binary[82:90], binary[90:98],
                       binary[98:106], binary[106:114], binary[114:122], binary[122:130]]

            if len(binary) > 130:
                binList.append(binary[130:])
            hexes = []
            
            for sec in binList:
                hexString = hex(int(sec,2))[2:]
                while len(hexString) < 2:
                    hexString = "0" + hexString
                hexes.append(hexString)

            if int("".join(hexes),16) != 0:
                writeString += " ".join(hexes)
            else:
                writeString += "0"
            writeString += "\n"

        doWrite = True
            
    except Exception, e:
        print "Failed to convert memory for storage"
        print e
        doWrite = False

    if doWrite == True:
        with open("memory.txt", "w") as mem:
            mem.write(writeString)
    
    print "Program end"
    print " "
    menu(None)



def menu(goTo):
    global programs, line, current, programsRaw

    if goTo == None:
        action = raw_input("Select an action (debug, run, create): ")

    elif goTo == "debug":
        action = "debug"

    elif goTo == "run":
        action = "run"

    elif goTo == "create":
        action = "create"

    if action == "debug":

        print " "
        for index in range(len(programs)):
            name = programs[index][0]
            newName = []
            for char in range(len(name)):
                if name[char:char+1] != "\n" and name[char-1:char] != "\n":
                    newName.append(name[char])
            newName = "".join(newName)
            if "*" in newName:
                newName = newName[1::]
            print "Index %s: %s" % (index, newName)
        print ""

        programToDebug = raw_input("Enter the index to debug: ")
        if programToDebug == "back":
            menu(None)
            return

        if int(programToDebug) > len(programs):
            print "That program doesn't exist"
            menu("debug")
            return
        try:
            debug(int(programToDebug))
        except Exception,e:
            print " "
            print "There was an error while attemtping to debug your program"
            print "Probably an incorrect number of parameters somwehere"
            print "Trying again..."
            print " "
            programs[int(programToDebug)].append(0)

            tries = 0

            while tries < 3:
                tries += 1
                try:
                    debug(int(programToDebug))
                    break
                except Exception,e:
                    print "Trying again..."
                    print " "
                    programs[int(programToDebug)].append(0)

            else:
                print "Failed to solve the issue"

    elif action == "run":

        print " "
        for index in range(len(programs)):
            name = programs[index][0]
            newName = []
            for char in range(len(name)):
                if name[char:char+1] != "\n" and name[char-1:char] != "\n":
                    newName.append(name[char])
            newName = "".join(newName)

            if "*" in newName:
                newName = newName[1:]

            rawProgram = programsRaw[index].split(";")
            editCount = ""

            if "> Edit" in rawProgram[1]:
                editCount = "(" + rawProgram[1][2:] + ")"

            print "Index %s: %s%s" % (index, newName, editCount)
        print ""

        programToRun = raw_input("Enter the index to run: ")
        if programToRun == "back":
            menu(None)
            return

        elif int(programToRun) > len(programs):
            print "That program doesn't exist"
            print " "
            menu("run")
            return

        run(0, int(programToRun), True)

    elif action == "create":
        print " "
        print "User-friendly program creation and editing"
        print "Type 'save' to save program, 'back' to delete last function, or 'cancel' to quit"
        print "Create functions by name, not id"
        print "Create 'type' parameters by id, not name"
        print " "

        for index in range(len(programs)):
            name = programs[index][0]
            newName = []
            for char in range(len(name)):
                if name[char:char+1] != "\n" and name[char-1:char] != "\n":
                    newName.append(name[char])
            newName = "".join(newName)

            if "*" in newName:
                newName = newName[1:]

            rawProgram = programsRaw[index].split(";")
            editCount = ""

            if "> Edit" in rawProgram[1]:
                editCount = "(" + rawProgram[1][2:] + ")"

            print "Index %s: %s%s" % (index, newName, editCount)
        print ""

        action2 = raw_input("Select an action (create, edit): ")
        if action2 == "back":
            menu(None)
            return
        elif action2 == "create":
            print " "
            print "New program (%s)" % (len(programs))
            print "-------------"
            programCreator(None)
        elif action2 == "edit":
            address = raw_input("Enter the address to edit: ")
            if address == "back":
                menu(None)
                return

            try:
                address = int(address)

            except Exception:
                print "That program doesn't exist"
                menu("create")
                return

            if address > len(programs)-1:
                print "That program doesn't exist"
                menu(None)
                return

            else:
                print " "
                print "Editing program " + str(address)
                print "------------------"
                programCreator(address)
        else:
            print "Invalid action"
            menu("create")
            return

    else:
        print "Invalid action"
        menu(None)
        return

def getFunctionName(function):

    if function == 0b0000:
        return "Blank"
    elif function == 0b0001:
        return "Write"
    elif function == 0b0010:
        return "Read"
    elif function == 0b0011:
        return "Write from"
    elif function == 0b0100:
        return "Display"
    elif function == 0b0101:
        return "Add"
    elif function == 0b0110:
        return "Greater than"
    elif function == 0b1001:
        return "Subtract"
    elif function == 0b1010:
        return "Divide"
    elif function == 0b1011:
        return "Multiply"
    elif function == 0b1000:
        return "Run program"
    elif function == 0b1100:
        return "User input"
    elif function == 0b1101:
        return "Equal to"
    elif function == 0b0111:
        return "If"

def linesToSkip(function):

    if function == 0b0001:
        return 4
    elif function == 0b0010:
        return 3
    elif function == 0b0011:
        return 3
    elif function == 0b0100:
        return 3
    elif function == 0b0101:
        return 4
    elif function == 0b0110:
        return 4
    elif function == 0b1001:
        return 4
    elif function == 0b1010:
        return 4
    elif function == 0b1011:
        return 4
    elif function == 0b1000:
        return 3
    elif function == 0b1100:
        return 1
    elif function == 0b1101:
        return 4

def debug(address):

    global line
    line = 1
    debugProgram = programs[address]

    error = 0

    print " "
    print "Checking program at address " + str(address)
    print "------------------------------"

    while line < len(debugProgram):
        if debugProgram[line] == 0b0000:
            print "Found blank function at function " + str(line) + ", probably mixed up with a parameter"
            error = 1
            break
        elif debugProgram[line] == 0b0001:
            print "Function " + str(line) + ":" + " Write"
            print " "
            line += 4

        elif debugProgram[line] == 0b0010:
            print "Function " + str(line) + ":" + " Read"
            print " "
            line += 3

        elif debugProgram[line] == 0b0011:
            print "Function " + str(line) + ":" + " Write from"
            print " "
            line += 3

        elif debugProgram[line] == 0b0100:
            print "Function " + str(line) + ":" + " Display"
            print " "
            if debugProgram[line+1] != 0b0000 and debugProgram[line+1] != 0b0001 and debugProgram[line+1] != 0b0010 and debugProgram[line+1] != 0b0011:
                print "Invalid parameter type at function " + str(line)
                error = 1
                break
            line += 3

        elif debugProgram[line] == 0b0101:
            print "Function " + str(line) + ":" + " Add"
            print " "
            if debugProgram[line+1] != 0b0000 and debugProgram[line+1] != 0b0001:
                print "Invalid parameter type at function " + str(line)
                error = 1
                break
            line += 4

        elif debugProgram[line] == 0b0110:
            print "Function " + str(line) + ":" + " Greater than"
            print " "
            if debugProgram[line+1] != 0b0000 and debugProgram[line+1] != 0b0001:
                print "Invalid parameter type at function " + str(line)
                error = 1
                break
            line += 4

        elif debugProgram[line] == 0b0111:

            print "Function " + str(line) + ":" +  " If:",

            if debugProgram[line+1] == 0b0010:
                print "read "

            elif debugProgram[line+1] == 0b0110:
                line += 1
                print "greater than "

            elif debugProgram[line+1] == 0b1101:
                line += 1
                print "equal to "

            else:
                print "Invalid comparator at function " + str(line+1)
                error = 1
                break


            if debugProgram[line+4] == 0b0001:

                print "If true: Write "
                print "If false:",
                print getFunctionName(debugProgram[line+8])
                line += 8
                line += linesToSkip(debugProgram[line])

            elif debugProgram[line+4] == 0b0010:

                print "If true: Read"
                print "If false:",
                print getFunctionName(debugProgram[line+7])
                line += 7
                line += linesToSkip(debugProgram[line])

            elif debugProgram[line+4] == 0b0011:

                print "If true: Write from"
                print "If false:",
                print getFunctionName(debugProgram[line+7])
                line += 7
                line += linesToSkip(debugProgram[line])

            elif debugProgram[line+4] == 0b0100:

                print "If true: Display"
                print "If false:",
                print getFunctionName(debugProgram[line+7])
                line += 7
                line += linesToSkip(debugProgram[line])

            elif debugProgram[line+4] == 0b0101:

                print "If true: Add"
                print "If false:",
                print getFunctionName(debugProgram[line+8])
                line += 8
                line += linesToSkip(debugProgram[line])

            elif debugProgram[line+4] == 0b1001:

                print "If true: Subtract"
                print "If false:",
                print getFunctionName(debugProgram[line+8])
                line += 8
                line += linesToSkip(debugProgram[line])

            elif debugProgram[line+4] == 0b1010:

                print "If true: Divide"
                print "If false:",
                print getFunctionName(debugProgram[line+8])
                line += 8
                line += linesToSkip(debugProgram[line])

            elif debugProgram[line+4] == 0b1011:

                print "If true: Multiply"
                print "If false:",
                print getFunctionName(debugProgram[line+8])
                line += 8
                line += linesToSkip(debugProgram[line])

            elif debugProgram[line+4] == 0b1000:

                print "If true: Run program"
                print "If false:",
                print getFunctionName(debugProgram[line+7])
                line += 7
                line += linesToSkip(debugProgram[line])

            elif debugProgram[line+4] == 0b1100:

                print "If true: User input"
                print "If false:",
                print getFunctionName(debugProgram[line+6])
                line += 6
                line += linesToSkip(debugProgram[line])

            else:
                print "Invalid function at line " + str(line+4)
                error = 1
                break

            print " "


        elif debugProgram[line] == 0b1000:
            print "Function " + str(line) + ":" + " Run program"
            print " "
            line += 3

        elif debugProgram[line] == 0b1001:
            print "Function " + str(line) + ":" + " Subtract"
            print " "
            if debugProgram[line+1] != 0b0000 and debugProgram[line+1] != 0b0001:
                print "Invalid parameter type at function " + str(line+1)
                error = 1
                break
            line += 4

        elif debugProgram[line] == 0b1010:
            print "Function " + str(line) + ":" + " Divide"
            print " "
            if debugProgram[line+1] != 0b0000 and debugProgram[line+1] != 0b0001:
                print "Invalid parameter type at function " + str(line+1)
                error = 1
                break
            line += 4

        elif debugProgram[line] == 0b1011:
            print "Function " + str(line) + ":" + " Multiply"
            print " "
            if debugProgram[line+1] != 0b0000 and debugProgram[line+1] != 0b0001:
                print "Invalid parameter type at function " + str(line+1)
                error = 1
                break
            line += 4

        elif debugProgram[line] == 0b1100:
            print "Function " + str(line) + ":" + " User input"
            print " "
            line += 1

        elif debugProgram[line] == 0b1101:
            print "Function " + str(line) + ":" + " Equal to"
            print " "
            if debugProgram[line+1] != 0b0000 and debugProgram[line+1] != 0b0001:
                print "Invalid parameter type at function " + str(line+1)
                error = 1
                break
            line += 4

        else:
            print "Invalid function at line " + str(line+1)
            error = 1
            break

    print " "
    print "Done checking program:"
    if error == 0:
        print "Program should run without errors, this does not mean it will function as"
        print "expected"
    else:
        print "Errors found"
    print " "
    print "------------------------------"
    print " "

    menu(None)

def collectInfo(msg):

    newFunction = raw_input(msg)

    if newFunction == "write":
        param1 = raw_input("Type: ")
        param2 = raw_input("Address: ")
        param3 = raw_input("Data: ")
        return [1, param1, param2, param3]

    elif newFunction == "read":
        param1 = raw_input("Type: ")
        param2 = raw_input("Address: ")
        return [2, param1, param2]

    elif newFunction == "writefrom":
        param1 = raw_input("Address: ")
        param2 = raw_input("Address 2: ")
        return [3, param1, param2]

    elif newFunction == "display":
        param1 = raw_input("Type: ")
        param2 = raw_input("Data/Address: ")
        return [4, param1, param2]

    elif newFunction == "add":
        param1 = raw_input("Type: ")
        param2 = raw_input("Address: ")
        param3 = raw_input("Data/Address 2: ")
        return [5, param1, param2, param3]

    elif newFunction == "subtract":
        param1 = raw_input("Type: ")
        param2 = raw_input("Address: ")
        param3 = raw_input("Data/Address 2: ")
        return [9, param1, param2, param3]

    elif newFunction == "divide":
        param1 = raw_input("Type: ")
        param2 = raw_input("Address: ")
        param3 = raw_input("Data/Address 2: ")
        return [10, param1, param2, param3]

    elif newFunction == "multiply":
        param1 = raw_input("Type: ")
        param2 = raw_input("Address: ")
        param3 = raw_input("Data/Address 2: ")
        return [11, param1, param2, param3]

    elif newFunction == "greaterthan":
        param1 = raw_input("Type: ")
        param2 = raw_input("Address: ")
        param3 = raw_input("Data/Address 2: ")
        return [6, param1, param2, param3]

    elif newFunction == "run":
        param1 = raw_input("Address: ")
        return [8, 0, param1]

    elif newFunction == "equalto":
        param1 = raw_input("Type: ")
        param2 = raw_input("Address: ")
        param3 = raw_input("Data/Address 2: ")
        return [13, param1, param2, param3]

def padding(number, length):
    number = bin(number)
    number = number[2::]
    while len(number) < length:
        number = "0" + number
    return "0b" + number

def programCreator(edit):

    global programs, programsRaw

    newProgram = []
    editCount = 0

    if edit != None:
        newProgram = formatProgram(programs[edit])
        name = programs[edit][0]

        for program in programs:
            if program[0] == name:
                editCount += 1

        editCount = " " + str(editCount)

    done = False

    while done == False:

        newFunction = raw_input("New function: ")

        if newFunction.lower() == "write":
            param1 = raw_input("Type: ")
            param2 = raw_input("Address: ")
            param3 = raw_input("Data: ")
            newProgram.append([1, param1, param2, param3])

        elif newFunction.lower() == "read":
            param1 = raw_input("Type: ")
            param2 = raw_input("Address: ")
            newProgram.append([2, param1, param2])

        elif newFunction.lower() == "writefrom":
            param1 = raw_input("Address: ")
            param2 = raw_input("Address 2: ")
            newProgram.append([3, param1, param2])

        elif newFunction.lower() == "display":
            param1 = raw_input("Type: ")
            param2 = raw_input("Data/Address: ")
            newProgram.append([4, param1, param2])

        elif newFunction.lower() == "add":
            param1 = raw_input("Type: ")
            param2 = raw_input("Address: ")
            param3 = raw_input("Data/Address 2: ")
            newProgram.append([5, param1, param2, param3])

        elif newFunction.lower() == "subtract":
            param1 = raw_input("Type: ")
            param2 = raw_input("Data/Address: ")
            param3 = raw_input("Data/Address 2: ")
            newProgram.append([9, param1, param2, param3])

        elif newFunction.lower() == "divide":
            param1 = raw_input("Type: ")
            param2 = raw_input("Data/Address: ")
            param3 = raw_input("Data/Address 2: ")
            newProgram.append([10, param1, param2, param3])

        elif newFunction.lower() == "multiply":
            param1 = raw_input("Type: ")
            param2 = raw_input("Address: ")
            param3 = raw_input("Data/Address 2: ")
            newProgram.append([11, param1, param2, param3])

        elif newFunction.lower() == "greaterthan":
            param1 = raw_input("Type: ")
            param2 = raw_input("Address: ")
            param3 = raw_input("Data/Address 2: ")
            newProgram.append([6, param1, param2, param3])

        elif newFunction.lower() == "run":
            param1 = raw_input("Address: ")
            newProgram.append([8, 0, param1])

        elif newFunction.lower() == "equalto":
            param1 = raw_input("Type: ")
            param2 = raw_input("Address: ")
            param3 = raw_input("Data/Address 2: ")
            newProgram.append([13, param1, param2, param3])

        elif newFunction.lower() == "userinput":
            newProgram.append([12])

        elif newFunction.lower() == "if":

            newIf = [7]

            condition = raw_input("Condition: ")

            if condition.lower() == "greaterthan":
                param1 = raw_input("Type: ")
                param2 = raw_input("Address: ")
                param3 = raw_input("Data/Address 2: ")
                paramList = [6, param1, param2, param3]

            elif condition.lower() == "equalto":
                param1 = raw_input("Type: ")
                param2 = raw_input("Address: ")
                param3 = raw_input("Data/Address 2: ")
                paramList = [13, param1, param2, param3]

            elif condition.lower() == "read":
                param1 = raw_input("Type: ")
                param2 = raw_input("Address: ")
                param3 = raw_input("Data/Address 2: ")
                paramList = [2, param1, param2, param3]

            iftrue = collectInfo("If true: ")
            iffalse = collectInfo("If false: ")

            for item in paramList:
                newIf.append(item)

            for item in iftrue:
                newIf.append(item)

            for item in iffalse:
                newIf.append(item)

            newProgram.append(newIf)

        elif newFunction == "save":
            done = True

            if edit == None:
                name = raw_input("Program name: ")
                name = "*" + name
            convertedProgram = [name]

            error = False

            print " "

            for function in range(len(newProgram)):
                print "Adding function %s/%s: %s" % (function+1, len(newProgram), getFunctionName(newProgram[function][0]))
                for parameter in newProgram[function]:

                    try:
                        paramInt = int(parameter)
                        paramInt = padding(paramInt, 4)
                        convertedProgram.append(paramInt)
                    except Exception:
                            error = True
                            print "Error when converting function %s, parameter: %s" % (function+1, newProgram[function].index(parameter))

            print " "
            print "Done!"
            print " "

            if error == False:
                print "Conversion successful, restart to load program"
            else:
                print "Conversion failed"

            convertedProgram = "; ".join(convertedProgram[1:])

            if editCount > 0:
                convertedProgram = "%s;> Edit%s; %s" % (name, editCount, convertedProgram)
            else:
                convertedProgram = "%s; %s" % (name, convertedProgram)

            convertedProgram = convertedProgram.replace("\n", "")

            if error == False:
                with open("programs.txt", "a") as saveNewProgram:
                    saveNewProgram.write("\n//\n" + convertedProgram)

            print " "
            menu(None)

        elif newFunction == "back":
            if len(newProgram) > 0:
                print "Deleted '%s' function" % (getFunctionName(newProgram[-1][0]))
                newProgram.pop(-1)
            else:
                print "There are no functions to delete"

        elif newFunction == "cancel":
            menu(None)
            break

        else:
            print "Invalid function"

        print " "

def formatProgram(program):

    program = program[1:]

    newProgram = []
    functionLine = 0

    while functionLine < range(len(program)):

        if not int(functionLine) < len(program):
            break

        function = program[functionLine]

        newFunction = []

        newFunction.append(int(function))

        if function in [1, 5, 6, 9, 10, 11, 13]:
            newFunction.append(program[functionLine+1])
            newFunction.append(program[functionLine+2])
            newFunction.append(program[functionLine+3])
            functionLine += 4

        elif function != 12 and function != 0:
            newFunction.append(program[functionLine+1])
            newFunction.append(program[functionLine+2])
            functionLine += 3

        else:
            functionLine += 1

        newProgram.append(newFunction)

    return newProgram

menu(None)
