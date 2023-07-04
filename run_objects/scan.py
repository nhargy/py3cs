"""
class   : scan
author  : Nadav Hargittai
"""

from sys3CS import default_rule


# Default system_state_filepath
path_to_system_state = 'C:/rep_py3cs/py3cs/config/system/states'
default_state = 'state_AA.json'

class scan:
    
    def __init__(self, path_to_hdf5, rule_filepath = default_rule, system_state_filepath = default_state):
        
        # now this class can have a method that takes the system state by
        # reading the state json file, and creating a group for each device
        # it can also check for a npy file in the folder of the component,
        # and create a named dataset for it within the group, alongside the id
        
        pass