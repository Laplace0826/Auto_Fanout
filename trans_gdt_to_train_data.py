import shutil
import os
import base_function as bf

from config import SETUP
from config import NETLIST

if __name__ == '__main__':

    setup = SETUP()
    setup.read_config(setup.filepath+"/conf/"+setup.target_file)

    # clear data    
    
    try:
        shutil.rmtree(setup.filepath+"routable")
        os.mkdir('./learning_data/routable')
    except OSError as e:
        print(e)
        
    try:
        shutil.rmtree(setup.filepath+"unroutable")
        os.mkdir('./learning_data/unroutable')
    except OSError as e:
        print(e)

    print("CLEAR")

    # load
    
    target_folder=10
    
    print("\nEnvironment "+str(target_folder)+"\n")
    for times in range(1):
        
        if times%100==0:
            print(times)
        
        netlist = NETLIST()
        netlist.read_netlist(setup.filepath+"/conf/"+setup.target_file)
        netlist.multiply_1000()
        netlist.remove_unness_pin(setup.component)
        netlist.route_two_pin_net()
        netlist.focus_on_target_com(setup.component[ setup.target_component_index[0]], setup.component[setup.target_component_index[1]])
        netlist.find_boundary(setup.component[ setup.target_component_index[0]], setup.track_width, 5)
        netlist.remove_extra_obs(setup.layer)
        
        # process
        result=bf.trans_to_pic(setup, netlist, setup.filepath+setup.target_file+"/"+str(target_folder)+"/data_"+str(times)+".gdt")
        if result!=0:
            print("The file num_"+str(times)+" ! ERROR_code:"+str(result))

    print("\nFinish")
    