'''
    @Filename | ARL.py
    @Author   | SoongFish
    @Date     | 2020.10.12. ~ 2020.10.16
    @Desc     | GUIfy on Civil Complaint Analysis System for co-worker's accessibility
'''

#!/usr/bin/env python
# coding: utf-8

# todo
# 1. analysis frame 디자인
# 97. object.place 정리 (pack, grid로, https://blog.naver.com/sisosw/221412034474)
# 98. Processbar 작성
# 99. '내용'.len < 15 처리 (Prepro)

# Errorlog
# 1. 전처리 후 EDA 내 버튼 클릭시 화면 작아짐

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import sys
import os
import re
#pip install soynlp
from soynlp.word import WordExtractor
from soynlp.tokenizer import LTokenizer
from soynlp.utils import DoublespaceLineCorpus
from collections import Counter
#pip install wordcloud
from wordcloud import WordCloud
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter.filedialog import askopenfilenames
import tkinter.ttk as ttk


 # 환경 설정
plt.rc('font', family='Malgun Gothic') # matplotlib 한글 처리

title = '경상남도 민원분석 시스템'
flag_login = 0
username = ''
workdir = ''
resultdir = ''
filename = ''
filename_dateflag = ''
data_origin = pd.DataFrame()
rbt_value = 0

flag_prepro = 0

mainwindow = tk.Tk()
mainwindow.title(title)
mainwindow.geometry('800x600')
mainwindow.resizable(False, False)


 # 민원파일 로드 + 경로 설정
def Load_File():
    if flag_login == 0 or flag_login == None or flag_login == '':
        Login()
    else:
        global filename, workdir, resultdir, filename_dateflag
        file = askopenfilenames(initialdir = 'c:/', filetypes = (('csv File', '*.csv'), ('All Files', '*.*')), title = '민원파일 선택')
        filename = file[0].split('/')[-1]
        workdir = file[0].split('/')[:-1] # 작업경로(민원파일 경로) 설정
        workdir = '/'.join(workdir) + '/'
        os.chdir(workdir)
        os.makedirs('result', exist_ok = True)
        resultdir = os.getcwd() + '/result/'
        now = datetime.datetime.now()
        filename_dateflag = '[' + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + '] '
        
        mainwindow.title(title + '(' + username + ') ' + '- 작업중 (' + filename + ')')
        
        Load_Pandas()
        
        # preview (https://youtu.be/PgLjwl6Br0k)
        data_preview_frame = tk.LabelFrame(mainwindow, text = '데이터 미리보기 ({}행, {}열)'.format(data_origin.shape[0], data_origin.shape[1]))
        data_preview_frame.place(height = 300, width = 800, y = 5)
        
        data_preview = ttk.Treeview(data_preview_frame)
        data_preview.place(relheight = 1, relwidth = 1)
        
        scrolly = tk.Scrollbar(data_preview_frame, orient = 'vertical', command = data_preview.yview)
        scrollx = tk.Scrollbar(data_preview_frame, orient = 'horizontal', command = data_preview.xview)
        data_preview.configure(xscrollcommand = scrollx.set, yscrollcommand = scrolly.set)
        scrollx.pack(side = 'bottom', fill = 'x')
        scrolly.pack(side = 'right', fill = 'y')
        
        data_preview['column'] = list(data_origin.columns)
        data_preview['show'] = 'headings'
        for column in data_preview['columns']:
            data_preview.heading(column, text = column)
            
        data_origin['rows'] = data_origin.to_numpy().tolist()
        for row in data_origin['rows']:
            data_preview.insert('', 'end', values = row)        
        
        # analysis frame
        frame_analysis = ttk.Notebook(mainwindow, width = 787, height = 230)
        frame_analysis.place(x = 5, y = 320)
       
       
        frame_prepro = tk.Frame(mainwindow)
        frame_EDA = tk.Frame(mainwindow)
        frame_word = tk.Frame(mainwindow)
        
        
        frame_analysis.add(frame_prepro, text = '데이터 전처리')
        frame_analysis.add(frame_EDA, text = 'EDA')
        frame_analysis.add(frame_word, text = '워드클라우드')
        #prepro#
        bt_test_prepro = tk.Button(frame_prepro, text = '데이터 전처리', overrelief = 'solid', command = lambda:Prepro())
        bt_test_prepro.place(x = 10, y = 10)
        #EDA#
        bt_yearly = tk.Button(frame_EDA, text = '연간 민원건수 분석', overrelief = 'solid', command = lambda:Makegraph_Yearly(rbt_value))
        bt_yearly.place(x = 10, y = 10)
        bt_monthly = tk.Button(frame_EDA, text = '월간 민원건수 분석', overrelief = 'solid', command = lambda:Makegraph_Monthly(rbt_value))
        bt_monthly.place(x = 10, y = 40)
        bt_yearmonth = tk.Button(frame_EDA, text = '연간+월간 민원건수 분석', overrelief = 'solid', command = lambda:Makegraph_Yearmonth(rbt_value))
        bt_yearmonth.place(x = 10, y = 70)
        bt_daily = tk.Button(frame_EDA, text = '요일별 민원건수 분석', overrelief = 'solid', command = lambda:Makegraph_Daily(rbt_value))
        bt_daily.place(x = 10, y = 100)
        
        rbt_var = tk.IntVar()
        rbt_graphtype_0 = tk.Radiobutton(frame_EDA, text = '막대그래프', variable = rbt_var, value = 0, command = lambda:(Rbt_Check(rbt_var.get())))
        rbt_graphtype_0.select()
        rbt_graphtype_0.place(x = 200, y = 10)
        rbt_graphtype_1 = tk.Radiobutton(frame_EDA, text = '꺾은선그래프', variable = rbt_var, value = 1, command = lambda:(Rbt_Check(rbt_var.get())))
        rbt_graphtype_1.deselect()
        rbt_graphtype_1.place(x = 200, y = 30)
        #word#
        bt_test_yearly = tk.Button(frame_word, text = '워드클라우드', overrelief = 'solid', command = lambda:Makegraph_Wordcloud())
        bt_test_yearly.place(x = 10, y = 10)
    

def Login(pleasebequiet = 1):
    global flag_login, username
    if flag_login == 0 or flag_login == None or flag_login == '':
        flag_login = simpledialog.askstring("인증", "사용자 코드를 입력하세요.", parent = mainwindow)
        # todo
        # sha256 후 서버연동 + dialog 아이콘 변경 + 디자인
        if flag_login == 0 or flag_login == None or flag_login == '' or len(flag_login) > 20:
            flag_login = 0
            return
        else:
            username = flag_login
            mainwindow.title(title + '(' + username + ') ')
    else:
        if pleasebequiet != 1:
            messagebox.showwarning("계정", "이미 로그인 되어있습니다!") 
            return
    
def Logout():
    global flag_login, flag_prepro, username, rbt_value
    if flag_login == 0 or flag_login == None or flag_login == '':
        messagebox.showwarning("계정", "먼저 로그인하세요!")
    else:
        messagebox.showinfo("계정", "로그아웃이 완료되었습니다.")
        for widget in mainwindow.winfo_children(): # 화면 클리어
            widget.destroy()
        Make_Menu()
        flag_login, flag_prepro, rbt_value = 0
        username = ''
        mainwindow.title(title)

def Quit():
	mainwindow.quit()
    
def Rbt_Check(rbt_val):
    global rbt_value
    rbt_value = rbt_val
    
 # 작업 데이터 로드
def Load_Pandas():
    global data_origin
    data_origin = pd.read_csv(workdir + filename, encoding = 'cp949') # 도지사에게바란다
    #data_origin = pd.read_csv(workdir + filename, encoding = 'utf-8') # 국민신문고

 # 데이터 전처리
def Prepro():
    global data_origin, flag_prepro
    
    #data_origin = data_origin[data_origin['내용'].str.len() > 15] # '내용' 15글자 이상만 추출 (왜안되지?)
    #data_origin = data_origin.drop([data_origin['내용'].str.len() > 15], axis = 0) # '내용' 15글자 이상만 추출 (왜안되지??)
    
    data_origin['작성일시'] = pd.to_datetime(data_origin['작성일시']) # 작성일시 날짜화
    data_origin = data_origin.sort_values(by = ["작성일시"], ascending = True) # 작성일시 기준으로 정렬
    
    flag_prepro = 1
    
    messagebox.showinfo("작업", "데이터 전처리가 완료되었습니다.")
    
 # 연도별 민원 빈도 그래프 작성 (코드 개선필요)
def Makegraph_Yearly(graphtype): #graphtype - 0:bar / 1:plot
    #print(graphtype)
    if flag_login == 0 or flag_login == None or flag_login == '':
        Login()
    elif flag_prepro == 0:
        messagebox.showwarning("주의", "데이터 전처리 후 실행해주세요.")
        return
    else:
        (cnt2018, cnt2019, cnt2020) = (0, 0, 0)
        for i in range(len(data_origin['작성일시'])):
           if data_origin.loc[i, '작성일시'].year == 2018: cnt2018 += 1
           elif data_origin.loc[i, '작성일시'].year == 2019: cnt2019 += 1
           else: cnt2020 += 1
                   
        plt.clf() # plt figure 초기화
        plt.style.use('ggplot')
        plt.title("연도별 민원 빈도")
        if graphtype:   plt.plot(["2018", "2019", "2020"], [cnt2018, cnt2019, cnt2020])
        else:   plt.bar(["2018", "2019", "2020"], [cnt2018, cnt2019, cnt2020])
        #plt.show()
        plt.savefig(resultdir + filename_dateflag + '연도별 민원 빈도.png', dpi = 200)
        
    messagebox.showinfo("작업", "연간 민원건수 분석이 완료되었습니다.\n\nresult폴더에 결과물이 저장되었습니다.")

 # 월별 민원 빈도 그래프 작성 (코드 개선필요)
def Makegraph_Monthly(graphtype): #graphtype - 0:bar / 1:plot
    if flag_login == 0 or flag_login == None or flag_login == '':
        Login()
    elif flag_prepro == 0:
        messagebox.showwarning("주의", "데이터 전처리 후 실행해주세요.")
        return
    else:
       (cnt1, cnt2, cnt3, cnt4, cnt5, cnt6, cnt7, cnt8, cnt9, cnt10, cnt11, cnt12) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
       for i in range(len(data_origin['작성일시'])):
           if data_origin.loc[i, '작성일시'].month == 1: cnt1 += 1
           elif data_origin.loc[i, '작성일시'].month == 2: cnt2 += 1
           elif data_origin.loc[i, '작성일시'].month == 3: cnt3 += 1
           elif data_origin.loc[i, '작성일시'].month == 4: cnt4 += 1
           elif data_origin.loc[i, '작성일시'].month == 5: cnt5 += 1
           elif data_origin.loc[i, '작성일시'].month == 6: cnt6 += 1
           elif data_origin.loc[i, '작성일시'].month == 7: cnt7 += 1
           elif data_origin.loc[i, '작성일시'].month == 8: cnt8 += 1
           elif data_origin.loc[i, '작성일시'].month == 9: cnt9 += 1
           elif data_origin.loc[i, '작성일시'].month == 10: cnt10 += 1
           elif data_origin.loc[i, '작성일시'].month == 11: cnt11 += 1
           else: cnt12 += 1
                   
       plt.clf()
       plt.style.use('ggplot')
       plt.title('월별 민원 빈도')
       if graphtype:    plt.plot(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'], [cnt1, cnt2, cnt3, cnt4, cnt5, cnt6, cnt7, cnt8, cnt9, cnt10, cnt11, cnt12])
       else:    plt.bar(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'], [cnt1, cnt2, cnt3, cnt4, cnt5, cnt6, cnt7, cnt8, cnt9, cnt10, cnt11, cnt12])
       #plt.show()
       plt.savefig(resultdir + filename_dateflag + '월별 민원 빈도.png', dpi = 200)
       
    messagebox.showinfo("작업", "월간 민원건수 분석이 완료되었습니다.\n\nresult폴더에 결과물이 저장되었습니다.")


 # 요일별 민원 빈도 그래프 작성 (코드 개선필요)
def Makegraph_Daily(graphtype): #graphtype - 0:bar / 1:plot
    if flag_login == 0 or flag_login == None or flag_login == '':
        Login()
    elif flag_prepro == 0:
        messagebox.showwarning("주의", "데이터 전처리 후 실행해주세요.")
        return
    else:
       (cntd1, cntd2, cntd3, cntd4, cntd5, cntd6, cntd7) = (0, 0, 0, 0, 0, 0, 0)
       for i in range(len(data_origin['작성일시'])):
           if data_origin.loc[i, '작성일시'].weekday() == 0: cntd1 += 1
           elif data_origin.loc[i, '작성일시'].weekday() == 1: cntd2 += 1
           elif data_origin.loc[i, '작성일시'].weekday() == 2: cntd3 += 1
           elif data_origin.loc[i, '작성일시'].weekday() == 3: cntd4 += 1
           elif data_origin.loc[i, '작성일시'].weekday() == 4: cntd5 += 1
           elif data_origin.loc[i, '작성일시'].weekday() == 5: cntd6 += 1
           else: cntd7 += 1
           
       plt.clf()
       plt.style.use('ggplot')
       plt.title("요일별 민원 빈도")
       if graphtype:    plt.plot(["월", "화", "수", "목", "금", "토", "일"], [cntd1, cntd2, cntd3, cntd4, cntd5, cntd6, cntd7])
       else:    plt.bar(["월", "화", "수", "목", "금", "토", "일"], [cntd1, cntd2, cntd3, cntd4, cntd5, cntd6, cntd7])
       #plt.show()
       plt.savefig(resultdir + filename_dateflag + '요일별 민원 빈도.png', dpi = 200)
       
    messagebox.showinfo("작업", "요일별 민원건수 분석이 완료되었습니다.\n\nresult폴더에 결과물이 저장되었습니다.")


 # 연도+월별 민원 빈도 그래프 작성 (코드 개선필요)
def Makegraph_Yearmonth(graphtype): #graphtype - 0:bar / 1:plot
    if flag_login == 0 or flag_login == None or flag_login == '':
        Login()
    elif flag_prepro == 0:
        messagebox.showwarning("주의", "데이터 전처리 후 실행해주세요.")
        return
    else:
        cnt = 0
        tmp_yymm = ''
        list_yymm = list()
        list_yymm_cnt = list()

        for i in data_origin['작성일시']:
           if tmp_yymm != str(i.year) + '-' + str(i.month): 
               if cnt > 1: list_yymm_cnt.append(cnt)
               cnt = 1
               tmp_yymm = str(i.year) + '-' + str(i.month)
               list_yymm.append(tmp_yymm)
           else:
               cnt += 1
        list_yymm_cnt.append(cnt)

        plt.clf()
        plt.style.use('ggplot')
        plt.figure(figsize = (len(list_yymm)*0.6, 10)) # grid size 가변화
        plt.title("연도+월별 민원 빈도")
        if graphtype:   plt.plot(list_yymm, list_yymm_cnt)
        else:   plt.bar(list_yymm, list_yymm_cnt)
        plt.xticks(rotation = 45, ha = "right") # x축 라벨 회전
        #plt.show()
        plt.savefig(resultdir + filename_dateflag + '연도+월별 민원 빈도.png', dpi = 200)
        
    messagebox.showinfo("작업", "연간+월간 민원건수 분석이 완료되었습니다.\n\nresult폴더에 결과물이 저장되었습니다.")


 # 처리상황 파이차트


 # 답변소요기간 계산
# todo
# 기준을 작성일시로 할지 수정일시로 할지?
# 답변소요기간 표시형식 바꾸기
# NaT 처리
def reply():
    data_origin['답변일자'] = pd.to_datetime(data_origin['답변일자']) # 답변일자 날짜화

for i in range(len(data_origin)):
   data_origin.loc[i, '답변소요기간'] = data_origin.loc[i, '답변일자'] - data_origin.loc[i, '작성일시']


 # 처리부서별 최소, 최대, 평균 답변소요기간 (어렵네)
#data_origin.groupby('담당부서').apply(lambda x : data_origin['답변소요기간'])


 # 워드클라우드 (https://blog.naver.com/jjuna91/222108733922)
 # todo
 # stopwords 목록 추가(공무원, 행정, 민원 ...) / 삭제(경남, 김해 ...) 
 # 워드클라우드 모양 https://blog.naver.com/nilsine11202/221834254905
def Makegraph_Wordcloud():
    if flag_login == 0 or flag_login == None or flag_login == '':
        Login()
    elif flag_prepro == 0:
        messagebox.showwarning("주의", "데이터 전처리 후 실행해주세요.")
        return
    else:
        data_wordcloud = pd.DataFrame(data_origin['내용'], columns = ['contents'])
        data_wordcloud['contents'] = data_origin['내용'].apply(lambda x: re.sub('[^가-힣]',' ', x))

        word_extractor = WordExtractor(min_frequency = 100, # 가변화하기 (ex. data_origin.len() 비례)
                         min_cohesion_forward = 0.05,
                         min_right_branching_entropy = 0.0)
        word_extractor.train(data_wordcloud['contents'].values)
        words = word_extractor.extract()

        cohesion_score = {word:score.cohesion_forward for word, score in words.items()}
        tokenizer = LTokenizer(scores = cohesion_score)
        data_wordcloud['tokenizer'] = data_wordcloud['contents'].apply(lambda x: tokenizer.tokenize(x, remove_r = True))

        words = list()
        for i in data_wordcloud['tokenizer'].values:
            for j in i:
                words.append(j)

        count = Counter(words)
        words_dict = dict(count)

        csv_stopwords = pd.read_csv(workdir + 'stopwords.csv', encoding = 'cp949', skiprows = 0)
        stopwords = list()
        for i in csv_stopwords.values:
            for j in i:
                stopwords.append(j)

        for word in stopwords:
            words_dict.pop(word, None)

        wordcloud = WordCloud(font_path = workdir + 'NanumGothic.ttf', width = 500, height = 500, background_color = 'white').generate_from_frequencies(words_dict)

        plt.clf()
        plt.figure(figsize = (20, 20))
        plt.imshow(wordcloud)
        plt.axis('off')
        #plt.show()
        plt.savefig(resultdir + filename_dateflag + '워드클라우드.png', dpi = 100)
        
    messagebox.showinfo("작업", "워드클라우드 생성이 완료되었습니다.\n\nresult폴더에 결과물이 저장되었습니다.")

 # Menubar
def Make_Menu():
    menubar = tk.Menu(mainwindow)

    menu_1 = tk.Menu(menubar, tearoff = 0)
    menu_1.add_command(label = "민원파일 열기", command = Load_File)
    menu_1.add_separator()
    menu_1.add_command(label = "종료", command = Quit)
    menubar.add_cascade(label = "파일", menu = menu_1)

    menu_2 = tk.Menu(menubar, tearoff = 0)
    menu_2.add_command(label = "로그인", command = lambda:Login(pleasebequiet = 0))
    menu_2.add_separator()
    menu_2.add_command(label = "로그아웃", command = Logout)
    menubar.add_cascade(label = "계정", menu = menu_2)

    menu_3 = tk.Menu(menubar, tearoff = 0)
    menu_3.add_command(label = "About")
    menu_3.add_command(label = "버전 정보")
    menubar.add_cascade(label = "정보", menu = menu_3)

    mainwindow.config(menu = menubar)
    
def log():
    with open(workdir + 'log.log', 'a') as logdata:
        logfuncname = sys._getframe().f_back.f_code.co_name
        logtime = time.strftime('%c', time.localtime(time.time()))
        logdata.write('[{}] {} ##funcname: {} ##workdir: {} ##filename: {}\n'.format(username, logtime, logfuncname, workdir, filename))

 # main
mainwindow.tk.call('wm', 'iconphoto', mainwindow._w, tk.PhotoImage(file = 'icon.png'))
Make_Menu()
mainwindow.mainloop()
#Makegraph_Yearly()
#Makegraph_Monthly()
#Makegraph_Daily()
#Makegraph_Yearmonth()
#Makegraph_Wordcloud()