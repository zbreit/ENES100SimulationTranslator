import json
from re import match
from validator import SettingsValidator

class SimulationSettings:
    """A class to that retreives and updates the user settings for the simulation script."""

    def __init__(self, path_to_config_file):
        self.file = path_to_config_file
        self.configs = None
        
        while not self.configs:
            try:
                with open(self.file) as configFile:
                    self.configs = json.loads(configFile.read())
            except (json.decoder.JSONDecodeError, EnvironmentError):
                print(f'\nError: "{self.file}" is not a valid JSON file.')
                self.file = input('Enter the path to a valid configuration file: ')
        
        SettingsValidator.fixConfigs(self)
        self.export()
        
    def get(self, *propertyList):
        """Retreives the configuration property with the given property path."""
        # Retreive the configuration with the given path to its property
        desired_config = self.configs
        for prop in propertyList:
            desired_config = desired_config[prop]

        return desired_config

    def update(self, *propertyList, oldValue=''):
        """Prompts the user for the value of the setting with the given property path."""
        config_val = self.__prompt_for_valid_config(*propertyList, oldValue=oldValue)

        configs_copy = self.configs
        # Go through every nested property, initializing it as an empty dictionary if it 
        # does not exist
        for prop in propertyList[:-1]:
            configs_copy = configs_copy.setdefault(prop, {})

        configs_copy[propertyList[-1]] = config_val

    def __prompt_for_valid_config(self, *propertyList, oldValue=''):
        """Retrieve a valid configuration value from the user on the command line"""
        self.__display_property_error(*propertyList, oldValue=oldValue)
        desired_config_val = input(f'Enter an appropriate value: ')

        # Make the user retype the value if property represents a function user input is in the wrong format
        if not SettingsValidator.isCodeFile(desired_config_val) and not SettingsValidator.isFunction(desired_config_val):
            desired_config_val = self.__prompt_for_valid_config(*propertyList, oldValue=desired_config_val)

        return desired_config_val

    def __display_property_error(self, *propertyList, oldValue=''):
        """Display what's wrong with the supplied property value"""
        errorStr = f'\nError: "{oldValue}" is not a valid setting for "{propertyList[-1]}". '

        if 'functionNameReplacements' in propertyList:
            errorStr += 'Function values must be in the form "dataType functionName".'
        elif 'pathToSourceFile' in propertyList:
            errorStr += 'The path to the source code file must be in the form "*.ino".'

        print(errorStr)

    def export(self):
        """Write the current configurations to the specified file"""
        with open(self.file, 'w') as configFile:
            configFile.write(json.dumps(self.configs, indent=4, sort_keys=True))