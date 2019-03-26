from pathlib import Path
import json
import shutil
from re import sub, match, compile, MULTILINE
from glob import iglob
from settings import SimulationSettings
from fileutils import remove_directory, recursively_copy

def translate_to_simulation(codeString):
    """Replaces all of the functions from the regular <Enes100.h> library with the 
       functions from the <Enes100Simulation.h> and <TankSimulation.h> libraries"""
    codeString = sub(r'#include +<Enes100.h>', 
        '#include <Enes100Simulation.h>\n#include <TankSimulation.h>',
        codeString)
    codeString = sub(r'void +setup\( *\) *{', 
        'void setup() {\n\tTankSimulation.begin();',
        codeString)
    codeString = sub(r'\.begin\(.*?\)',
        '.begin()',
        codeString)
    codeString = sub(r'ping\( *\)',
        'updateLocation()',
        codeString)
    codeString = sub(r'mission\((.+)\);',
        r'print("MISSION VALUE: ");\nEnes100Simulation.println(\1);',
        codeString)
    codeString = sub(r'Enes100\.',
        'Enes100Simulation.',
        codeString)
    codeString = replace_configured_functions(codeString)
    return codeString

def replace_configured_functions(codeString):
    """Replaces all of the user defined functions with their equivalents in 
       the functionNameReplacements object"""
    for simulationFunctionName, functionInfo in SETTINGS.get('functionNameReplacements').items():
        codeString = delete_definition(functionInfo, codeString)
        functionName = functionInfo.split(' ')[1]
        codeString = replace_calls(functionName, simulationFunctionName, codeString)

    return codeString

def delete_definition(functionPrototype, codeString):
    """Deletes the function definition for the provided function"""
    functionDefinitionRegex = compile(functionPrototype + r' *\(.*\) *\{(.|\n)*?\}', MULTILINE)  
    return sub(functionDefinitionRegex,
        '',
        codeString)

def replace_calls(functionName, simulationFunctionName, codeString):
    """Replaces all calls of the given function with the associated function 
       name in the simulation libraries."""
    # Replace all function calls with the simulation function name
    if 'readDistanceSensor' in simulationFunctionName:
        # Handle any function that is an alias for a distance sensor reading
        pinNumber = simulationFunctionName[-1]
        simulationFunctionName = 'Enes100Simulation.' + simulationFunctionName[:-1]
        functionName = compile(fr'{functionName} *\(.*\)')
        codeString = sub(functionName,
            simulationFunctionName + f'({pinNumber})',
            codeString)
    else:
        codeString = sub(functionName,
            'TankSimulation.' + simulationFunctionName,
            codeString)
    
    return codeString

def rename_src_file(sourceFileName, simulationDir):
    """Attempts to rename the main '.ino' source file to 'OSVSimulation.ino' in 
       the simulation directory. This is required in order for the Arduino IDE to 
       compile the simulation file."""
    shutil.move(simulationDir / sourceFileName,
                simulationDir / 'OSVSimulation.ino')

def setup_simulation_directory():
    """Copy every .ino file from the current directory into a new directory
       (called 'OSVSimulation/') in the parent folder"""
    PATH_TO_SOURCE_FILE = Path(SETTINGS.get('pathToSourceFile'))
    simulationDir = PATH_TO_SOURCE_FILE.parent / '../OSVSimulation'
    recursively_copy(PATH_TO_SOURCE_FILE.parent, simulationDir)
    rename_src_file(PATH_TO_SOURCE_FILE.name, simulationDir)

    return simulationDir

# Get the settings from the JSON file, and make sure that they're correct
SETTINGS = SimulationSettings('simulation-settings.json')
simulationDir = setup_simulation_directory()

# Go through every file in the current directory
for codeFile in iglob(str(simulationDir / '*.ino')):
    # Replace the Enes100.h functions with the simulation's functions
    with open(codeFile, 'r+') as code:
        codeString = code.read()
        code.seek(0) # Go to the beginning of the file
        code.write(translate_to_simulation(codeString))

print(f'\nSuccessfully translated all of your OSV code into the directory {simulationDir.resolve()}')