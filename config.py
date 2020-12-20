
class SETUP:

    def __init__(self):
        self.component = []
        self.usable_layer = 0
        self.strategy = []
        
        self.target_file = "2"
        self.target_component_index = [ 0, 2]
        self.layer = 0
        self.PIC_SIZE = 80
        self.track_width = 4000
        self.pin_width = 400
        self.filepath = "./learning_data/"
        self.EPISODE = 3

    def read_config(self,file_path):
        
        f_read = open(file_path+".conf",'r')
        text = f_read.readlines()
        f_read.close()
        
        for line in range(len(text)):
            text[line]=text[line].strip('\n')
            text[line]=text[line].strip('\t')
        
        index_colon=text[0].find(':')
        cpu=text[0][index_colon+1:]
            
        ddr = []
        index_colon=text[1].find(':')
        text[1]=text[1][index_colon+1:]
        index_space=0
        while index_space!=-1:
            index_space=text[1].find(' ')
            if index_space!=-1:
                ddr_name=text[1][0:index_space]
                text[1]=text[1][index_space+1:]
                ddr.append(ddr_name)
            elif index_space==-1:
                ddr_name=text[1]
                ddr.append(ddr_name)

        self.component.append([cpu,9999999,0,9999999,0])
        for i in range(len(ddr)):
            self.component.append([ddr[i],9999999,0,9999999,0])
    
        index_colon=text[2].find(':')
        self.usable_layer=text[2][index_colon+1:]
        
        index_colon=text[3].find(':')
        text[3]=text[3][index_colon+1:]
        index_space=0
        while index_space!=-1:
            index_space=text[3].find(' ')
            if index_space!=-1:
                strategy_name=text[3][0:index_space]
                text[3]=text[3][index_space+1:]
                self.strategy.append(strategy_name)
            elif index_space==-1:
                strategy_name=text[3]
                self.strategy.append(strategy_name)

    def update_com_boundary(self, netlist, extra_track_num):
        for i in range(len(self.component)):
            for j in range(len(netlist.pin)):
                for k in range(len(netlist.pin[j])):
                    if netlist.pin[j][k][0]==self.component[i][0]:
                        if netlist.pin[j][k][2] < self.component[i][1]:
                            self.component[i][1] = netlist.pin[j][k][2]
                        if netlist.pin[j][k][2] > self.component[i][2]:
                            self.component[i][2] = netlist.pin[j][k][2]
                        if netlist.pin[j][k][3] < self.component[i][3]:
                            self.component[i][3] = netlist.pin[j][k][3]
                        if netlist.pin[j][k][3] > self.component[i][4]:
                            self.component[i][4] = netlist.pin[j][k][3]
            self.component[i][1] = self.component[i][1] - self.track_width * extra_track_num
            self.component[i][2] = self.component[i][2] + self.track_width * extra_track_num
            self.component[i][3] = self.component[i][3] - self.track_width * extra_track_num
            self.component[i][4] = self.component[i][4] + self.track_width * extra_track_num

class NETLIST:

    def __init__(self):

        self.pin = []
        self.obs = []
        self.boundary = []
        self.remove_pin = []

    def read_netlist(self, file_path):

        f_read_pin = open(file_path+".brd_input.netlist",'r')
        text = f_read_pin.readlines()
        f_read_pin.close()
        
        for line in range(len(text)):
            text[line]=text[line].strip('\n')
            text[line]=text[line].strip('\t')
    
        one_net = []
        begin_pin_start = 0  
        for line in range(len(text)):
            if begin_pin_start == 0:
                index=text[line].find('PIN START')
                if index!=-1:
                    begin_pin_start=1
            elif begin_pin_start == 1:
                index=text[line].find('PIN END')
                if index!=-1:
                    begin_pin_start=0
                    self.pin.append(one_net)
                    one_net = []
                else:
                    index_space=text[line].find(' ')
                    name=text[line][0:index_space]
                    index_name=name.find('.')
                    com_name=name[0:index_name]
                    pin_name=name[index_name+1:]
                    text[line]=text[line][index_space+1:]
                    index_space=text[line].find(' ')
                    if index_space!=-1:
                        text[line]=text[line][0:index_space]
                    index_space=text[line].find(',')
                    x=text[line][0:index_space]
                    y=text[line][index_space+1:]
                    one_net.append([com_name,pin_name,x,y])
        
        f_read_obs = open(file_path+".brd.obs",'r')
        text = f_read_obs.readlines()
        f_read_obs.close()
        
        for line in range(len(text)):
            text[line]=text[line].strip('\n')
            text[line]=text[line].strip('\t')
        
        for line in range(len(text)):
            index=text[line].find('ObsPad')
            if index!=-1:
                layer=text[line+1][9:]
                coor=text[line+2][8:]
                index_coor=coor.find(',')
                x=coor[0:index_coor]
                y=coor[index_coor+1:]
                width=text[line+4][9:]
                height=text[line+5][10:]
                self.obs.append([int(layer),x,y,width,height])

    def multiply_1000(self):
        for i in range(len(self.pin)):
            for j in range(len(self.pin[i])):
                self.pin[i][j][2]=int(float(self.pin[i][j][2])*1000)
                self.pin[i][j][3]=int(float(self.pin[i][j][3])*1000)
        for i in range(len(self.obs)):
            self.obs[i][1]=int(float(self.obs[i][1])*1000)
            self.obs[i][2]=int(float(self.obs[i][2])*1000)
            self.obs[i][3]=int(float(self.obs[i][3])*1000)
            self.obs[i][4]=int(float(self.obs[i][4])*1000)

    def remove_unness_pin(self, component):
        clear = 0
        while clear==0:
            clear=1
            for i in range(len(self.pin)):
                if clear==0:
                    break
                if len(self.pin[i])<=1:
                    del self.pin[i]
                    clear=0
                    break
                for j in range(len(self.pin[i])):
                    check=0
                    for k in range(len(component)):
                        if self.pin[i][j][0]==component[k][0]:
                            check=1
                    if check==0:
                        del self.pin[i][j]
                        clear=0
                        break

    def route_two_pin_net(self):
        clear = 0
        while clear==0:
            clear=1
            for i in range(len(self.pin)):
                if len(self.pin[i])!=2:
                    for j in range(len(self.pin[i])):
                        self.remove_pin.append(self.pin[i][j])
                    del self.pin[i]
                    clear=0
                    break

    def focus_on_target_com(self,target_0,target_1):
        clear = 0
        while clear==0:
            clear=1
            for i in range(len(self.pin)):
                for j in range(len(self.pin[i])):
                    if self.pin[i][j][0]!=target_0 and self.pin[i][j][0]!=target_1:
                        self.remove_pin.append(self.pin[i][j])
                        del self.pin[i][j]
                        clear=0
                        break
                if len(self.pin[i])==1:
                    self.remove_pin.append(self.pin[i][0])
                    del self.pin[i]
                    clear=0
                    break
                if len(self.pin[i])<1:
                    clear=0
                    break

    def find_boundary(self, target_name, track_width , extra_track_num):
        max_x = self.pin[0][0][2]
        min_x = self.pin[0][0][2]
        max_y = self.pin[0][0][3]
        min_y = self.pin[0][0][3]
        self.boundary = [min_x,max_x,min_y,max_y]
        for i in range(len(self.pin)):
            for j in range(len(self.pin[i])):
                if self.pin[i][j][0]==target_name:
                    if self.pin[i][j][2] > self.boundary[1]:
                        self.boundary[1] = self.pin[i][j][2]
                    if self.pin[i][j][2] < self.boundary[0]:
                        self.boundary[0] = self.pin[i][j][2]
                    if self.pin[i][j][3] > self.boundary[3]:
                        self.boundary[3] = self.pin[i][j][3]
                    if self.pin[i][j][3] < self.boundary[2]:
                        self.boundary[2] = self.pin[i][j][3]
        
        self.boundary[0] = self.boundary[0] - int(track_width*extra_track_num)
        self.boundary[1] = self.boundary[1] + int(track_width*extra_track_num)
        self.boundary[2] = self.boundary[2] - int(track_width*extra_track_num)
        self.boundary[3] = self.boundary[3] + int(track_width*extra_track_num)

    def remove_extra_obs(self, layer):
        clear = 0
        while clear==0:
            clear=1
            for i in range(len(self.obs)):
                if self.obs[i][0]!=layer and layer!=-1:
                    del self.obs[i]
                    clear=0
                    break
                if self.obs[i][1]+self.obs[i][3] < self.boundary[0] or self.obs[i][1] > self.boundary[1] or self.obs[i][2]+self.obs[i][4] < self.boundary[2] or self.obs[i][2] > self.boundary[3]:
                    del self.obs[i]
                    clear=0
                    break

    def find_all_boundary(self, track_width , extra_track_num):
        max_x = self.pin[0][0][2]
        min_x = self.pin[0][0][2]
        max_y = self.pin[0][0][3]
        min_y = self.pin[0][0][3]
        self.boundary = [min_x,max_x,min_y,max_y]
        for i in range(len(self.pin)):
            for j in range(len(self.pin[i])):
                if self.pin[i][j][2] > self.boundary[1]:
                    self.boundary[1] = self.pin[i][j][2]
                if self.pin[i][j][2] < self.boundary[0]:
                    self.boundary[0] = self.pin[i][j][2]
                if self.pin[i][j][3] > self.boundary[3]:
                    self.boundary[3] = self.pin[i][j][3]
                if self.pin[i][j][3] < self.boundary[2]:
                    self.boundary[2] = self.pin[i][j][3]
                    
        for i in range(len(self.obs)):
            if self.obs[i][1]+self.obs[i][3] > self.boundary[1]:
                self.boundary[1] = self.obs[i][1]+self.obs[i][3]
            if self.obs[i][1] < self.boundary[0]:
                self.boundary[0] = self.obs[i][1]
            if self.obs[i][2]+self.obs[i][4] > self.boundary[3]:
                self.boundary[3] = self.obs[i][2]+self.obs[i][4]
            if self.obs[i][2] < self.boundary[2]:
                self.boundary[2] = self.obs[i][2]
        
        self.boundary[0] = self.boundary[0] - int(track_width*extra_track_num)
        self.boundary[1] = self.boundary[1] + int(track_width*extra_track_num)
        self.boundary[2] = self.boundary[2] - int(track_width*extra_track_num)
        self.boundary[3] = self.boundary[3] + int(track_width*extra_track_num)
        

