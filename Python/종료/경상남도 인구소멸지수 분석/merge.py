'''
    @Filename | merge.py
    @Author   | SoongFish
    @Date     | 2020.10.19. ~ 2020.10.30.
    @Desc     | Merge and restructure population data for use Microstrategy
'''

__TMONTH__ = 123 # toal month (2010.07. ~ 2020.09.)
__TEMD__ = 310 # total EMD
__COLINDEXMALE__ = range(8, 70, 3)
__COLINDEXFEMALE__ = range(9, 70, 3)
__AGE__ = ['A. 0~4세', 'B. 5~9세', 'C. 10~14세', 'D. 15~19세', 'E. 20~24세', 'F. 25~29세', 'G. 30~34세', 'H. 35~39세', 'I.40~44세', 'J. 45~49세', 'K. 50~54세', 'L. 55~59세', 'M. 60~64세', 'N. 65~69세', 'O. 70~74세', 'P. 75~79세', 'Q. 80~84세', 'R. 85~89세', 'S. 90~94세', 'T. 95~99세', 'U. 100세이상']
#__AGE__ = ['0~4세', '5~9세', '10~14세', '15~19세', '20~24세', '25~29세', '30~34세', '35~39세', '40~44세', '45~49세', '50~54세', '55~59세', '60~64세', '65~69세', '70~74세', '75~79세', '80~84세', '85~89세', '90~94세', '95~99세', '100세이상']

import pandas as pd
import numpy as np

data_origin = pd.read_csv('merge.csv', encoding = 'cp949')
''' df
년도, 월, 읍면동별, 코드, 계, 남, 여, 0~4세계, 0~4세남, 0~4세여, 5~9세계, 5~9세남, 5~9세여, ..., 95~99세여, 100세이상계, 100세이상남, 100세이상여, 소멸지수
df '''

''' sample 
년도, 월, 읍면동별, 코드, 성별(남), 0~4세남
년도, 월, 읍면동별, 코드, 성별(남), 5~9세남
...
년도, 월, 읍면동별, 코드, 성별(남), 100세이상남
년도, 월, 읍면동별, 코드, 성별(남), 계
년도, 월, 읍면동별, 코드, 성별(여), 0~4세여 
년도, 월, 읍면동별, 코드, 성별(여), 5~9세여
...
년도, 월, 읍면동별, 코드, 성별(여), 100세이상여
년도, 월, 읍면동별, 코드, 성별(여), 계
년도, 월, 읍면동별+1, 코드+1, 성별(남), 0~4세남
년도, 월, 읍면동별+1, 코드+1, 성별(남), 5~9세남
...
sample '''

list_result = list()
list_smgs = list()
flag_gender = 1 # 1 : M / 2 : F

for i in range(len(data_origin)): # 효율 개선하기
#for i in range(383): # test용
    for gender in range(2):
        for j in range(len(__AGE__)):
            list_result.append([data_origin.loc[i][0], data_origin.loc[i][1], data_origin.loc[i][2][5:], data_origin.loc[i][3], __AGE__[j],
            (lambda x: '남' if x == 1 else '여')(flag_gender), (lambda x: data_origin.loc[i][__COLINDEXMALE__[j]] if x == 1 else data_origin.loc[i][__COLINDEXFEMALE__[j]])(flag_gender)])
        if flag_gender == 1:
            flag_gender = 2
        else:
            flag_gender = 1
    list_smgs.append([data_origin.loc[i][0], data_origin.loc[i][1], data_origin.loc[i][2], data_origin.loc[i][3], data_origin.loc[i][-1]])

df_result = pd.DataFrame.from_records(list_result, columns = ['년도', '월', '읍면동별', '코드', '나이', '성별', '인구'])
df_smgs = pd.DataFrame.from_records(list_smgs, columns = ['년도', '월', '읍면동별', '코드', '소멸지수'])

df_result.to_csv('GSND_10years_Population.csv', encoding = 'cp949', index = False)
df_smgs.to_csv('GSND_10years_SMGS.csv', encoding = 'cp949', index = False)

#for i in range(__TMONTH__):
#    for j in range(__TEMD__):
#        # 전체순회 : __TMONTH__ * 310 + __TEMD__
#        # if i == 0: df1 = data
#        if i == 0:
#            
#        # else: df2 = data
#    # if i != 0: df1 = df1.append(df2)