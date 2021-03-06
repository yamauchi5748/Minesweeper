import sys

import gym
import gym.spaces
from tkinter import *
import numpy as np
import pandas as pd
import time
import random
import main 


class MyEnv(gym.Env):
    MAX_STEPS = 200
    TYPE = [
        0, # 0 空いていない
        1, # 1 空いている
        2, # 2 壁
    ]

    def __init__(self):
        super().__init__()
        self.width = 5
        self.height = 5

        self.action_space = gym.spaces.Discrete(self.height*self.width)
        self.observation_space = gym.spaces.Box(
            low=0,
            high=9,
            shape=np.array(range(self.height*self.width)).shape
        )

    def _reset(self, frame_list):
        # 諸々の変数を初期化する
        self.done = False
        self.steps = 0
        return self._observe(frame_list)

    def _step(self, frame_list, action, is_clear):
        # 1ステップ進める処理を記述。戻り値は observation, reward, done(ゲーム終了したか), info(追加の情報の辞書)

        self.steps += 1
        observation = self._observe(frame_list)
        reward = self._get_reward(frame_list[action], is_clear)
        self.done = self._is_done(frame_list[action], is_clear)
        return observation, reward, self.done, {}

    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    def _get_reward(self, frame, is_clear):
        # 報酬を返す。報酬の与え方が難しい
        # クリアしたら100ポイント
        # 1ステップごとに-10ポイント(できるだけ短いステップ)
        # 爆弾を開いたら-1000ポイント
        if is_clear:
            print("クリア！！")
            return 100
        elif frame.is_bomb:
            return -1000
        else:
            return 10

    def _is_pushable(self, frame_list, action):
        # パネルを開けるか
        return (
            0 <= action < len(frame_list)
            and frame_list[action].cget('relief') == 'raised'
        )

    def _is_done(self, frame, is_clear):
        # 爆弾パネルを開く　もしくは　クリア
        if frame.is_bomb or is_clear :
            return True
        else:
            return False

    def _observe(self, frame_list):
        observation = ""
        for frame in frame_list:
            if frame.cget('relief') == "ridge":
                if frame.cget('bg') == "yellow":
                    observation += ",9"
                else :
                    if frame.bomb_count == 0 :
                        observation += ",0"
                    elif frame.bomb_count == 1 :
                        observation += ",1"
                    elif frame.bomb_count == 2 :
                        observation += ",2"
                    elif frame.bomb_count == 3 :
                        observation += ",3"
                    elif frame.bomb_count == 4 :
                        observation += ",4"
                    elif frame.bomb_count == 5 :
                        observation += ",5"
                    elif frame.bomb_count == 6 :
                        observation += ",6"
                    elif frame.bomb_count == 7 :
                        observation += ",7"
                    elif frame.bomb_count == 8 :
                        observation += ",8"
            else :
                observation += ",10"
        return observation.lstrip(",")

    #行動価値関数
    def update_q_table(self, _q_table, _action,  _observation, _next_observation, _reward, _episode):
    
        alpha = 0.2 # 学習率
        gamma = 0.99 # 時間割引き率

        #_q_tableにデータが存在するか
        if len(_q_table[_q_table['observation'] == _observation][_q_table['action'] == _action]) > 0 :
            # 行動後の状態で得られる最大行動価値 Q(s',a')
            next_max_q_value = 0
            if len(_q_table[_q_table['observation'] == _next_observation]) > 0 :
                next_max_q_value = max(_q_table[_q_table['observation'] == _next_observation]['score'].values)
                next_max_q_action = _q_table[(_q_table['observation'] == _next_observation) & (_q_table['score'] == next_max_q_value)]['action']

            # 行動前の状態の行動価値 Q(s,a)
            q_value = _q_table[(_q_table['observation'] == _observation) & (_q_table['action'] == _action)]['score']

            # 行動価値関数の更新
            _q_table.loc[(_q_table['observation'] == _observation) & (_q_table['action'] == _action), 'score'] = q_value + alpha * (_reward + gamma * next_max_q_value - q_value)
        else :
            #　行動価値関数に新しいデータをセット
            new_data = pd.Series([_observation, _action, alpha*_reward], index=_q_table.columns, name=len(_q_table))
            _q_table = _q_table.append(new_data)
        return _q_table

    #グリーディ法
    def get_action(self, _env, _q_table, _observation, _episode, _frame_list):
        epsilon = 0.002
        _action = -1

        # 行動可能箇所を算出
        action_list = []
        for i in range(self.width*self.height) :
            if _frame_list[i].cget('relief') == "raised" :
                action_list.append(i)

        # ランダムでないかつ、盤面が既出の場合
        if np.random.uniform(0, 1) > epsilon and len(_q_table[_q_table['observation'] == _observation]) > 0:

            # 既出の盤面に対して行動可能な全行動をためしていないか
            if len(_q_table[_q_table['observation'] == _observation]) < len(action_list) :
                remove_list = _q_table[_q_table['observation'] == _observation]['action'].values
                for i in remove_list:
                    action_list.remove(i)
                _action = np.random.choice(action_list)
            else :
                _max_score = max(_q_table[_q_table['observation'] == _observation]['score'].values)
                _action = max(_q_table[(_q_table['observation'] == _observation) & (_q_table['score'] == _max_score)]['action'].values)
        else:
            _action = np.random.choice(action_list)
        return int(_action)
            