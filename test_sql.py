import pandas as pd
import json
import os
from datetime import datetime, timedelta
import mysql.connector

# 資料庫連接
def connect_to_db():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='memproject_manager',
        password='mempassword',
        database='memproject'
    )
# 設定初始預設值
DEFAULT_EF = 2.5
DEFAULT_N = 1
DEFAULT_I = 1

# 更新 EF 的函數
def update_ef(EF, q):
    EF = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    return max(EF, 1.3)

# SM2 演算法
def sm2(EF, n, I, q):
    if q >= 3:
        if n == 1:
            I = 1
        elif n == 2:
            I = 6
        else:
            I = I * EF
        EF = update_ef(EF, q)
        n += 1
    else:
        n = 1
        I = 1

    return EF, n, I

connect_to_db()

print("歡迎使用單字複習系統\n")
while True:
    option = input("請選擇功能 (1: 新增單字, 2: 開始複習): ")
    if option == '1':
        group_option = input("1:新增資料集,2:新增單字到現有資料集") 
        if group_option == '1':
            # 讀取 Excel 檔案
            file_path = 'words.xlsx'
            df = pd.read_excel(file_path)
            # 連線資料庫
            connection = connect_to_db()
            cursor = connection.cursor()
            # 新增資料集
            group = input("請輸入資料集名稱: ")
            #確認資料集名稱是否重複
            sql = "SELECT name FROM vocabulary_group"
            cursor.execute(sql)
            group_data = cursor.fetchall()
            group_list = [item[0] for item in group_data]
            if group in group_list:
                print("資料集名稱重複")
                continue
            sql = "INSERT INTO vocabulary_group (name) VALUES (%s)"
            val = (group,)
            cursor.execute(sql, val)
            connection.commit()
            #無用
            results = cursor.fetchall() 

            # 取得資料集編號
            group_id = cursor.lastrowid  # 使用 lastrowid 取得最新插入的資料集 ID

            sql = "insert into vocabulary (vocabulary_group_id, name, meaning ) values (%s, %s, %s)"
            for index, row in df.iterrows():
                word = row['單字']
                meaning = row['含意']
                val = (group_id, word, meaning,)
                cursor.execute(sql, val)
                connection.commit()

            cursor.close()

        if group_option == '2':
            # 讀取 Excel 檔案
            file_path = 'words.xlsx'
            df = pd.read_excel(file_path)

           
            #讀取資料集選項
            connection = connect_to_db()
            cursor = connection.cursor()
            sql = "SELECT id FROM vocabulary_group"
            cursor.execute(sql)
            group_data = cursor.fetchall()
            #選擇資料集
            print("資料集列表:")
            for item in group_data:
                print(item[0])
            group_id= int(input("請輸入資料集編號: "))
            sql = "SELECT name FROM vocabulary WHERE vocabulary_group_id = %s"
            val = (group_id,)
            cursor.execute(sql, val)
            data = cursor.fetchall()

            # 檢查單字是否已經存在於該資料集中
            existing_words = {item[0] for item in data}
            # 新單字資料
            for index, row in df.iterrows():
                word = row['單字']
                if word not in existing_words:
                    sql = "insert into vocabulary (vocabulary_group_id, name, meaning ) values (%s, %s, %s)"
                    val = (group_id, word, row['含意'])
                    cursor.execute(sql, val)
                    connection.commit()


            cursor.close()
    elif option == '2':
        #讀取 SQL 資料
        connection = connect_to_db()
        cursor = connection.cursor()
        sql = "SELECT * FROM vocabulary"
        cursor.execute(sql)
        data = cursor.fetchall()
        #data格式 [(1, 1, 'good', '好', 1.0, 1.0, 2.5, datetime.date(2024, 9, 10), 0)]
        #格式(編號, 資料集編號, 要背的, 含意, 複習次數=n, 下次複習間隔天數=I, 難度參數=EF, 下次複習日期, 上次複習難度)
        # 進行複習模擬
        #抓取資料集名稱
        sql = "SELECT name FROM vocabulary_group"
        cursor.execute(sql)
        group_data = cursor.fetchall()
        group_list = []
        for item in group_data:
            group_list.append(item[0])
        group_select = input(f"請選擇要複習的資料集: {group_list} ")
        
        #抓取資料集內容
        sql = """
            SELECT *
            FROM vocabulary v
            JOIN vocabulary_group vg ON v.vocabulary_group_id = vg.id
            WHERE vg.name = %s
        """
        val = (group_select,)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        today = datetime.now().strftime('%Y-%m-%d')
        

        # 取得今天需要複習的單字 因為方便測試所以設定為今天之後的單字 
        #到時候要改成今天前的單字
        due_words = [item for item in result if item[7].strftime('%Y-%m-%d') >= today]

        for item in due_words:
            word = item[2]
            EF = item[6]
            n = item[4]
            I = item[5]
            id = item[0]
            print(f"單字: {word},id: {id}")
            # 模擬用戶對這個單字的記憶評分
            q = int(input("請評分 (0-5): ")) 
            
            # 使用 SM2 演算法更新資料
            EF, n, I = sm2(EF, n, I, q)

            # 計算下次複習日期
            next_review_date = ( datetime.now() + timedelta(days=I)).strftime('%Y-%m-%d')
                
            # 更新資料
            cursor = connection.cursor()
            sql = "UPDATE vocabulary SET difficult = %s, days_reviewed = %s, next_review_days = %s, next_review_dates = %s WHERE id = %s"
            val = (EF, n, I, next_review_date, id)
            cursor.execute(sql, val)
            connection.commit()
            cursor.close()

            
                      
        print(f"更新後的資料已儲存")
