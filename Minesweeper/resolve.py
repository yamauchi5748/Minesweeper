from tkinter import *
import time
import random
import main 

class resoleve():
    
    def __init__(self, game_frame, height, frame_height, width, frame_width, frame_list, bomb_num):
        self.game_frame = game_frame
        self.height = height
        self.frame_height = frame_height
        self.width = width
        self.frame_width = frame_width
        self.frame_list = frame_list
        self.bomb_num = bomb_num
        self.font_size = 16
        self.bomb_flag_num = 0
        self.clear_math_num = 0

    def getConfirmframeList(self,frame):
        undicide_list = []
        is_bomb = False
        if frame.bomb_count > 0 :
            confirm_math_num = 0
            confirm_bomb_num = 0
            around_list = self.searchAround(frame.num)
            for i in around_list :
                if self.frame_list[i].cget('bg') == 'yellow' :
                    confirm_math_num += 1
                    confirm_bomb_num += 1
                elif self.frame_list[i].cget('relief') == 'ridge' :
                    confirm_math_num += 1
                else :
                    undicide_list.append(i)
            if len(undicide_list) > 1 :
                if (len(undicide_list) == frame.bomb_count) and (confirm_bomb_num == 0) :
                    is_bomb = True
                elif not (confirm_bomb_num == frame.bomb_count) :
                    undicide_list.clear()
            elif len(undicide_list) == 1 :
                if confirm_bomb_num == frame.bomb_count - 1 :
                    is_bomb = True

        return (undicide_list, is_bomb)

    def bombSet(self,frame):
        around_list = self.searchAround(frame.num)
        all_frame_num_list = [i for i in range(self.width*self.height)]
        all_frame_num_list.remove(frame.num)
        for i in around_list :
            all_frame_num_list.remove(i)
        bomb_list = random.sample(all_frame_num_list, self.bomb_num)
        for bomb_idx in bomb_list :
            self.frame_list[bomb_idx].is_bomb = True
            bomb_around_list = self.searchAround(bomb_idx)
            for i in bomb_around_list :
                self.frame_list[i].bomb_count += 1
    

    def openPanel(self,frame):
        if (frame.cget('relief') == "ridge") :
            return

        frame.configure(relief = 'ridge', bd = '1')
        current_num = frame.num
        around_list = self.searchAround(frame.num)
        self.clear_math_num += 1

        if frame.bomb_count == 0:
            self.autoOpen(around_list)
        else:
            self.setLabelColor(current_num)
        
    def setBombFlag(self, frame):
        if (frame.cget('relief')) == 'raised' :
            if self.bomb_flag_num + 1 > self.bomb_num:
                return
            frame.configure(relief = 'ridge', bd = '1', bg = 'yellow')
            self.bomb_flag_num += 1
        else:
            frame.configure(relief = 'raised',bd = '3', bg = 'LightGray')
            self.bomb_flag_num -= 1

    def is_clear(self):
        return (self.height*self.width - self.clear_math_num) == self.bomb_num
    
    def autoOpen(self,around_list):
        for i in around_list:
            if (self.frame_list[i].cget('relief')) == 'ridge' :
                continue
            self.clear_math_num += 1
            next_around_list = self.searchAround(i)
            self.frame_list[i].configure(relief = 'ridge', bd = '1')
            if self.frame_list[i].bomb_count == 0 :
                self.autoOpen(next_around_list)
            else :
                self.setLabelColor(i)

    def setLabelColor(self,num):
        frame = self.frame_list[num]
        bomb_count_label = Label(frame, text = frame.bomb_count, bg = 'LightGray', font=('Helvetica', str(self.font_size), 'bold'))

        if frame.bomb_count == 1:
            bomb_count_label.configure(fg = 'Blue')
        elif frame.bomb_count == 2:
            bomb_count_label.configure(fg = 'Green')
        elif frame.bomb_count == 3:
            bomb_count_label.configure(fg = 'orange')
        elif frame.bomb_count == 4:
            bomb_count_label.configure(fg = 'Red')
        elif frame.bomb_count == 5:
            bomb_count_label.configure(fg = 'red4')
        elif frame.bomb_count == 6:
            bomb_count_label.configure(fg = 'Orange Red4')
        elif frame.bomb_count == 7:
            bomb_count_label.configure(fg = 'Deep Pink4')
        elif frame.bomb_count == 8:
            bomb_count_label.configure(fg = 'Deep Pink4')
        bomb_count_label.place(width = self.frame_width, height = self.frame_height)
    

    def searchAround(self,num):
        around_list = []

        top_left = num - self.width - 1
        top = num - self.width
        top_right = num - self.width + 1
        right = num + 1 
        bottom_right = num + self.width + 1
        bottom = num + self.width
        bottom_left = num + self.width - 1
        left = num - 1

        if top_left >= 0 and top_left % self.width != self.width - 1 :
            around_list.append(top_left)
        if top >= 0 :
            around_list.append(top)
        if top_right >= 0 and top_right % self.width != 0 :
            around_list.append(top_right)
        if right % self.width != 0 :
            around_list.append(right)
        if bottom_right < self.width*self.height and bottom_right % self.width != 0 :
            around_list.append(bottom_right)
        if bottom < self.width*self.height and bottom < self.width * self.height :
            around_list.append(bottom)
        if bottom_left < self.width*self.height and bottom_left % self.width != self.width - 1 :
            around_list.append(bottom_left)
        if left >= 0 and left % self.width != self.width - 1 :
            around_list.append(left)
        return around_list

    def resetButtonReset(self):
        self.start_flag = True
        self.bomb_flag_num = 0
        self.clear_math_num = 0
        i = 0
        self.frame_list.clear()
        for x in range(self.height):
            for y in range(self.width):
                frame = Frame(self.game_frame, width = self.frame_width, height = self.frame_height, bd = 3, relief = 'raised', bg = 'LightGray')
                frame.num = i
                frame.bomb_count = 0
                frame.is_bomb = False
                self.frame_list.append(frame)
                frame.grid(row=x, column=y)
                i += 1
