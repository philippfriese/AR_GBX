# functions : this_is_a_func()
# vars      : thisIsAVar
# classes   : ThisIsAClass


from abstract_classes import UserAction
from abstract_classes import ParsingReturnValues
from model import Model
from abstract_classes import UserInput
import threading
import queue
import argparse

class Control:
    def __init__(self, mock: bool, import_file: str, view_opt: str):
        EXPORT_FILENAME = "new_mod_data.dat"  
        IMPORT_FILENAME = import_file
        print("Export in Control " + EXPORT_FILENAME)
        print("Import in Control " + IMPORT_FILENAME)
        self.model = Model(EXPORT_FILENAME, IMPORT_FILENAME, mock)

        #self.view = view_commandline.CommandLineInterface(self.get_user_input, self.ctrl_msg_queue)
        self.view = self.select_view(view_opt)
        self.gui_thread = threading.Thread(target=self.view.interact)
        self.gui_thread.start()

       
    
    def select_view(self, view_opt: str):
        if "view_commandline" == view_opt:
            import view_commandline
            return view_commandline.CommandLineInterface(self.get_user_input, self.model)
        elif "tk_gui" == view_opt:
            import tk_gui
            return tk_gui.GUI(self.get_user_input, self.model)
        else:
            raise ValueError
    
    def parse_for_model(self, data):
        b_data = data.ljust(20).encode()
        return b_data

    def get_user_input(self, userInput: UserInput):
        userAction, additional_data = userInput.get_action_and_data()

        if userAction == UserAction.NO_ACTION:
            return
        elif userAction == UserAction.MODIFY_DATA:
            #TODO   is correct
            print("Ctrl: " + str(additional_data))
            g = self.model.get_gamecheatdata().get_Game(additional_data[0])
          
            g.delete_current_cheats()
            s = False
            cheatName = ''
            for elem in additional_data[1:]:
                if elem == "|":
                    s = True
                    continue
                if s:
                    b_cheatname = self.parse_for_model(elem)
                    g.set_cheatCodeName(b_cheatname)
                    cheatName = b_cheatname 
                    s = False
                else:
                    addresses = elem.split(', ')
                   # print(addresses)
                    g.set_cheatCodeAddresses(cheatName, addresses)

            self.model.write_data_to_device()
            self.model.driver.read_data()
        elif userAction == UserAction.EXPORT_ALL_DATA:
            
            self.model.write_data_to_device()
        #TODO DELETE_SINGLE_GAME
        elif userAction == UserAction.END_PROGRAM:
            self.model.tear_down()
            exit(0)
        else:
            print("Control says: Action is not possible")

if __name__ == "__main__":
    #get commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--mock', type=str, dest='mock', default="true", help="use real device or mock data")
    parser.add_argument('--if', type=str, dest='importfilename', default='imported_data.dat', help='File for saving device data')
    parser.add_argument('--view', type=str, dest='viewopt',default='view_commandline', help="select view options")
    args = parser.parse_args()
    if args.mock == "false":
        control = Control(False, args.importfilename, args.viewopt)
    else:
        control = Control(True, args.importfilename, args.viewopt)