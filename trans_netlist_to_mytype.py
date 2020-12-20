#import base_function as bf
from config import SETUP
from config import NETLIST

if __name__ == '__main__':
    
    i=20
    total=i
    while i>=0:
        total=total*i
    print(total)
    
    setup = SETUP()
    setup.read_config(setup.filepath+"/conf/"+setup.target_file)
    
    netlist = NETLIST()
    netlist.read_netlist(setup.filepath+"/conf/"+setup.target_file)
    netlist.multiply_1000()
    netlist.remove_unness_pin(setup.component)
    netlist.route_two_pin_net()
    netlist.focus_on_target_com(setup.component[ setup.target_component_index[0]], setup.component[setup.target_component_index[1]])
    f_data = open(setup.filepath+"/conf/"+setup.target_file+"_data",'w')
    
    # find overlapping region
    for i in range(len(netlist.pin)):
        for j in range(len(netlist.pin[i])):
            for k in range(len(netlist.obs)):
                if netlist.pin[i][j][2]>=netlist.obs[k][1] and netlist.pin[i][j][2]<=netlist.obs[k][1]+netlist.obs[k][3] and netlist.pin[i][j][3]>=netlist.obs[k][2] and netlist.pin[i][j][3]<=netlist.obs[k][2]+netlist.obs[k][4] and netlist.obs[k][0]==0:
                    print(netlist.pin[i][j])
                    print(netlist.obs[k])
                    print("---")

    # output
    for i in range(len(netlist.pin)):
        f_data.write("PIN")
        for j in range(len(netlist.pin[i])):
            f_data.write("("+str(netlist.pin[i][j][0])+","+str(netlist.pin[i][j][2])+","+str(netlist.pin[i][j][3])+")")
        f_data.write("\n")
    
    for i in range(len(netlist.obs)):
        f_data.write("OBS("+str(netlist.obs[i][0])+","+str(netlist.obs[i][1])+","+str(netlist.obs[i][2])+","+str(netlist.obs[i][3])+","+str(netlist.obs[i][4])+")\n")
    f_data.close()

