# ENES100SimulationTranslator
A convenience tool for converting OSV code to be compatible with the ENES100 vision system simulator.

## Download
Download the .ZIP folder for the repository, extract the


## How to Use It
Once you setup your configuration file, just run these commands in the terminal:
### Windows
```bash
$ cd PATH_TO_SIMULATION_EXECUTABLE_FOLDER # Locates the translator
$ simulate.exe # Runs the translator code
```
### Mac/Linux
```bash
$ cd PATH_TO_SIMULATION_EXECUTABLE_FOLDER # Locates the translator
$ ./simulate # Runs the translator code
```
Of course you have to replace `PATH_TO_SIMULATION_EXECUTABLE_FOLDER` with an actual file path. To see how to setup the translator to work with your code, check out the steps below.

## Setup
There are two critical componenets to the translator: the translator executable and the associated configuration file.

### The Executable
The executable (`simulate.exe`) holds all of the logic for converting your code into valid code for the vision simulator. It should be placed wherever you see convenient, although I would recommend placing it in the parent directory of your code folder, like so:
![Sample Folder Structure](https://imgur.com/zail7MW.png)

### The Configruation File
The configuration file (`simulation-settings.json`) allows you to specify the important settings for the translator (e.g., the path to your code files, the names of your own functions). The important settings are listed below:

```js
{
    "functionNameReplacements": {
        "readDistanceSensor1": "double getFrontDistance",
        "setLeftMotorPWM": "void setLeftSpeed",
        "setRightMotorPWM": "void setRightSpeed",
        "turnOffMotors": "void stopMotors"
    },
    "pathToSourceFile": "ActualOSVCode/ActualOSVCode.ino"
}
```
The configuration file is in the [JSON format](https://www.w3schools.com/js/js_json_intro.asp), which is just a way of storing data in `key: value` pairs. The string on the left is the key and the string or object on the right is the value. So the key `"pathToSourceFile"` has a value of `"ActualOSVCode/ActualOSVCode.ino"`.
#### How to setup your configuration file
1. Copy the above sample code into your own `simulation-settings.json` file, or use the one listed in this repository.
2. Specify the path to the primary OSV source code file. This should be the one that includes your `void loop()` and `void setup()` functions. If my source code folder looked something like this: ![Sample Source Code Folder](https://imgur.com/QtRL8jv.png) my setting for `pathToSourceFile` would be `"ActualOSVCode/ActualOSVCode.ino"`
3. Setup your function name replacements. There are a few functions in the simulation library, like `readDistanceSensor()` or `turnOffMotors()`, that aren't explicitly defined in the `Enes100.h` file. In your code file you'll specify your own functions that perform these same tasks, so we have to tell the translator their names and data types. For instance, let's say you had functions the following functions in your code:
   - `bool setRightMotorsTo()`
   - `bool setLeftMotorsTo()`
   - `void stopMotors()`
   - `double getFrontDistance()`
   - `double getSideDistance()`

    You would specify your `functionNameReplacements` object like so in the JSON:
```js
    "functionNameReplacements": {
        "readDistanceSensor1": "double getFrontDistance",
        "readDistanceSensor4": "double getSideDistance",
        "setLeftMotorPWM": "bool setRightMotorsTo",
        "setRightMotorPWM": "bool setLeftMotorsTo",
        "turnOffMotors": "void stopMotors"
    },
```
The names of the functions in the simulation libraries act as the keys, while the names of your own functions go on the right. Your functions should be in the format `dataType functionName`. A complete list of available function settings can be found below:
```js
    "functionNameReplacements": {
        "readDistanceSensor1": ...,
        "readDistanceSensor2": ...,
            ...
        "readDistanceSensor11": ...,
        "setLeftMotorPWM": "bool setLeftSpeed",
        "setRightMotorPWM": "bool setRightSpeed",
        "turnOffMotors": "void stopMotors",
    },
```
4. Save your file! For our example, the final file should look like this in the end (*Note: the order of the key, value pairs doesn't matter*):
```js
    "functionNameReplacements": {
        "readDistanceSensor1": "double getFrontDistance",
        "readDistanceSensor4": "double getSideDistance",
        "setLeftMotorPWM": "bool setRightMotorsTo",
        "setRightMotorPWM": "bool setLeftMotorsTo",
        "turnOffMotors": "void stopMotors"
    },
    "pathToSourceFile": "ActualOSVCode/ActualOSVCode.ino"
```
## TODO
- Add in automatic generation for the configuration file
- Create releases in GitHub to make downloading the translator easier
- Make error messages more helpful and context-specific

## Contributing
If you notice any issues with the translator, open a GitHub issue. If you find a way to fix the issue, feel free to send in a pull request.
