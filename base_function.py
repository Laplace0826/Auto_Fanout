import numpy as np
import cv2
import os
import random
import copy

def read_netlist_file(file_path):
    
    pin = []
    obs = []
    
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
                pin.append(one_net)
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
            obs.append([layer,x,y,width,height])
    
    return pin, obs

def read_config_file(filepath):
    
    f_read = open(filepath+".conf",'r')
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

    index_colon=text[2].find(':')
    usable_layer=text[2][index_colon+1:]
    
    strategy = []
    index_colon=text[3].find(':')
    text[3]=text[3][index_colon+1:]
    index_space=0
    while index_space!=-1:
        index_space=text[3].find(' ')
        if index_space!=-1:
            strategy_name=text[3][0:index_space]
            text[3]=text[3][index_space+1:]
            strategy.append(strategy_name)
        elif index_space==-1:
            strategy_name=text[3]
            strategy.append(strategy_name)
    
    com = []
    com.append(cpu)
    for i in range(len(ddr)):
        com.append(ddr[i])
    
    return com,usable_layer,strategy

def read_gdt_file(file_path,track_width):
    f_read = open(file_path,'r')
    text = f_read.readlines()
    f_read.close()
    
    del text[0]
    del text[0]
    del text[0]
    del text[0]
    del text[len(text)-1]
    del text[len(text)-1]
    
    for line in range(len(text)):
        text[line]=text[line].strip('\n')
        text[line]=text[line].strip('\t')

    # remove unroute pins
    clear=0  
    while clear==0:
        pin_a_find=0
        clear=1
        for i in range(len(text)):
            string_split = text[i].split(" ", 9)           
            pin=string_split[1][2:]
            if pin=="1":
                if pin_a_find==0:
                    pin_a_find=1
                elif pin_a_find==1:
                    pin_a_find=2
                elif pin_a_find==2:
                    del text[i-1]
                    del text[i-2]
                    clear=0
                    break
            elif pin=="100":
                del text[i]
                clear=0
                break
            elif pin=="0":
                pin_a_find=0
    
    # get fanout position
    data_one_block=[]
    data_pin=[]
    start_find=0
    for i in range(len(text)):
        string_split = text[i].split(" ", 9)
        string_split[1]=string_split[1][2:]
        string_split[2]=string_split[2][3:]
        string_split[9]=string_split[9][:len(string_split[9])-3]
        string_split[2]=int(float(string_split[2])*1000/2+track_width/2)
        string_split[3]=int(float(string_split[3])*1000/2+track_width/2)
        string_split[4]=int(float(string_split[4])*1000/2+track_width/2)
        string_split[5]=int(float(string_split[5])*1000/2+track_width/2)
        string_split[6]=int(float(string_split[6])*1000/2+track_width/2)
        string_split[7]=int(float(string_split[7])*1000/2+track_width/2)
        string_split[8]=int(float(string_split[8])*1000/2+track_width/2)
        string_split[9]=int(float(string_split[9])*1000/2+track_width/2)

        if string_split[1]=='1' and start_find==0:
            data_one_block=[[string_split[2],string_split[3]]]
            start_find=1
        elif string_split[1]=='1' and start_find==1:
            data_one_block.append([string_split[2],string_split[3]])
            start_find=2
        elif string_split[1]=='0' and start_find==2:
            data_one_block.append([string_split[2],string_split[3],string_split[6],string_split[7]])
            if i==len(text)-1:
                data_pin.append(data_one_block)
        elif string_split[1]=='1' and start_find==2:
            data_pin.append(data_one_block)
            data_one_block=[[string_split[2],string_split[3]]]
            start_find=1

            
    return data_pin

def multiply_1000(data_pin_pair,data_obs_stat):
    for i in range(len(data_pin_pair)):
        for j in range(len(data_pin_pair[i])):
            data_pin_pair[i][j][2]=str(int(float(data_pin_pair[i][j][2])*1000))
            data_pin_pair[i][j][3]=str(int(float(data_pin_pair[i][j][3])*1000))
    for i in range(len(data_obs_stat)):
        data_obs_stat[i][1]=str(int(float(data_obs_stat[i][1])*1000))
        data_obs_stat[i][2]=str(int(float(data_obs_stat[i][2])*1000))
        data_obs_stat[i][3]=str(int(float(data_obs_stat[i][3])*1000))
        data_obs_stat[i][4]=str(int(float(data_obs_stat[i][4])*1000))
    return data_pin_pair,data_obs_stat

def remove_unness_pin(data_pin_pair,com):
    clear = 0
    while clear==0:
        clear=1
        for i in range(len(data_pin_pair)):
            if clear==0:
                break
            if len(data_pin_pair[i])<=1:
                del data_pin_pair[i]
                clear=0
                break
            for j in range(len(data_pin_pair[i])):
                check=0
                for k in range(len(com)):
                    if data_pin_pair[i][j][0]==com[k]:
                        check=1
                if check==0:
                    del data_pin_pair[i][j]
                    clear=0
                    break
    return data_pin_pair

def focus_on_one_component(data_pin_pair,com_name):
    clear = 0
    while clear==0:
        clear=1
        for i in range(len(data_pin_pair)):
            check=0
            for j in range(len(data_pin_pair[i])):
                if data_pin_pair[i][j][0]==com_name:
                    check=1
            if check==0:
                del data_pin_pair[i]
                clear=0
                break
    for i in range(len(data_pin_pair)):
        if data_pin_pair[i][0][0]!=com_name:
            for j in range(len(data_pin_pair[i])):
                if data_pin_pair[i][j][0]==com_name:
                    (data_pin_pair[i][0],data_pin_pair[i][j])=(data_pin_pair[i][j],data_pin_pair[i][0])
    return data_pin_pair

def change_index_by_coordinate(data_pin_pair,direction):
    for i in range(len(data_pin_pair)):
       for j in range(i+1,len(data_pin_pair)):
           if direction=="x":
               if data_pin_pair[i][0][2]>data_pin_pair[j][0][2]:
                   (data_pin_pair[i],data_pin_pair[j])=(data_pin_pair[j],data_pin_pair[i])
           if direction=="y":
               if data_pin_pair[i][0][3]>data_pin_pair[j][0][3]:
                   (data_pin_pair[i],data_pin_pair[j])=(data_pin_pair[j],data_pin_pair[i])
    return data_pin_pair

def find_boundary( data_pin_pair, com_name, track_width, num_of_out_component_track):
    max_x=0
    min_x=9999999
    max_y=0
    min_y=9999999
    
    boundary=[min_x,max_x,min_y,max_y]

    for i in range(len(data_pin_pair)):
        for j in range(len(data_pin_pair[i])):
            if data_pin_pair[i][j][0]==com_name:
                if int(data_pin_pair[i][j][2])>boundary[1]:
                    boundary[1]=int(data_pin_pair[i][j][2])
                if int(data_pin_pair[i][j][2])<boundary[0]:
                    boundary[0]=int(data_pin_pair[i][j][2])
                if int(data_pin_pair[i][j][3])>boundary[3]:
                    boundary[3]=int(data_pin_pair[i][j][3])
                if int(data_pin_pair[i][j][3])<boundary[2]:
                    boundary[2]=int(data_pin_pair[i][j][3])

    boundary[0]=boundary[0]-int(track_width*num_of_out_component_track)
    boundary[1]=boundary[1]+int(track_width*num_of_out_component_track)
    boundary[2]=boundary[2]-int(track_width*num_of_out_component_track)
    boundary[3]=boundary[3]+int(track_width*num_of_out_component_track)
    
    return boundary

def remove_out_of_the_boundary_obs(data_obs_stat,boundary,layer):
    clear=0
    while clear==0:
        clear=1
        for i in range(len(data_obs_stat)):
            if int(data_obs_stat[i][0])!= layer or int(data_obs_stat[i][1])<boundary[0] or int(data_obs_stat[i][1])>boundary[1] or int(data_obs_stat[i][2])<boundary[2] or int(data_obs_stat[i][2])>boundary[3]:
                del data_obs_stat[i]
                clear=0
                break
    return data_obs_stat

def remove_not_this_layer_obs(data_obs_stat,layer):
    clear=0
    while clear==0:
        clear=1
        for i in range(len(data_obs_stat)):
            if int(data_obs_stat[i][0])!= layer:
                del data_obs_stat[i]
                clear=0
                break
    return data_obs_stat

def trans_to_pic(setup, netlist, filepath):
    boundary = copy.deepcopy(netlist.boundary)
    
    # read gdt file
    data_pin=read_gdt_file(filepath, setup.track_width)
    
    # clear out of boundary pin
    for i in range(len(data_pin)):
        if data_pin[i][0][0] < boundary[0] or data_pin[i][0][0] > boundary[1] or data_pin[i][0][1] < boundary[2] or data_pin[i][0][1] > boundary[3]:
            del data_pin[i][0]
        if data_pin[i][1][0] < boundary[0] or data_pin[i][1][0] > boundary[1] or data_pin[i][1][1] < boundary[2] or data_pin[i][1][1] > boundary[3]:
            del data_pin[i][1]
            
    # count the max number fanout side
    fanout_side=[0,0,0,0] #up down left right
    for i in range(len(data_pin)):
        for j in range(1,len(data_pin[i])):
            # up
            if data_pin[i][j][1] < boundary[3] and data_pin[i][j][3] > boundary[3]:
                fanout_side[0]+=1
                break
            # down
            elif data_pin[i][j][1] < boundary[2] and data_pin[i][j][3] > boundary[2]:
                fanout_side[1]+=1
                break
            # left
            elif data_pin[i][j][0] < boundary[0] and data_pin[i][j][2] > boundary[0]:
                fanout_side[2]+=1
                break
            # right
            elif data_pin[i][j][0] < boundary[1] and data_pin[i][j][2] > boundary[1]:
                fanout_side[3]+=1
                break
    max_side = int(fanout_side.index(max(fanout_side)))

    all_on_one_side=0
    for i in range(len(fanout_side)):
        if i==max_side:
            continue
        if fanout_side[i]!=0:
            all_on_one_side+=1

    # control the boundary to make all the fanout on single side
    while all_on_one_side!=0:
        boundary[0]=boundary[0]-int(setup.track_width)
        boundary[1]=boundary[1]+int(setup.track_width)
        boundary[2]=boundary[2]-int(setup.track_width)
        boundary[3]=boundary[3]+int(setup.track_width)
        # check all side
        fanout_side=[0,0,0,0] #up down left right
        for i in range(len(data_pin)):
            for j in range(1,len(data_pin[i])):
                # up
                if data_pin[i][j][1] < boundary[3] and data_pin[i][j][3] > boundary[3]:
                    fanout_side[0]+=1
                    break
                # down
                elif data_pin[i][j][1] < boundary[2] and data_pin[i][j][3] > boundary[2]:
                    fanout_side[1]+=1
                    break
                # left
                elif data_pin[i][j][0] < boundary[0] and data_pin[i][j][2] > boundary[0]:
                    fanout_side[2]+=1
                    break
                # right
                elif data_pin[i][j][0] < boundary[1] and data_pin[i][j][2] > boundary[1]:
                    fanout_side[3]+=1
                    break
        all_on_one_side=0
        for i in range(len(fanout_side)):
            if i==max_side:
                continue
            if fanout_side[i]!=0:
                all_on_one_side+=1
        
    max_side=int(fanout_side.index(max(fanout_side)))
    for i in range(len(data_pin)):
        print(data_pin[i])
    # clear out of boundary block
    clear=0
    while clear==0:
        clear=1
        for i in range(len(data_pin)):
            if clear==0:
                break
            for j in range(1,len(data_pin[i])):
                # all outside
                if data_pin[i][j][2] < boundary[0] or data_pin[i][j][0] > boundary[1] or data_pin[i][j][3] < boundary[2] or data_pin[i][j][1] > boundary[3]:
                    del data_pin[i][j]
                    clear=0
                    break
                # all inside
                if data_pin[i][j][0] > boundary[0] and data_pin[i][j][2] < boundary[1] and data_pin[i][j][1] > boundary[2] and data_pin[i][j][3] < boundary[3]:
                    del data_pin[i][j]
                    clear=0
                    break

    clear=0
    while clear==0:
        clear=1
        for i in range(len(data_pin)):
            if len(data_pin[i])>2:
                del data_pin[i][2]
                clear=0
                break
            elif len(data_pin[i])<2:
                return 1

    for i in range(len(data_pin)):
        for j in range(i+1,len(data_pin)):
            if max_side==0 or max_side==1:
                if data_pin[i][1][0]>data_pin[j][1][0]:
                    (data_pin[i],data_pin[j])=(data_pin[j],data_pin[i])
            if max_side==2 or max_side==3:
                if data_pin[i][1][1]>data_pin[j][1][1]:
                    (data_pin[i],data_pin[j])=(data_pin[j],data_pin[i])

    # accurate the pin position
    for i in range(len(data_pin)):
        # up
        if data_pin[i][1][1] <= boundary[3] and data_pin[i][1][3] >= boundary[3]:
            data_pin[i][1][1]=boundary[3]
            del data_pin[i][1][2]
            del data_pin[i][1][2]
        # down
        elif data_pin[i][1][1] <= boundary[2] and data_pin[i][1][3] >= boundary[2]:
            data_pin[i][1][1]=boundary[2]
            del data_pin[i][1][2]
            del data_pin[i][1][2]
        # left
        elif data_pin[i][1][0] <= boundary[0] and data_pin[i][1][2] >= boundary[0]:
            data_pin[i][1][0]=boundary[0]
            del data_pin[i][1][3]
            del data_pin[i][1][2]
        # right
        elif data_pin[i][1][0] <= boundary[1] and data_pin[i][1][2] >= boundary[1]:
            data_pin[i][1][0]=boundary[1]
            del data_pin[i][1][3]
            del data_pin[i][1][2]
        else:
            return 2

    return 0

def trans_to_pic_old(file_path,pic_size,data_pin_pair,data_obs_stat,track_width,boundary):
    """

    # make matrix
        
    # column
    data_pin_pair = change_index_by_coordinate(data_pin_pair,"x")
    
    # add pin column
    column_information = [[int(data_pin_pair[0][0][2]),0,0]]
    now_position=int(data_pin_pair[0][0][2])
    for i in range(len(data_pin_pair)):
        if int(data_pin_pair[i][0][2])>now_position:
            column_information.append([int(data_pin_pair[i][0][2]),0,0])            
            now_position=int(data_pin_pair[i][0][2])

    # add fanout column
    found_track=0
    for i in range(len(data_pin)):
        found_track=0
        if int(data_pin[i][1][0]) < column_information[0][0]-track_width*3:
            column_information.insert(0,[int(data_pin[i][1][0]),0,0])
            found_track=1
            continue
        for j in range(len(column_information)-1):
            if int(data_pin[i][1][0])>column_information[j][0]+track_width*3 and int(data_pin[i][1][0])<column_information[j+1][0]-track_width*3 :
                column_information.insert(j+1,[int(data_pin[i][1][0]),0,0])
                found_track=1
                break
        if int(data_pin[i][1][0])>column_information[len(column_information)-1][0]+track_width*3 and found_track==0:
            column_information.append([int(data_pin[i][1][0]),0,0])
            
    # add obs column
    for i in range(len(data_obs_stat)):
        if int(data_obs_stat[i][1]) < column_information[0][0]-track_width*3:
            column_information.insert(0,[int(data_obs_stat[i][1]),0,0])
            continue
        for j in range(len(column_information)-1):
            if int(data_obs_stat[i][1])>column_information[j][0]+track_width*3 and int(data_obs_stat[i][1])<column_information[j+1][0]-track_width*3 :
                column_information.insert(j+1,[int(data_obs_stat[i][1]),0,0])
                break
  
    # count capacity
    for i in range(1,len(column_information)):
        column_information[i][1]=int((int((column_information[i][0]-column_information[i-1][0])/track_width)-1)/2)

    # expand all column
    while 1==1:
        clear=0
        for i in range(1,len(column_information)):
            if column_information[i][1]>0:
                column_information[i][1]-=1
                column_information.insert(i,[column_information[i][0]-track_width*2,0,0])            
                clear=1
                break
        # count capacity
        column_information[0][1]=0
        for i in range(1,len(column_information)):
            column_information[i][1]=int((int((column_information[i][0]-column_information[i-1][0])/track_width)-1)/2)
        
        if clear==0:
            break
    
    for i in range(len(column_information)):
        column_information[i][2]=i
    
    # row
    data_pin_pair = change_index_by_coordinate(data_pin_pair,"y")
   
    # add pin row
    row_information = [[int(data_pin_pair[0][0][3]),0,0]]
    now_position=int(data_pin_pair[0][0][3])
    for i in range(len(data_pin_pair)):
        if int(data_pin_pair[i][0][3])>now_position:
            row_information.append([int(data_pin_pair[i][0][3]),0,0])            
            now_position=int(data_pin_pair[i][0][3])

    # add fanout row
    found_track=0
    for i in range(len(data_pin)):
        found_track=0
        if int(data_pin[i][1][1]) < row_information[0][0]-track_width*3:
            row_information.insert(0,[int(data_pin[i][1][1]),0,0])
            found_track=1
            continue
        for j in range(len(row_information)-1):
            if int(data_pin[i][1][1])>row_information[j][0]+track_width*3 and int(data_pin[i][1][1])<row_information[j+1][0]-track_width*3 :
                row_information.insert(j+1,[int(data_pin[i][1][1]),0,0])
                found_track=1
                break
        if int(data_pin[i][1][1])>row_information[len(row_information)-1][0]+track_width*3 and found_track==0:
            row_information.append([int(data_pin[i][1][1]),0,0])
            
    # add obs row
    for i in range(len(data_obs_stat)):
        if int(data_obs_stat[i][2]) < row_information[0][0]-track_width*3:
            row_information.insert(0,[int(data_obs_stat[i][2]),0,0])
            continue
        for j in range(len(row_information)-1):
            if int(data_obs_stat[i][2])>row_information[j][0]+track_width*3 and int(data_obs_stat[i][2])<row_information[j+1][0]-track_width*3 :
                row_information.insert(j+1,[int(data_obs_stat[i][2]),0,0])
                break

    # count capacity
    for i in range(1,len(row_information)):
        row_information[i][1]=int((int((row_information[i][0]-row_information[i-1][0])/track_width)-1)/2)

    # expand all column
    while 1==1:
        clear=0
        for i in range(1,len(row_information)):
            if row_information[i][1]>0:
                row_information[i][1]-=1
                row_information.insert(i,[row_information[i][0]-track_width*2,0,0])            
                clear=1
                break
        # count capacity
        row_information[0][1]=0
        for i in range(1,len(row_information)):
            row_information[i][1]=int((int((row_information[i][0]-row_information[i-1][0])/track_width)-1)/2)
        
        if clear==0:
            break

    for i in range(len(row_information)):
        row_information[i][2]=i

    # make matrix

    if len(column_information)>=pic_size or len(row_information)>=pic_size:
        print(str(len(column_information))+" "+str(len(row_information)))
        return 2

    img = np.zeros((pic_size,pic_size,3),dtype='int16')
    img[:]=0

    # boundary
    for x in range(pic_size):
        for y in range(pic_size):
            if x>len(column_information) or y>len(row_information):
                img[x][y][0]=255
                img[x][y][1]=255

    # obs
    for i in range(len(data_obs_stat)):
        column=0
        row=0
        for column_index in range(len(column_information)):
            if column_index==len(column_information)-1:
                column=column_index
                break
            elif int(data_obs_stat[i][1])>=column_information[column_index][0] and int(data_obs_stat[i][1])<column_information[column_index+1][0]:
                column=column_index
                break
        for row_index in range(len(row_information)):
            if row_index==len(row_information)-1:
                row=row_index
                break
            elif int(data_obs_stat[i][2])>=row_information[row_index][0] and int(data_obs_stat[i][2])<row_information[row_index+1][0]:
                row=row_index
                break
        img[column][row][0]=255
        img[column][row][1]=255
        
    # pin
    for i in range(len(data_pin_pair)):
        column=0
        row=0
        for column_index in range(len(column_information)):
            if column_index==len(column_information)-1:
                column=column_index
                break
            elif int(data_pin_pair[i][0][2])>=column_information[column_index][0] and int(data_pin_pair[i][0][2])<column_information[column_index+1][0]:
                column=column_index
                break
        for row_index in range(len(row_information)):
            if row_index==len(row_information)-1:
                row=row_index
                break
            elif int(data_pin_pair[i][0][3])>=row_information[row_index][0] and int(data_pin_pair[i][0][3])<row_information[row_index+1][0]:
                row=row_index
                break
        img[column][row][0]=100
        img[column][row][1]=0

    # pin pair
    dis_for_pin_pair=int(255/(len(data_pin)+5))
    start_for_pin_pair=3*dis_for_pin_pair
    for i in range(len(data_pin)):
        for j in range(len(data_pin[i])):
            column=0
            row=0
            for column_index in range(len(column_information)):
                if column_index==len(column_information)-1:
                    column=column_index
                    break
                elif int(data_pin[i][j][0])>=column_information[column_index][0] and int(data_pin[i][j][0])<column_information[column_index+1][0]:
                    column=column_index
                    break
            for row_index in range(len(row_information)):
                if row_index==len(row_information)-1:
                    row=row_index
                    break
                elif int(data_pin[i][j][1])>=row_information[row_index][0] and int(data_pin[i][j][1])<row_information[row_index+1][0]:
                    row=row_index
                    break
            img[column][row][0]=50
            img[column][row][1]=start_for_pin_pair
            start_for_pin_pair+=dis_for_pin_pair

    index_for_pic=0
    while 1==1:
        if os.path.isfile('./learning_data/routable/num'+str(index_for_pic)+".jpg"):
            index_for_pic+=1
        else:
            cv2.imwrite('./learning_data/routable/num'+str(index_for_pic)+'.jpg', img)
            break

    # make unroutable matrix

    img = np.zeros((pic_size,pic_size,3),dtype='int16')
    img[:]=0
    
    # boundary
    for x in range(pic_size):
        for y in range(pic_size):
            if x>len(column_information) or y>len(row_information):
                img[x][y][0]=255
                img[x][y][1]=255

    # obs
    for i in range(len(data_obs_stat)):
        column=0
        row=0
        for column_index in range(len(column_information)):
            if column_index==len(column_information)-1:
                column=column_index
                break
            elif int(data_obs_stat[i][1])>=column_information[column_index][0] and int(data_obs_stat[i][1])<column_information[column_index+1][0]:
                column=column_index
                break
        for row_index in range(len(row_information)):
            if row_index==len(row_information)-1:
                row=row_index
                break
            elif int(data_obs_stat[i][2])>=row_information[row_index][0] and int(data_obs_stat[i][2])<row_information[row_index+1][0]:
                row=row_index
                break
        img[column][row][0]=255
        img[column][row][1]=255
        
    # pin
    for i in range(len(data_pin_pair)):
        column=0
        row=0
        for column_index in range(len(column_information)):
            if column_index==len(column_information)-1:
                column=column_index
                break
            elif int(data_pin_pair[i][0][2])>=column_information[column_index][0] and int(data_pin_pair[i][0][2])<column_information[column_index+1][0]:
                column=column_index
                break
        for row_index in range(len(row_information)):
            if row_index==len(row_information)-1:
                row=row_index
                break
            elif int(data_pin_pair[i][0][3])>=row_information[row_index][0] and int(data_pin_pair[i][0][3])<row_information[row_index+1][0]:
                row=row_index
                break
        img[column][row][0]=100
        img[column][row][1]=0
    
    # ramdon change pin position
    for i in range(int(len(data_pin)/2)):
        change_a=random.randint(0, len(data_pin)-1)
        change_b=random.randint(0, len(data_pin)-1)
        (data_pin[change_a][1],data_pin[change_b][1])=(data_pin[change_b][1],data_pin[change_a][1])
    
    # pin pair
    dis_for_pin_pair=int(255/(len(data_pin)+5))
    start_for_pin_pair=3*dis_for_pin_pair
    for i in range(len(data_pin)):
        for j in range(len(data_pin[i])):
            column=0
            row=0
            for column_index in range(len(column_information)):
                if column_index==len(column_information)-1:
                    column=column_index
                    break
                elif int(data_pin[i][j][0])>=column_information[column_index][0] and int(data_pin[i][j][0])<column_information[column_index+1][0]:
                    column=column_index
                    break
            for row_index in range(len(row_information)):
                if row_index==len(row_information)-1:
                    row=row_index
                    break
                elif int(data_pin[i][j][1])>=row_information[row_index][0] and int(data_pin[i][j][1])<row_information[row_index+1][0]:
                    row=row_index
                    break
            img[column][row][0]=50
            img[column][row][1]=start_for_pin_pair
            start_for_pin_pair+=dis_for_pin_pair        
        
    index_for_pic=0
    while 1==1:
        if os.path.isfile('./learning_data/unroutable/num'+str(index_for_pic)+".jpg"):
            index_for_pic+=1
        else:
            cv2.imwrite('./learning_data/unroutable/num'+str(index_for_pic)+'.jpg', img)
            break
    return 0
    """

def trans_input_to_matrix(pic_size,data_pin_pair,data_obs_stat,track_width,boundary):

    # column
    data_pin_pair = change_index_by_coordinate(data_pin_pair,"x")
    
    # add pin column
    column_information = [[int(data_pin_pair[0][0][2]),0,0]]
    now_position=int(data_pin_pair[0][0][2])
    for i in range(len(data_pin_pair)):
        if int(data_pin_pair[i][0][2])>now_position:
            column_information.append([int(data_pin_pair[i][0][2]),0,0])            
            now_position=int(data_pin_pair[i][0][2])

    # add obs column
    for i in range(len(data_obs_stat)):
        if int(data_obs_stat[i][1]) < column_information[0][0]-track_width*3:
            column_information.insert(0,[int(data_obs_stat[i][1]),0,0])
            continue
        for j in range(len(column_information)-1):
            if int(data_obs_stat[i][1])>column_information[j][0]+track_width*3 and int(data_obs_stat[i][1])<column_information[j+1][0]-track_width*3 :
                column_information.insert(j+1,[int(data_obs_stat[i][1]),0,0])
                break
            
    for _ in range(7):
        column_information.insert(0,[column_information[0][0]-track_width*2,0,0])
    for _ in range(7):
        column_information.insert(len(column_information),[column_information[len(column_information)-1][0]+track_width*2,0,0])

    # count capacity
    for i in range(1,len(column_information)):
        column_information[i][1]=int((int((column_information[i][0]-column_information[i-1][0])/track_width)-1)/2)

    # expand all column
    while 1==1:
        clear=0
        for i in range(1,len(column_information)):
            if column_information[i][1]>0:
                column_information[i][1]-=1
                column_information.insert(i,[column_information[i][0]-track_width*2,0,0])            
                clear=1
                break
        # count capacity
        column_information[0][1]=0
        for i in range(1,len(column_information)):
            column_information[i][1]=int((int((column_information[i][0]-column_information[i-1][0])/track_width)-1)/2)
        
        if clear==0:
            break
    
    for i in range(len(column_information)):
        column_information[i][2]=i
    
    # row
    data_pin_pair = change_index_by_coordinate(data_pin_pair,"y")
   
    # add pin row
    row_information = [[int(data_pin_pair[0][0][3]),0,0]]
    now_position=int(data_pin_pair[0][0][3])
    for i in range(len(data_pin_pair)):
        if int(data_pin_pair[i][0][3])>now_position:
            row_information.append([int(data_pin_pair[i][0][3]),0,0])            
            now_position=int(data_pin_pair[i][0][3])

    # add obs row
    for i in range(len(data_obs_stat)):
        if int(data_obs_stat[i][2]) < row_information[0][0]-track_width*3:
            row_information.insert(0,[int(data_obs_stat[i][2]),0,0])
            continue
        for j in range(len(row_information)-1):
            if int(data_obs_stat[i][2])>row_information[j][0]+track_width*3 and int(data_obs_stat[i][2])<row_information[j+1][0]-track_width*3 :
                row_information.insert(j+1,[int(data_obs_stat[i][2]),0,0])
                break
            
    for _ in range(7):
        row_information.insert(0,[row_information[0][0]-track_width*2,0,0])
    for _ in range(7):
        row_information.insert(len(row_information),[row_information[len(row_information)-1][0]+track_width*2,0,0])
        
    # count capacity
    for i in range(1,len(row_information)):
        row_information[i][1]=int((int((row_information[i][0]-row_information[i-1][0])/track_width)-1)/2)

    # expand all column
    while 1==1:
        clear=0
        for i in range(1,len(row_information)):
            if row_information[i][1]>0:
                row_information[i][1]-=1
                row_information.insert(i,[row_information[i][0]-track_width*2,0,0])            
                clear=1
                break
        # count capacity
        row_information[0][1]=0
        for i in range(1,len(row_information)):
            row_information[i][1]=int((int((row_information[i][0]-row_information[i-1][0])/track_width)-1)/2)
        
        if clear==0:
            break

    for i in range(len(row_information)):
        row_information[i][2]=i

    # make matrix

    if len(column_information)>=pic_size or len(row_information)>=pic_size:
        print(str(len(column_information))+" "+str(len(row_information)))
        return 2
    
    img = np.zeros((pic_size,pic_size,3),dtype='int16')
    img[:]=0
    
    # only process two pin net
    
    clear=0
    while clear==0:
        clear=1
        for i in range(len(data_pin_pair)):
            if len(data_pin_pair[i])>2:
                del data_pin_pair[i]
                clear=0
                break
    # boundary
    for x in range(pic_size):
        for y in range(pic_size):
            if x>len(column_information) or y>len(row_information):
                img[x][y][0]=255
                img[x][y][1]=255

    # obs
    for i in range(len(data_obs_stat)):
        column=0
        row=0
        for column_index in range(len(column_information)):
            if column_index==len(column_information)-1:
                column=column_index
                break
            elif int(data_obs_stat[i][1])>=column_information[column_index][0] and int(data_obs_stat[i][1])<column_information[column_index+1][0]:
                column=column_index
                break
        for row_index in range(len(row_information)):
            if row_index==len(row_information)-1:
                row=row_index
                break
            elif int(data_obs_stat[i][2])>=row_information[row_index][0] and int(data_obs_stat[i][2])<row_information[row_index+1][0]:
                row=row_index
                break
        img[column][row][0]=255
        img[column][row][1]=255
        
    # pin
    for i in range(len(data_pin_pair)):
        column=0
        row=0
        for column_index in range(len(column_information)):
            if column_index==len(column_information)-1:
                column=column_index
                break
            elif int(data_pin_pair[i][0][2])>=column_information[column_index][0] and int(data_pin_pair[i][0][2])<column_information[column_index+1][0]:
                column=column_index
                break
        for row_index in range(len(row_information)):
            if row_index==len(row_information)-1:
                row=row_index
                break
            elif int(data_pin_pair[i][0][3])>=row_information[row_index][0] and int(data_pin_pair[i][0][3])<row_information[row_index+1][0]:
                row=row_index
                break
        img[column][row][0]=100
        img[column][row][1]=0
    
    index_for_pic=0
    while 1==1:
        if os.path.isfile('./use_for_MCTS_num'+str(index_for_pic)+".jpg"):
            index_for_pic+=1
        else:
            cv2.imwrite('./use_for_MCTS_num'+str(index_for_pic)+'.jpg', img)
            break
        
    return img

def cross(p1,p2,p3):
    x1=p2[0]-p1[0]
    y1=p2[1]-p1[1]
    x2=p3[0]-p1[0]
    y2=p3[1]-p1[1]
    return x1*y2-x2*y1     

def segment(p1,p2,p3,p4):

    if(max(p1[0],p2[0])>=min(p3[0],p4[0]) and max(p3[0],p4[0])>=min(p1[0],p2[0]) and max(p1[1],p2[1])>=min(p3[1],p4[1]) and max(p3[1],p4[1])>=min(p1[1],p2[1])):
        if(cross(p1,p2,p3)*cross(p1,p2,p4)<=0 and cross(p3,p4,p1)*cross(p3,p4,p2)<=0):
            return 1
        else:
            return 0
    else:
        return 0

def count_crossing_number_v1(data_pin):

    total_crossing_number=0
    
    for one_pin in range(len(data_pin)):
        (data_pin[one_pin],data_pin[0])=(data_pin[0],data_pin[one_pin])
        count=0
        for i in range(1,len(data_pin)):
            x=segment(data_pin[0][0],data_pin[0][1],data_pin[i][0],data_pin[i][1])
            count+=x
        total_crossing_number+=count
    
    return total_crossing_number

def count_crossing_number(data_pin):

    total_crossing_number=0
    
    for one_pin in range(len(data_pin)):
        (data_pin[one_pin],data_pin[0])=(data_pin[0],data_pin[one_pin])
        count=0
        for i in range(1,len(data_pin)):
            x=segment(data_pin[0][0],data_pin[0][1],data_pin[i][0],data_pin[i][1])
            count+=x
        total_crossing_number+=count
    
    return total_crossing_number