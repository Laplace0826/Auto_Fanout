import numpy as np
import pandas as pd
import random
from copy import deepcopy

import config
import base_function as bf

class State:

    def __init__(self, matrix, pins, width, height, fanout_queue):
        self.matrix = matrix.copy()
        self.pins = pins.copy()
        self.width = width
        self.height = height
        self.fanout_queue = fanout_queue

    def __eq__(self, other):
        if (self.matrix == other.matrix).all():
            return True
        else:
            return False

    def get_available_actions(self):
        """
        觀察現有的layout返回可執行的動作，這些位置稱之為動作
        :return: 可行的動作
        """
        available_actions = []
        for i in range(len(self.pins)):
            if self.pins[i][3] == False:
                available_actions.append(self.pins[i][2])
        for x in range(self.width):
            for y in range(self.height):
                if self.matrix[x][y][0]==70 and self.matrix[x][y][1]==70:
                    available_actions.append(0)
        return available_actions

    def get_state_result(self):
        """
        返回狀態對應的結果
        :return: 返回predict probability, number of crossing
        """
        
        rand=random.random()
        if rand>=0.5:
            is_over=True
        else:
            is_over=False
            
        crossing_number=bf.count_crossing_number(self.pins)

        return is_over, crossing_number

    def get_next_state(self, action):
        """
        根據動作返回新的狀態
        :param action:[x y net_index]
        :return: 新的狀態
        """
        next_layout = self.matrix.copy()
        next_pins = self.next_pins.copy()
        next_layout[action[0]][action[1]]=action[2]
        if action[2]!=0:
            for i in range(len(next_pins)):
                if next_pins[i][2]==action[2]:
                    next_pins[i][3] = True
                    next_pins[i][4] = int(action[0])
                    next_pins[i][5] = int(action[1])
        next_state = State(next_layout, next_pins, self.width, self.height)
        return next_state

class Layout:
    
    def __init__(self, state=None):
        if state:
            matrix = state.matrix
            pins = state.pins
            width = state.width
            height = state.height
            fanout_queue = state.fanout_queue
        else:
            matrix = np.zeros((config.PIC_SIZE,config.PIC_SIZE,2),dtype='int')
            pins = []
            width = 0
            height = 0
            fanout_queue = []
        self.state=State(matrix, pins, width, height, fanout_queue)
    
    def case_input(self):
        f_read = open(config.filepath+config.target_file+"/conf/matrix",'r')
        text = f_read.readlines()
        f_read.close()
        
        pin_index=1
        for line in range(len(text)):
            text[line] = text[line].strip('\n')
            if line==0:
                self.state.width = int(text[line][0:text[line].find(',')])
                self.state.height = int(text[line][text[line].find(',')+1:])
            else:
                if text[line].find('PIN') != -1:
                    x = int(text[line][4:text[line].find(',')])
                    y = int(text[line][text[line].find(',')+1:len(text[line])-1])
                    self.add_pin(x, y)
                    self.state.pins.append([x,y, pin_index, False, 0, 0])
                    pin_index+=1
                if text[line].find('OBS') != -1:
                    x = int(text[line][4:text[line].find(',')])
                    y = int(text[line][text[line].find(',')+1:len(text[line])-1])
                    self.add_obs(x, y)

        for x in range(config.PIC_SIZE):
            for y in range(config.PIC_SIZE):
                if x >= self.state.width or y >= self.state.height:
                    self.add_obs(x, y)
        
        for x in range(config.PIC_SIZE):
            if x < self.state.width:
                self.add_fanout_resvered(x,0)

    def add_obs(self,x,y):
        self.state.matrix[x,y,0]=100
        self.state.matrix[x,y,1]=100
        
    def add_pin(self,x,y):
        self.state.matrix[x,y,0]=10
        self.state.matrix[x,y,1]=10
    
    def add_fanout_resvered(self,x,y):
        self.state.matrix[x,y,0]=70
        self.state.matrix[x,y,1]=70
    
    def add_fanout(self,x1,y1,x2,y2,net_index):
        self.state.matrix[x1,y1,0]=50
        self.state.matrix[x1,y1,1]=net_index
        self.state.matrix[x2,y2,0]=50
        self.state.matrix[x2,y2,1]=net_index
        
    def step(self, action):
        if action:
            self.state = self.state.get_next_state(action)
        return self.state
        
    def printLayout(self):
        print("============================== Layout ==============================")
        for x in range(self.state.width):
            for y in range(self.state.height):
                if self.state.matrix[x,y,0]==100 and self.state.matrix[x,y,1]==100:
                    print("X",end="")
                elif self.state.matrix[x,y,0]==0 and self.state.matrix[x,y,1]==0:
                    print(".",end="")
                elif self.state.matrix[x,y,0]==10 and self.state.matrix[x,y,1]==10:
                    print("O",end="")
                elif self.state.matrix[x,y,0]==70 and self.state.matrix[x,y,1]==70:
                    print("#",end="")
            print("")
        print("============================== Layout ==============================")

class Node:
    def __init__(self, state: State, parent=None):
        self.state = deepcopy(state)
        self.untried_actions = state.get_available_actions()
        self.parent = parent
        self.children = {}
        self.Q = 0  # 節點最終收益價值
        self.N = 0  # 節點被訪問的次數

    def weight_func(self, c_param=1.4):
        if self.N != 0:
            # -self.Q 
            w = -self.Q / self.N + c_param * np.sqrt(2 * np.log(self.parent.N) / self.N)
        else:
            w = 0.0
        return w

    @staticmethod
    def get_random_action(available_actions):
        action_number = len(available_actions)
        action_index = np.random.choice(range(action_number))
        return available_actions[action_index]

    def select(self, c_param=1.4):
        """
        根据当前的子节点情况选择最优的动作并返回子节点
        :param c_param: 探索参数用于探索的比例
        :return: 最优动作，最优动作下的子节点
        """
        weights = [child_node.weight_func(c_param) for child_node in self.children.values()]
        action = pd.Series(data=weights, index=self.children.keys()).idxmax()
        next_node = self.children[action]
        return action, next_node

    def expand(self):
        """
        擴展子節點並回傳剛擴展的子節點
        :return: 剛擴展的子節點
        """
        # 從沒有常識的節點中選擇
        action = self.untried_actions.pop()
        # 獲得下一步的局面
        next_matrix = self.state.matrix.copy()
        next_matrix[action[0]][action[1]] = action[2]
        next_pins = self.state.pins.copy()
        for i in range(len(next_pins)):
            if next_pins[i][2]==action[2]:
                del next_pins[i]
                break
        # 擴展出一個子節點
        state = State(next_matrix, next_pins, self.state.width, self.state.height)
        child_node = Node(state, self)
        self.children[action[2]] = child_node
        return child_node

    def update(self, winner):
        """
        经过模拟之后更新节点的价值和访问次数
        :param winner: 返回模拟的胜者
        :return:
        """
        self.N += 1
        opponent = get_opponent(self.state.player)

        if winner == self.state.player:
            self.Q += 1
        elif winner == opponent:
            self.Q -= 1

        if self.is_root_node():
            self.parent.update(winner)

    def rollout(self):
        """
        從當前節點進行MCTS模擬返回模擬結果
        :return: 模擬結果
        """
        current_state = deepcopy(self.state)
        while True:
            is_over, winner = current_state.get_state_result()
            if is_over:
                break
            available_actions = current_state.get_available_actions()
            action = Node.get_random_action(available_actions)
            current_state = current_state.get_next_state(action)
        return winner

    def is_full_expand(self):
        """
        检测节点是否是已经完全扩展了
        :return: 返回节点是否完全扩展
        """
        return len(self.untried_actions) == 0

    def is_root_node(self):
        """
        检测节点是否是根节点
        :return: 返回节点是否是根节点
        """
        return self.parent

class MCTS:
    def __init__(self):
        self.root = None
        self.current_node = None

    def __str__(self):
        return "MCTS"

    def simulation(self, count=1000):
        """
        用於模擬MCTS
        :param count: 模擬的次數
        :return:
        """
        for _ in range(count):
            leaf_node = self.simulation_policy()
            winner = leaf_node.rollout()
            leaf_node.update(winner)

    def simulation_policy(self):
        """
        模擬過程中找到當前的leaf node
        :return: leaf node
        """
        current_node = self.current_node
        while True:
            is_over, _ = current_node.state.get_state_result()
            if is_over:
                break
            if current_node.is_full_expand():
                _, current_node = current_node.select()
            else:
                return current_node.expand()
        leaf_node = current_node
        return leaf_node

    def take_action(self, current_state):
        """
        MCTS選擇最佳動作
        :param current_state: 當前狀態
        :return: 最佳動作
        """
        if not self.root: # 初始化
            self.root = Node(current_state, None)
            self.current_node = self.root
        else:
            for child_node in self.current_node.children.values():# 跳转到合适的状态
                if child_node.state == current_state:
                    self.current_node = child_node
                    break
            else:
                self.current_node = self.root

        self.simulation(100)
        action, next_node = self.current_node.select(0.0)
        self.current_node = next_node
        return action
