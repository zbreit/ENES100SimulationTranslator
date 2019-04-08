from pathlib import Path
import json
import shutil
from re import sub, match, compile, MULTILINE
from glob import iglob
from settings import SimulationSettings
from fileutils import remove_directory, recursively_copy


def translate_to_simulation(inputCode):
    """Replaces all of the functions from the regular <Enes100.h> library with the
    functions from the <Enes100Simulation.h> and <TankSimulation.h> libraries"""
    inputCode = sub(r'#include +<Enes100.h>', 
                    '#include <Enes100Simulation.h>\n#include <TankSimulation.h>',
                    inputCode)
    inputCode = sub(r'void +setup\( *?\) *?\{', 
                    'void setup() {\n\tTankSimulation.begin();',
                    inputCode)
    inputCode = sub(r'Enes100.begin\(.*?\)',
                    'Enes100Simulation.begin()',
                    inputCode)
    inputCode = sub(r'ping\( *?\)',
                    'updateLocation()',
                    inputCode)
    inputCode = sub(r'mission\((.+?)\);',
                    r'print("MISSION VALUE: ");\nEnes100Simulation.println(\1);',
                    inputCode)
    inputCode = sub(r'Enes100\.',
                    'Enes100Simulation.',
                    inputCode)
    inputCode = replace_configured_functions(inputCode)
    return inputCode


def replace_configured_functions(inputCode):
    """Replaces all of the user defined functions with their equivalents in 
       the functionNameReplacements object"""
    for simulationFunctionName, functionInfo in SETTINGS.get('functionNameReplacements').items():
        inputCode = delete_definition(functionInfo, inputCode)
        functionName = functionInfo.split(' ')[-1]
        inputCode = replace_calls(functionName, simulationFunctionName, inputCode)

    return inputCode


def delete_definition(functionPrototype, inputCode):
    """Deletes the function definition for the provided function"""
    searchRegex = r'(\w+) (\w+\.)?(\w+)'
    replaceRegex = r'\1 \3'
    isStatic = '::' in functionPrototype
    if isStatic:
        searchRegex = r'(\w+) (\w+::\w+)'
        replaceRegex = r'\1 \2'
    
    functionPrototype = sub(searchRegex, replaceRegex, functionPrototype)
    dataType, functionName = functionPrototype.split(' ')


    functionDefinitionRegex = dataType + r' *?(\w+::)?' + functionName + r' *?\(.*?\) *?\{(.|\n)*?\}'
    if isStatic:
        functionDefinitionRegex = r'static ' + functionDefinitionRegex

    functionDefinitionRegex = compile(functionDefinitionRegex, MULTILINE)
    return sub(functionDefinitionRegex, '', inputCode)


def replace_calls(functionName, simulationFunctionName, inputCode):
    """Replaces all calls of the given function with the associated function 
       name in the simulation libraries."""
    # Replace all function calls with the simulation function name
    if 'readDistanceSensor' in simulationFunctionName:
        # Handle any function that is an alias for a distance sensor reading
        pinNumber = simulationFunctionName[-1]
        simulationFunctionName = 'Enes100Simulation.' + simulationFunctionName[:-1]
        functionName = compile(functionName + r' *?\(\w*?\)')
        inputCode = sub(functionName,
                        simulationFunctionName + f'({pinNumber})',
                        inputCode)
    else:
        inputCode = sub(functionName,
                        'TankSimulation.' + simulationFunctionName,
                        inputCode)
    
    return inputCode

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
    simulationDir = PATH_TO_SOURCE_FILE.parent.parent / 'OSVSimulation'
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
        translatedCode = translate_to_simulation(codeString)
        code.seek(0)  # Go to the beginning of the file
        code.write(translatedCode)
        code.truncate()

print(f'\nSuccessfully translated all of your OSV code into the directory {simulationDir.resolve()}')
