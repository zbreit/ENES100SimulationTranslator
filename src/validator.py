from re import match, M
from pathlib import Path

class SettingsValidator:
    """A collection of static functions for validating the user's simulation settings"""

    @staticmethod
    def isCodeFile(filePath):
        """Returns true if the file at the given path is an Arduino file"""
        return isinstance(filePath, str) and match(r'^.+\.ino$', filePath) and Path(filePath).is_file()
    
    @staticmethod
    def isFunction(function):
        """Returns true if the given function value follows the format 'dataType functionName'"""
        return isinstance(function, str) and match(r'^(void|int|float|double|bool|long)\s\w[\w\d]*(\.\w[\w\d]*)?$', function, M)
    
    @staticmethod
    def fixConfigs(settings):
        # Make sure the source file is correct
        SettingsValidator.fixProperty('pathToSourceFile',
            validator=SettingsValidator.isCodeFile,
            settings=settings)
        
        # Make sure the functionNameReplacement dictionary exists
        functionReplacements = {}
        try:
            functionReplacements = settings.get('functionNameReplacements')
            if not isinstance(functionReplacements, dict):
                functionReplacements = dict(functionReplacements)
        except KeyError:
            settings.configs['functionNameReplacements'] = functionReplacements
        
        # Make sure all function names are valid
        for function in functionReplacements:
            SettingsValidator.fixProperty('functionNameReplacements', function,
                validator=SettingsValidator.isFunction,
                settings=settings)

    @staticmethod
    def fixProperty(*propertyList, validator, settings):
        try:
            currentVal = settings.get(*propertyList)
            if not validator(currentVal):
                settings.update(*propertyList, oldValue=currentVal)
        except KeyError:
            settings.update(*propertyList)