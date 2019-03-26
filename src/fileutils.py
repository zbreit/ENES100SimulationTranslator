import shutil

def remove_directory(dir):
    """A wrapper for shutil.rmtree() that will give the user time to
       close resources if they're open by accident."""   
    try:
        shutil.rmtree(dir)
    except PermissionError:
        # Try to remove the directory again if any of its resources
        # were open elsewhere on the computer
        print(f'\nThe "{dir.resolve()}" folder is in use on your computer.')
        input('Press "ENTER" after closing any windows that were accessing that directory: ')
        remove_directory(dir)
    except FileNotFoundError:
        # Ignore the remove command if the directory doesn't exist
        pass

def recursively_copy(src, dest, counter=0):
    """A wrapper for shutil.copytree() that will call itself again
       if there is a permission error in copying the file."""
    remove_directory(dest) # necessary to prevent a FileExistsError
    try:
        shutil.copytree(src, dest)
    except PermissionError:
         # Try the copy again if there is a weird permission error on the first
         # attempt
        if counter < 10:
            recursively_copy(src, dest, counter + 1)
        else:
            raise PermissionError('Can\'t copy the Arduino sketch directory.')