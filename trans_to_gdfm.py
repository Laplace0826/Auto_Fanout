import math
import random
import os
import time

from config import SETUP
from config import NETLIST

def read_route_file(file_name):
    f_read = open(file_name,'r')
    text = f_read.readlines()
    f_read.close()
    
    for line in range(len(text)):
        text[line]=text[line].strip('\n')
        text[line]=text[line].strip('\t')
        
    unroute_net = text
    return unroute_net

def output_the_nemo_format(netlist, setup, layer, extra_track_num=2):
    # gdfm
    f_gdfm = open('./'+setup.target_file+'.gdfm','w')
    f_gdfm.write('.tech\n')
    f_gdfm.write('1 0 0 0 0 0 0 0 '+str(netlist.boundary[1])+' '+str(netlist.boundary[3])+'\n')
    f_gdfm.write('.end\n')
    f_gdfm.write('.cell\n')
    f_gdfm.write('.end\n')
    f_gdfm.write('.net\n')
    for i in range(len(netlist.pin)):
        f_gdfm.write(str(i)+' net'+str(i)+' '+str(netlist.pin[i][0][1])+' '+str(netlist.pin[i][1][1])+'\n')
    f_gdfm.write('.end\n')
    f_gdfm.write('.pin\n')
    for i in range(len(netlist.pin)):
        for j in range(len(netlist.pin[i])):
            f_gdfm.write(str(netlist.pin[i][j][1])+' 0 0 '+str(i)+' '+str(netlist.pin[i][j][2])+' '+str(netlist.pin[i][j][3])+'\n')
    f_gdfm.write('.end\n')
    f_gdfm.close()
    # obs
    f_obs = open('./'+setup.target_file+'.obs','w')
    for i in range(len(netlist.obs)):
        if netlist.obs[i][0]==layer:
            f_obs.write(str(netlist.obs[i][1])+' '+str(netlist.obs[i][2])+' '+str(netlist.obs[i][1]+netlist.obs[i][3])+' '+str(netlist.obs[i][2]+netlist.obs[i][4])+' '+str(netlist.obs[i][0])+'\n')
    if layer==0:
        for i in range(len(netlist.remove_pin)):
            f_obs.write(str(netlist.remove_pin[i][2]-int(setup.pin_width/2))+' '+str(netlist.remove_pin[i][3]-int(setup.pin_width/2))+' '+str(netlist.remove_pin[i][2]+int(setup.pin_width/2))+' '+str(netlist.remove_pin[i][3]+int(setup.pin_width/2))+' '+str(0)+'\n')
    f_obs.close()
    # pgr
    f_pgr = open('./'+setup.target_file+'.pgr','w')
    f_pgr.write('1 1\n')
    f_pgr.write(str(netlist.boundary[1])+' '+str(netlist.boundary[3])+'\n')
    for i in range(len(netlist.pin)):
        f_pgr.write('.net '+str(i)+' 0\n')
        f_pgr.write('0 0 0\n')
    f_pgr.close()

def create_obs_gdt(netlist, setup): 
    # gdfm
    f_gdfm = open('./'+setup.target_file+'_obs.gdfm','w')
    f_gdfm.write('.tech\n')
    f_gdfm.write('3 0 0 0 0 0 0 0 '+str(netlist.boundary[1])+' '+str(netlist.boundary[3])+'\n')
    f_gdfm.write('.end\n')
    f_gdfm.write('.cell\n')
    f_gdfm.write('.end\n')
    f_gdfm.write('.net\n')
    f_gdfm.write('0 net0 0 1\n')
    f_gdfm.write('.end\n')
    f_gdfm.write('.pin\n')
    f_gdfm.write('0 0 0 0 100000 100000\n')
    f_gdfm.write('1 0 0 0 200000 100000\n')
    f_gdfm.write('.end\n')    
    f_gdfm.close()
    # obs
    f_obs = open('./'+setup.target_file+'_obs.obs','w')
    for i in range(len(netlist.obs)):
        f_obs.write(str(netlist.obs[i][1])+' '+str(netlist.obs[i][2])+' '+str(netlist.obs[i][1]+netlist.obs[i][3])+' '+str(netlist.obs[i][2]+netlist.obs[i][4])+' '+str(netlist.obs[i][0])+'\n')
    for i in range(len(netlist.remove_pin)):
            f_obs.write(str(netlist.remove_pin[i][2]-int(setup.pin_width/2))+' '+str(netlist.remove_pin[i][3]-int(setup.pin_width/2))+' '+str(netlist.remove_pin[i][2]+int(setup.pin_width/2))+' '+str(netlist.remove_pin[i][3]+int(setup.pin_width/2))+' '+str(0)+'\n')
    f_obs.close()
    
    # pgr
    f_pgr = open('./'+setup.target_file+'_obs.pgr','w')
    f_pgr.write('1 1\n')
    f_pgr.write(str(netlist.boundary[1])+' '+str(netlist.boundary[3])+'\n')
    f_pgr.write('.net 0 0\n')
    f_pgr.write('0 0 0\n')
    f_pgr.close()
    
    os.system("./nemo ./"+setup.target_file+"_obs ./"+setup.target_file+"_obs")
    
    os.system("rm ./"+setup.target_file+"_obs.gdfm")
    os.system("rm ./"+setup.target_file+"_obs.obs")
    os.system("rm ./"+setup.target_file+"_obs.pgr")

def combine_the_same_part_gdt(setup):
    f_read = open(setup.target_file+'_0.gdt','r')
    text_0 = f_read.readlines()
    f_read.close()
    
    
    del text_0[0]
    del text_0[0]
    del text_0[0]
    del text_0[0]
    del text_0[len(text_0)-1]
    del text_0[len(text_0)-1]
    
    clear = 0
    while clear==0:
        clear=1
        for i in range(len(text_0)):
            if text_0[i][2]==str(0) and text_0[i][7]==str(0):
                clear=0
                del text_0[i]
                break
          
    # 1
    f_read = open(setup.target_file+'_1.gdt','r')
    text_1 = f_read.readlines()
    f_read.close()
    
    del text_1[0]
    del text_1[0]
    del text_1[0]
    del text_1[0]
    del text_1[len(text_1)-1]
    del text_1[len(text_1)-1]
    
    clear = 0
    while clear==0:
        clear=1
        for i in range(len(text_1)):
            if text_1[i][2]==str(0) and text_1[i][7]==str(0):
                clear=0
                del text_1[i]
                break
    
    for i in range(len(text_1)):
        text_1[i] = text_1[i].replace("b{50", "b{60")
    
    #obs
    f_read = open(setup.target_file+'_obs.gdt','r')
    text = f_read.readlines()
    f_read.close()
    
    clear=0
    while clear==0:
        clear=1
        for i in range(len(text)):
            if i>50:
                break
            if i>3:
                if text[i][6]!=str(1) or text[i][7]!=str(0) or text[i][8]!=str(0):
                    del text[i]
                    clear=0
                    break

    index=4
    for i in range(len(text_0)):
        text.insert(index,text_0[i])
        index=index+1
        
    for i in range(len(text_1)):
        text.insert(index,text_1[i])
        index=index+1
    
    clear=0
    while clear==0:
        clear=1
        pin_count=0
        for i in range(len(text)):
            if "b{0 dt100" in text[i]:
                continue
            if "b{50" in text[i] or "b{60" in text[i]:
                pin_count=0
            elif "b{0 dt1" in text[i] and pin_count==0:
                pin_count=1
            elif "b{0 dt1" in text[i] and pin_count==1:
                pin_count=2
            elif "b{0 dt1" in text[i] and pin_count>=2:
                del text[i-1]
                del text[i-2]
                clear=0
                break
                
    # output gdt file
        
    f_gdt = open('./'+setup.target_file+'_total.gdt','w')
    for i in range(len(text)):
        f_gdt.write(text[i])
    f_gdt.close()

    os.system("./gdt2gds ./"+setup.target_file+"_total.gdt ./"+setup.target_file+"_total.gds")

def get_fanout_position(netlist, setup, layer):
    f_read = open(setup.target_file+'_'+str(layer)+'.gdt','r')
    text = f_read.readlines()
    f_read.close()
    
    del text[0]
    del text[0]
    del text[0]
    del text[0]
    del text[len(text)-1]
    del text[len(text)-1]
    
    data_obs = []
    data_pin = []
    
    for i in range(len(text)):
        string_split = text[i].split(" ", 9)
        string_split[0]=string_split[0][2:]
        string_split[1]=string_split[1][2:]
        string_split[2]=string_split[2][3:]
        string_split[9]=string_split[9][:len(string_split[9])-3]
        string_split[2]=int(float(string_split[2])*1000/2)
        string_split[3]=int(float(string_split[3])*1000/2)
        string_split[4]=int(float(string_split[4])*1000/2)
        string_split[5]=int(float(string_split[5])*1000/2)
        string_split[6]=int(float(string_split[6])*1000/2)
        string_split[7]=int(float(string_split[7])*1000/2)
        string_split[8]=int(float(string_split[8])*1000/2)
        string_split[9]=int(float(string_split[9])*1000/2)
        if string_split[1]=='100':
            data_obs.append(string_split)
        elif string_split[1]=='1':
            for i in range(len(setup.component)):
                if string_split[2]>=setup.component[i][1] and string_split[2]<=setup.component[i][2] and string_split[3]>=setup.component[i][3] and string_split[3]<=setup.component[i][4]:
                    string_split.append(setup.component[i][0])
                    string_split.append('')
                    data_pin.append(string_split)
        elif string_split[1]=='0':
            string_split.append('')
            string_split.append('')
            data_pin.append(string_split)

    clear=0
    while clear==0:
        clear=1
        pin_count=0
        for i in range(len(data_pin)):
            if data_pin[i][1]=='0':
                pin_count=0
            elif data_pin[i][1]=='1' and pin_count==0:
                pin_count=1
            elif data_pin[i][1]=='1' and pin_count==1:
                pin_count=2
            elif data_pin[i][1]=='1' and pin_count>=2:
                del data_pin[i-2]
                clear=0
                break
        if clear==1 and pin_count>=2:
            del data_pin[len(data_pin)-1]
            del data_pin[len(data_pin)-1]
    
    for i in range(len(data_pin)):
        print(data_pin[i])
        
    print('-------------')
    print("Start find fanout point.")
    print('-------------')
    print('')
    com_index=0
    times=0
    tStart = time.time()

def get_fanout_position_old(file_name,com_boundary,max_x,max_y):

    f_read = open(file_name+'.gdt','r')
    text = f_read.readlines()
    f_read.close()
    
    del text[0]
    del text[0]
    del text[0]
    del text[0]
    del text[len(text)-1]
    del text[len(text)-1]
    
    data_obs = []
    data_pin = []
    
    for i in range(len(text)):
        string_split = text[i].split(" ", 9)
        string_split[0]=string_split[0][2:]
        string_split[1]=string_split[1][2:]
        string_split[2]=string_split[2][3:]
        string_split[9]=string_split[9][:len(string_split[9])-3]
        string_split[2]=int(float(string_split[2])*1000/2)
        string_split[3]=int(float(string_split[3])*1000/2)
        string_split[4]=int(float(string_split[4])*1000/2)
        string_split[5]=int(float(string_split[5])*1000/2)
        string_split[6]=int(float(string_split[6])*1000/2)
        string_split[7]=int(float(string_split[7])*1000/2)
        string_split[8]=int(float(string_split[8])*1000/2)
        string_split[9]=int(float(string_split[9])*1000/2)
        if string_split[1]=='100':
            data_obs.append(string_split)
        elif string_split[1]=='1':
            for i in range(len(com_boundary)):
                if string_split[2]>=com_boundary[i][1] and string_split[2]<=com_boundary[i][2] and string_split[3]>=com_boundary[i][3] and string_split[3]<=com_boundary[i][4]:
                    string_split.append(com_boundary[i][0])
                    string_split.append('')
                    data_pin.append(string_split)
        elif string_split[1]=='0':
            string_split.append('')
            string_split.append('')
            data_pin.append(string_split)

    clear=0
    while clear==0:
        clear=1
        pin_count=0
        for i in range(len(data_pin)):
            if data_pin[i][1]=='0':
                pin_count=0
            elif data_pin[i][1]=='1' and pin_count==0:
                pin_count=1
            elif data_pin[i][1]=='1' and pin_count==1:
                pin_count=2
            elif data_pin[i][1]=='1' and pin_count>=2:
                del data_pin[i-2]
                clear=0
                break
        if clear==1 and pin_count>=2:
            del data_pin[len(data_pin)-1]
            del data_pin[len(data_pin)-1]

    print('-------------')
    print("Start find fanout point.")
    print('-------------')
    print('')
    com_index=0
    times=0
    tStart = time.time()
    
    while 1==1:
        print('-------------')
        print("Process the "+com_boundary[com_index][0]+". The "+str(times)+" times")
        print('-------------')
        check_data_pin = []
        start_find=0
        for a in range(len(data_pin)):
            if data_pin[a][10]==com_boundary[com_index][0] and start_find==0:
                new_pin_a=data_pin[a]
                start_find=1
                new_pin_a[2]=math.floor(new_pin_a[2]/10)*10
                new_pin_a[3]=math.floor(new_pin_a[3]/10)*10
                new_pin_a[4]=math.floor(new_pin_a[4]/10)*10
                new_pin_a[5]=math.floor(new_pin_a[5]/10)*10
                new_pin_a[6]=math.floor(new_pin_a[6]/10)*10
                new_pin_a[7]=math.floor(new_pin_a[7]/10)*10
                new_pin_a[8]=math.floor(new_pin_a[8]/10)*10
                new_pin_a[9]=math.floor(new_pin_a[9]/10)*10
            if start_find==1:
                if data_pin[a][0]=='50':
                    if data_pin[a][2]<=com_boundary[com_index][1] and data_pin[a][4]>=com_boundary[com_index][1]:#左
                        if data_pin[a][3]>=com_boundary[com_index][3] and data_pin[a][3]<=com_boundary[com_index][4]:
                            best_posi_x=com_boundary[com_index][1]
                            best_posi_y=data_pin[a][3]
                            new_pin_b=[data_pin[a][0],data_pin[a][1],best_posi_x,best_posi_y,best_posi_x,best_posi_y,best_posi_x,best_posi_y,best_posi_x,best_posi_y,com_boundary[com_index][0],'','']
                            check_data_pin.append([new_pin_a,new_pin_b])
                            start_find=0
                    if data_pin[a][2]<=com_boundary[com_index][2] and data_pin[a][4]>=com_boundary[com_index][2]:#右
                        if data_pin[a][3]>=com_boundary[com_index][3] and data_pin[a][3]<=com_boundary[com_index][4]:
                            best_posi_x=com_boundary[com_index][1]
                            best_posi_y=data_pin[a][3]
                            new_pin_b=[data_pin[a][0],data_pin[a][1],best_posi_x,best_posi_y,best_posi_x,best_posi_y,best_posi_x,best_posi_y,best_posi_x,best_posi_y,com_boundary[com_index][0],'','']
                            check_data_pin.append([new_pin_a,new_pin_b])
                            start_find=0
                    if data_pin[a][3]<=com_boundary[com_index][3] and data_pin[a][7]>=com_boundary[com_index][3]:#下
                        if data_pin[a][2]>=com_boundary[com_index][1] and data_pin[a][2]<=com_boundary[com_index][2]:
                            best_posi_x=data_pin[a][2]
                            best_posi_y=com_boundary[com_index][3]
                            new_pin_b=[data_pin[a][0],data_pin[a][1],best_posi_x,best_posi_y,best_posi_x,best_posi_y,best_posi_x,best_posi_y,best_posi_x,best_posi_y,com_boundary[com_index][0],'','']
                            check_data_pin.append([new_pin_a,new_pin_b])
                            start_find=0
                    if data_pin[a][3]<=com_boundary[com_index][4] and data_pin[a][7]>=com_boundary[com_index][4]:#上
                        if data_pin[a][2]>=com_boundary[com_index][1] and data_pin[a][2]<=com_boundary[com_index][2]:
                            best_posi_x=data_pin[a][2]
                            best_posi_y=com_boundary[com_index][4]
                            new_pin_b=[data_pin[a][0],data_pin[a][1],best_posi_x,best_posi_y,best_posi_x,best_posi_y,best_posi_x,best_posi_y,best_posi_x,best_posi_y,com_boundary[com_index][0],'','']
                            check_data_pin.append([new_pin_a,new_pin_b])
                            start_find=0

        if len(check_data_pin)!=0:
            
            for i in range(len(check_data_pin)):
                check_data_pin[i][1][12]=int(math.sqrt(check_data_pin[i][1][2]*check_data_pin[i][1][2]+check_data_pin[i][1][3]*check_data_pin[i][1][3]))
                
            for i in range(len(check_data_pin)):
                for j in range(i+1,len(check_data_pin)):
                    if check_data_pin[i][1][12]>check_data_pin[j][1][12]:
                        (check_data_pin[i],check_data_pin[j])=(check_data_pin[j],check_data_pin[i])
            
            # random change two fanout position
            
            
            
            """
            if check_data_pin[0][1][2]==check_data_pin[len(check_data_pin)-1][1][2]:
                min_pos=check_data_pin[0][1][3]
                max_pos=check_data_pin[len(check_data_pin)-1][1][3]
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            elif check_data_pin[0][1][3]==check_data_pin[len(check_data_pin)-1][1][3]:
                min_pos=check_data_pin[0][1][2]
                max_pos=check_data_pin[len(check_data_pin)-1][1][2]
                space=int((max_pos-min_pos)/(len(check_data_pin)-2))
                for i in range(len(check_data_pin)):
                    min_pos=min_pos+space
                    check_data_pin[i][1][2]=min_pos
            else:
                print("Corner")
            """
            
            if times!=0:
                random.shuffle(check_data_pin)

            num_pin_index=0
            for count_1 in range(len(check_data_pin)):
                for count_2 in range(len(check_data_pin[count_1])):
                    check_data_pin[count_1][count_2][11]=str(num_pin_index)
                    num_pin_index=num_pin_index+1
                    
            # gdfm
            f_gdfm = open('./'+file_name+'_fanout_'+str(com_index)+'.gdfm','w')
            f_gdfm.write('.tech\n')
            f_gdfm.write('1 0 0 0 0 0 0 0 '+str(max_x)+' '+str(max_y)+'\n')
            f_gdfm.write('.end\n')
            f_gdfm.write('.cell\n')
            f_gdfm.write('.end\n')
            f_gdfm.write('.net\n')
            for net_count in range(len(check_data_pin)):
                f_gdfm.write(str(net_count)+' net'+str(net_count)+' '+str(check_data_pin[net_count][0][11])+' '+str(check_data_pin[net_count][1][11])+'\n')
            f_gdfm.write('.end\n')
            f_gdfm.write('.pin\n')
            for net_count in range(len(check_data_pin)):
                for j in range(len(check_data_pin[net_count])):
                    f_gdfm.write(str(check_data_pin[net_count][j][11])+' 0 0 '+str(net_count)+' '+str(check_data_pin[net_count][j][2])+' '+str(check_data_pin[net_count][j][3])+'\n')
            f_gdfm.write('.end\n')    
            f_gdfm.close()
            
            # obs
            f_obs = open('./'+file_name+'_fanout_'+str(com_index)+'.obs','w')
            for obs_count in range(len(data_obs)):
                f_obs.write(str(data_obs[obs_count][2])+' '+str(data_obs[obs_count][3])+' '+str(data_obs[obs_count][6])+' '+str(data_obs[obs_count][7])+' '+'0\n')
            
            space_for_route=700
            f_obs.write('0 0 '+str(math.floor(com_boundary[com_index][2]+space_for_route))+' '+str(math.floor(com_boundary[com_index][3]-space_for_route))+' 0\n')
            f_obs.write('0 0 '+str(math.floor(com_boundary[com_index][1]-space_for_route))+' '+str(math.floor(com_boundary[com_index][4]+space_for_route))+' 0\n')
            f_obs.write('0 '+str(math.floor(com_boundary[com_index][4]+space_for_route))+' '+str(max_x)+' '+str(max_y)+' 0\n')
            f_obs.write(str(math.floor(com_boundary[com_index][2]+space_for_route))+' 0 '+str(max_x)+' '+str(max_y)+' 0\n')
            f_obs.close()
            
            # pgr
            f_pgr = open('./'+file_name+'_fanout_'+str(com_index)+'.pgr','w')
            f_pgr.write('1 1\n')
            f_pgr.write(str(max_x)+' '+str(max_y)+'\n')
            for net_count in range(len(check_data_pin)):
                f_pgr.write('.net '+str(net_count)+' 0\n')
                f_pgr.write('0 0 0\n')
            f_pgr.close()
            
            if times<=35:
                os.system("./nemo_fast ./"+file_name+"_fanout_"+str(com_index)+" ./"+file_name+"_fanout_"+str(com_index))
            else:
                os.system("./nemo ./"+file_name+"_fanout_"+str(com_index)+" ./"+file_name+"_fanout_"+str(com_index))
            unroute_net = read_route_file('Route.txt')

            os.system("rm ./"+file_name+"_fanout_"+str(com_index)+".gdfm")
            os.system("rm ./"+file_name+"_fanout_"+str(com_index)+".obs")
            os.system("rm ./"+file_name+"_fanout_"+str(com_index)+".pgr")

            filepath = "./learning_data"
            if len(unroute_net)!=1:
                times=times+1
                if times>=40:
                    #確認不可繞
                    index=0
                    while 1==1:
                        if os.path.isfile(filepath+"/unroutable/data_"+str(index)+".gdt"):
                            index+=1
                        else:
                            os.system("cp ./"+file_name+"_fanout_"+str(com_index)+".gdt"+" "+filepath+"/unroutable/data_"+str(index)+".gdt")
                            os.system("cp ./"+file_name+"_fanout_"+str(com_index)+".gds"+" "+filepath+"/unroutable/data_"+str(index)+".gds")
                            os.system("rm ./"+file_name+"_fanout_"+str(com_index)+".gds")
                            os.system("rm ./"+file_name+"_fanout_"+str(com_index)+".gdt")
                            break
                            
                    times=0
                    com_index=com_index+1
                    tEnd = time.time()
                    if com_index==len(com_boundary):
                        success=1
                        break
            else:                
                #確認可繞
                index=0
                while 1==1:
                    if os.path.isfile(filepath+"/routable/data_"+str(index)+".gdt"):
                        index+=1
                    else:
                        os.system("cp "+file_name+"_fanout_"+str(com_index)+".gdt"+" "+filepath+"/routable/data_"+str(index)+".gdt")
                        os.system("cp "+file_name+"_fanout_"+str(com_index)+".gds"+" "+filepath+"/routable/data_"+str(index)+".gds")
                        os.system("rm ./"+file_name+"_fanout_"+str(com_index)+".gds")
                        os.system("rm ./"+file_name+"_fanout_"+str(com_index)+".gdt")
                        break
                        
                times=0
                com_index=com_index+1
                tEnd = time.time()
                tStart = time.time()
                if com_index==len(com_boundary):
                    break
        else:
            times=0
            com_index=com_index+1
            if com_index==len(com_boundary):
                break

if __name__ == '__main__':
    
    print("#####################################")
    print("#                                   #")
    print("#              START                #")
    print("#                                   #")
    print("#####################################")
    
    setup = SETUP()
    setup.read_config(setup.filepath+"conf/"+setup.target_file)
    
    netlist = NETLIST()
    netlist.read_netlist(setup.filepath+"conf/"+setup.target_file)
    netlist.multiply_1000()
    setup.update_com_boundary( netlist, 2)
    netlist.remove_unness_pin(setup.component)
    netlist.route_two_pin_net()
    netlist.focus_on_target_com(setup.component[ setup.target_component_index[0]][0], setup.component[setup.target_component_index[1]][0])
    netlist.find_all_boundary( setup.track_width, 2)

    create_obs_gdt(netlist, setup)

    print("#####################################")
    print("#                                   #")
    print("#            TWO PIN NET            #")
    print("#                                   #")
    print("#####################################")
    
    test_time = 0
    
    while test_time <= 2500:
        print("#####################")
        print("#   The "+str(test_time)+" times.   #")
        print("#####################")
        
        random.shuffle(netlist.pin)
        
        # rename the pin name
        num_pin_index=0
        for i in range(len(netlist.pin)):
            for j in range(len(netlist.pin[i])):
                netlist.pin[i][j][1]=str(num_pin_index)
                num_pin_index+=1
        output_the_nemo_format( netlist, setup, setup.layer)
        
        print("#####################################")
        print("#                                   #")
        print("#              LAYER 0              #")
        print("#                                   #")
        print("#####################################")
        
        if test_time<=250:
            os.system("./nemo_no_iterative ./"+setup.target_file+" ./"+setup.target_file+"_0")
        else:
            os.system("./nemo ./"+setup.target_file+" ./"+setup.target_file+"_0")
        
        unroute_net = read_route_file('Route.txt')
        
        if len(unroute_net)!=1:   
            for i in range(len(netlist.pin)):
                for j in range(len(netlist.pin[i])):
                        netlist.pin[i][j][1]=''
            # trans pin name to index
            num_pin_index=0
            for i in range(len(netlist.pin)):
                routed=1
                for j in range(len(unroute_net)-1):
                    if i == int(unroute_net[j]):
                        routed=0
                        break
                if routed==0:
                    for j in range(len(netlist.pin[i])):
                        netlist.pin[i][j][1]=str(num_pin_index)
                        num_pin_index+=1
            clear=0
            while clear==0:
                clear=1
                for i in range(len(netlist.pin)):
                    if clear==0:
                        break
                    for j in range(len(netlist.pin[i])):
                        if netlist.pin[i][j][1]=='':
                            del netlist.pin[i]
                            clear=0
                            break
            output_the_nemo_format( netlist, setup, setup.layer+1)
    
            print("#####################################")
            print("#                                   #")
            print("#              LAYER 1              #")
            print("#                                   #")
            print("#####################################")

            os.system("./nemo ./"+setup.target_file+" ./"+setup.target_file+"_1")

            unroute_net = read_route_file('Route.txt')

            netlist = NETLIST()
            netlist.read_netlist(setup.filepath+"conf/"+setup.target_file)
            netlist.multiply_1000()
            setup.update_com_boundary( netlist, 2)
            netlist.remove_unness_pin(setup.component)
            netlist.route_two_pin_net()
            netlist.focus_on_target_com(setup.component[ setup.target_component_index[0]][0], setup.component[setup.target_component_index[1]][0])
            netlist.find_all_boundary( setup.track_width, 2)

            if len(unroute_net)!=1:
                print("ERROR cannot route")
                continue

            combine_the_same_part_gdt(setup)

            test_time += 1
            index=0
            while 1==1:
                if os.path.isfile("./learning_data/layer0/data_"+str(index)+".gdt"):
                    index+=1
                else:
                    os.system("cp "+setup.target_file+"_0.gdt"+" "+"./learning_data/layer0/data_"+str(index)+".gdt")
                    os.system("cp "+setup.target_file+"_1.gdt"+" "+"./learning_data/layer1/data_"+str(index)+".gdt")
                    os.system("cp "+setup.target_file+"_total.gds"+" "+"./learning_data/total_layout/data_"+str(index)+".gds")
                    os.system("cp "+setup.target_file+"_total.gdt"+" "+"./learning_data/total_layout/data_"+str(index)+".gdt")
                    break

            #get_fanout_position(netlist, setup, 0)
            
    os.system("rm ./"+setup.target_file+".gdfm")
    os.system("rm ./"+setup.target_file+".obs")
    os.system("rm ./"+setup.target_file+".pgr")
    os.system("rm ./"+setup.target_file+"_0.gds")
    os.system("rm ./"+setup.target_file+"_0.gdt")
    os.system("rm ./"+setup.target_file+"_1.gds")
    os.system("rm ./"+setup.target_file+"_1.gdt")
    os.system("rm ./"+setup.target_file+"_total.gds")
    os.system("rm ./"+setup.target_file+"_total.gdt")
    os.system("rm ./"+setup.target_file+"_obs.gds")
    os.system("rm ./"+setup.target_file+"_obs.gdt")
    
    print('END')
