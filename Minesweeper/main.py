from tkinter import *
import gym
from gym.envs.registration import register
import pymongo
import time
import random
import numpy as np
import pandas as pd
import resolve
import learning

# mongodb へのアクセスを確立
client = pymongo.MongoClient('localhost', 27017)

# データベースを作成 (名前: my_database)
db = client["Minesweeper_database"]

# コレクションを作成 (名前: my_collection)
co = db["Minesweeper_data_001"]

#サンプルDFの作成
df = pd.DataFrame.from_dict(list(co.find({},{
    '_id' : False,
    'observation' : True,
    'action' : True,
    'score' : True
}))).astype(object)

class Main():

    def __init__(self):
        ###学習環境を登録
        register(
            id='Myenv-v0',
            entry_point='learning:MyEnv'
        )
        self.env = gym.make('Myenv-v0')
        # Qテーブルの初期化
        self.q_table = df

        ####メイン画面の生成####
        self.root = Tk()
        self.root.title("マインスイーパ")
        self.root.resizable(0,0)
        
        ###メニュー作成###
        self.menu_ROOT = Menu(self.root)
        self.root.configure(menu = self.menu_ROOT)
        
        self.menu_GAME = Menu(self.menu_ROOT, tearoff = False)
        self.menu_MODE = Menu(self.menu_ROOT, tearoff = False)
        self.menu_ROOT.add_cascade(label = '難易度(G)', under = 4, menu = self.menu_GAME)
        self.menu_ROOT.add_cascade(label = 'モード(R)', under = 4, menu = self.menu_MODE)
        
        self.menu_GAME.add_command(label = "初級(B)", under = 3, command = self.game_0level_set)
        self.menu_GAME.add_command(label = "中級(I)", under = 3, command = self.game_1level_set)
        self.menu_GAME.add_command(label = "上級(E)", under = 3, command = self.game_2level_set)
        self.menu_GAME.add_command(label = "エキスパート(L)", under = 7, command = self.game_3level_set)

        self.menu_MODE.add_command(label = "通常(K)", under = 3, command = self.common_mode)
        self.menu_MODE.add_command(label = "学習(J)", under = 3, command = self.learning_mode)

        self.menu_ROOT.add_command(label = "終了(X)", under = 3, command = self.game_close)
        
        ###フレームオブジェクト作成###
        self.root_frame = Frame(self.root, relief = 'groove', borderwidth = 5, bg = 'LightGray')
        self.status_frame = Frame(self.root_frame, height = 50, relief = 'sunken', borderwidth = 3, bg = 'LightGray')
        self.game_frame = Frame(self.root_frame, relief = 'sunken', borderwidth = 3, bg = 'LightGray')
        self.root_frame.pack()

        ###statusフレーム作成###
        self.status_frame.pack(pady = 5, padx = 5, fill = 'x')
        self.font_size = 16
        self.button_font_size = 13
        self.stop_timer = False
        self.timer = 0
        self.bomb_num = 50
        self.bomb_flag_num = 0
        self.clear_math_num = 0
        self.start_flag = True
        
        ###ボムカウンター###
        self.exist_bomb_count_label = Label(self.status_frame, text = '残り' + str(self.bomb_num), bg = 'LightGray', fg = 'Blue', font=('Helvetica', str(self.font_size), 'bold'))
        self.exist_bomb_count_label.place(relx=0.02, rely=0.1)

        ###リセットボタン作成###
        self.reset_button = Button(self.status_frame, text='リセット', bg = 'LightGray', fg = 'Black', font=('Helvetica', str(self.button_font_size), 'bold'), command = self.reset_button_onclick)
        self.reset_button.place(relx=0.25, rely=0.1)

        ###オートボタン作成###
        self.auto_button = Button(self.status_frame, text='オート', bg = 'LightGray', fg = 'Black', font=('Helvetica', str(self.button_font_size), 'bold'), command = self.auto_button_onclick)
        self.auto_button.place(relx=0.55, rely=0.1)

        ###タイマーラベル###
        self.timer_label = Label(self.status_frame, text = '00:00', bg = 'LightGray', fg = 'Red', font=('Helvetica', str(self.font_size), 'bold')) 
        self.timer_label.place(relx=0.83, rely=0.1)

        ###クリアラベル###
        self.clear_label = Label(self.status_frame, text = "", bg = 'LightGray', fg = 'Yellow', font=('Helvetica', str(self.font_size), 'bold'))
        self.clear_label.place(relx=0.50, rely=0.1)

        ###gameフレーム作成###
        self.game_frame.pack(pady = 5, padx = 5)

        ####マス目の作成####
        i = 0
        self.frame_list = []
        self.width = 20
        self.height = 15
        self.frame_width = 20
        self.frame_height = 20

        for x in range(self.height):
            for y in range(self.width):
                frame = Frame(self.game_frame, width = self.frame_width, height = self.frame_height, bd = 3, relief = 'raised', bg = 'LightGray')
                frame.bind("<1>", self.left_click)
                frame.bind("<3>", self.right_click)
                frame.num = i
                frame.bomb_count = 0
                frame.is_bomb = False
                self.frame_list.append(frame)
                frame.grid(row=x, column=y)
                i += 1
        self.resol = resolve.resoleve(self.game_frame, self.height, self.frame_height, self.frame_width, self.width, self.frame_list, self.bomb_num)
        
    def left_click(self,event):
        if (event.widget.cget('relief') == "ridge") :
            return
        event.widget.configure(relief = 'ridge', bd = '1')
        current_num = event.widget.num
        around_list = self.search_around(event.widget.num)

        #最初に爆弾をセット
        if self.start_flag:
            self.start_flag = False
            all_frame_num_list = [i for i in range(self.width*self.height)]
            all_frame_num_list.remove(current_num)
            for i in around_list :
                all_frame_num_list.remove(i)
            bomb_list = random.sample(all_frame_num_list, self.bomb_num)
            for bomb_idx in bomb_list :
                self.frame_list[bomb_idx].is_bomb = True
                bomb_around_list = self.search_around(bomb_idx)
                for i in bomb_around_list :
                    self.frame_list[i].bomb_count += 1
            #タイマースタート
            self.timer_start()
        #爆弾をクリック
        if  event.widget.is_bomb :
            self.timer_stop()
            #全パネルオープン
            for frame in self.frame_list:
                if frame.is_bomb:
                    frame.configure(relief = 'raised', bd = '3', bg = 'red')
                else:
                    frame.configure(relief = 'ridge', bd = '1', bg = 'LightGray')
                    if not frame.bomb_count == 0:
                        self.set_label_color(frame.num)
                frame.bind("<1>", self.stop)
                frame.bind("<3>", self.stop)
            self.clear_label.configure(text = 'GameOver!', fg = 'Red')
        else :
            self.clear_math_num += 1
            if event.widget.bomb_count == 0:
                self.auto_open(around_list)
            else:
                self.set_label_color(current_num)
            event.widget.bind("<1>", self.stop)
            event.widget.bind("<3>", self.stop)
            ###ゲームクリア判定###
            if self.is_clear():
                self.clear_label.configure(text = 'clear!', fg = 'Yellow')
                self.timer_stop()
                for frame in self.frame_list:
                    if frame.is_bomb :
                        frame.configure(bg = 'red')
                    frame.bind("<1>", self.stop)
                    frame.bind("<3>", self.stop)

    def right_click(self,event):
        if (event.widget.cget('relief')) == 'raised' :
            if self.bomb_flag_num + 1 > self.bomb_num:
                return
            event.widget.configure(relief = 'ridge', bd = '1', bg = 'yellow')
            self.bomb_flag_num += 1
        else:
            event.widget.configure(relief = 'raised',bd = '3', bg = 'LightGray')
            self.bomb_flag_num -= 1
        
        self.exist_bomb_count_label.configure(text = '残り'+ str(self.bomb_num - self.bomb_flag_num))
    
    def reset_button_onclick(self):
        self.timer_stop()
        self.timer = 0
        self.start_flag = True
        self.bomb_flag_num = 0
        self.clear_math_num = 0
        self.exist_bomb_count_label.configure(text = "残り" + str(self.bomb_num))
        self.clear_label.configure(text = '')
        i = 0
        for frame in self.frame_list :
            self.frame_list[frame.num] = frame.destroy()
        self.frame_list.clear()
        for x in range(self.height):
            for y in range(self.width):
                frame = Frame(self.game_frame, width = self.frame_width, height = self.frame_height, bd = 3, relief = 'raised', bg = 'LightGray')
                frame.bind("<1>", self.left_click)
                frame.bind("<3>", self.right_click)
                frame.num = i
                frame.bomb_count = 0
                frame.is_bomb = False
                self.frame_list.append(frame)
                frame.grid(row=x, column=y)
                i += 1
        self.timer_label.configure(text = "00:00")
        self.resol = resolve.resoleve(self.game_frame, self.height, self.frame_height, self.frame_width, self.width, self.frame_list, self.bomb_num)
    

    def auto_button_onclick(self):
        game_flag = False
        #最初に爆弾をセットしてパネルを開く
        if self.start_flag :
            self.start_flag = False
            first_open_frame_num = random.choice([i for i in range(self.width*self.height)])
            self.resol.bombSet(self.frame_list[first_open_frame_num])
            self.resol.openPanel(self.frame_list[first_open_frame_num])
            game_flag = True            
        else :
            #各マスの評価
            for frame in self.resol.frame_list :
                if frame.cget('relief') == 'ridge' :
                    (confirm_frame_list, confirm_frame_is_bomb) = self.resol.getConfirmframeList(frame)
                    #確定したマスをオープン
                    if len(confirm_frame_list) > 1 :
                        game_flag = True
                        for i in confirm_frame_list :
                            if confirm_frame_is_bomb :
                                self.resol.setBombFlag(self.resol.frame_list[i])
                            else :
                                self.resol.openPanel(self.resol.frame_list[i])
                        break
                    elif len(confirm_frame_list) == 1 :
                        game_flag = True
                        num = confirm_frame_list.pop()
                        #爆弾が確定したなら爆弾フラグをセット
                        if confirm_frame_is_bomb :
                            self.resol.setBombFlag(self.resol.frame_list[num])
                        else :
                            self.resol.openPanel(self.resol.frame_list[num])
                        break
                else :
                    continue

        ###ゲームクリア判定###
        if self.resol.is_clear():
            for frame in self.resol.frame_list:
                if frame.is_bomb :
                    frame.configure(bg = 'red', relief = 'raised', bd = '3')
            print('clear')
        else :
            if game_flag :
                self.root.after(80, self.auto_button_onclick)
            else :
                print('解けない')

    def auto_button_onclick2(self):
        observations = []
        self.learning(observations, 0)

    def learning(self, observations, episode):
        # 10000エピソードで学習する
        learning_flag = False
        #最初に爆弾をセットしてパネルを開く
        if self.start_flag :
            self.start_flag = False
            first_open_frame_num = random.choice([i for i in range(self.width*self.height)])
            self.resol.bombSet(self.frame_list[first_open_frame_num])
            self.resol.openPanel(self.frame_list[first_open_frame_num])
            learning_flag = True
            for frame in self.frame_list :
                if frame.cget('relief') == 'ridge' :
                    around_list = self.search_around(frame.num)
                    for i in around_list :
                        if  self.frame_list[i].cget('relief') == 'raised' :
                            observation = self.env.reset(self.frame_list, i)
                            observations.append(observation)
        else :
            # ε-グリーディ法で行動を選択
            action = self.env.get_action(self.env, self.q_table, observations, episode)
            #パネルが開けるか判定
            moved = False
            if self.frame_list[action].cget('relief') == "raised" :
                moved = True
            #パネルオープン
            self.resol.openPanel(self.frame_list[action])
            # 観測結果・報酬・ゲーム終了FLG・詳細情報を取得
            next_observation, reward, done, _ = self.env.step(self.frame_list, action, moved)

            # Qテーブルの更新
            self.q_table = self.env.update_q_table(self.q_table, action, observation, next_observation, reward, episode)
            print("テーブル数", len(self.q_table), "action", action, "エピソード", episode)
            print()
            observation = next_observation

            if done:
                # doneがTrueになったら１エピソード終了
                episode += 1
                self.reset_button_onclick()
                self.env.steps = 0

                if episode%500 == 0 :    
                    self.q_table.to_csv('C:\python\Minesweeper\data001.csv', header=True, index=False)

                #10000回学習したら終了
                if episode < 10000 :
                    learning_flag = True
            else :
                learning_flag = True
            
        if learning_flag :
            self.root.after(200, self.learning, observations, episode)
        else:
            print("学習終了")

    def auto_open(self,around_list):
        for i in around_list:
            if (self.frame_list[i].cget('relief')) == 'ridge' :
                continue
            self.clear_math_num += 1
            next_around_list = self.search_around(i)
            self.frame_list[i].configure(relief = 'ridge', bd = '1')
            self.frame_list[i].bind("<1>", self.stop)
            self.frame_list[i].bind("<3>", self.stop)
            if self.frame_list[i].bomb_count == 0 :
                self.auto_open(next_around_list)
            else :
                self.set_label_color(i)

    def set_label_color(self,num):
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
    
    def is_clear(self):
        return (self.height*self.width - self.clear_math_num) == self.bomb_num
    
    def search_around(self,num):
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
    
    def stop(self,event):
        pass

    def timer_count(self):
        if not self.stop_timer:
            self.timer += 1
            second = self.timer
            minute = 0
            text = ""

            while second > 59 :
                minute += 1
                second -= 60
            if minute < 10 :
                text += "0" + str(minute)
            else :
                text += str(minute)
            text += ":"
            if second < 10 :
                text += "0" + str(second)
            else :
                text += str(second)
            self.timer_label.configure(text = text)    
            self.root.after(1000,self.timer_count)   
        else:
            return 
        
    def timer_stop(self):
        self.stop_timer = True

    def timer_start(self):
        self.stop_timer = False
        self.root.after(1000, self.timer_count)
    
    def game_0level_set(self):
        self.reset_button_onclick()
        self.bomb_num = 20
        self.exist_bomb_count_label.configure(text = '残り' + str(self.bomb_num))

    def game_1level_set(self):
        self.reset_button_onclick()
        self.bomb_num = 35
        self.exist_bomb_count_label.configure(text = '残り' + str(self.bomb_num))

    def game_2level_set(self):
        self.reset_button_onclick()
        self.bomb_num = 50
        self.exist_bomb_count_label.configure(text = '残り' + str(self.bomb_num))

    def game_3level_set(self):
        self.reset_button_onclick()
        self.bomb_num = 70
        self.exist_bomb_count_label.configure(text = '残り' + str(self.bomb_num))

    def common_mode(self):
        self.auto_button.configure(command = self.auto_button_onclick)

    def learning_mode(self):
        self.auto_button.configure(text = '学習', command = self.auto_button_onclick2)

    def game_close(self):
        self.root.quit()

if __name__ == "__main__":
    main = Main()
    main.root.mainloop()

    #Mongoに保存できる形式にする
    objs = []
    for i in range(len(main.q_table)):
        _observation = str(main.q_table['observation'].values[i])
        _action = int(main.q_table['action'].values[i])
        _score = int(main.q_table['score'].values[i])
        obj = {
            'observation' : _observation,
            'action' : _action,
            'score' : _score
        }
        objs.append(obj)

    #コレクション初期化
    #co.drop()

    # なんか適当に保存
    #co.insert_many(objs)
    print("完了")


