#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import openpyxl
import time

#####################################常用方法###################################

#获取dir路径下的所有文件/文件夹路径
def get_filelist(dir):
		fullnamelist=[]
		for home, dirs, files in os.walk(dir):
				for filenamelist in files:
						fullnamelist.append(os.path.join(home, filenamelist))
		return fullnamelist

#####################################常用方法###################################

if __name__ == "__main__":
		meta_10=[]
		logpath=get_filelist(os.getcwd())
		creat_file= os.path.join(os.getcwd()+"\\output")
		print(os.path.exists(creat_file))
		if os.path.exists(creat_file) == False:	
			os.makedirs(creat_file,exist_ok=True)#当 exists_ok=False 时，若目录已存在，报 FileExistsError：当文件已存在时，无法创建该文件，exists_ok=True 时，不会报错。
		print(logpath)
		for i in range(len(logpath)):
			if ".csv" in logpath[i] and "IMEI.csv" not in logpath[i] and "result" not in logpath[i]:
				print("解析文件路径：",logpath[i])
				df1 = pd.read_csv(logpath[i],encoding='gbk')
				df2 = pd.read_csv('IMEI.csv')
				save_path=os.path.join(creat_file,"result.csv")
				print(save_path)
				distname=open(save_path,'w',newline ='') #newline 参数解决保存时中间空了一行的问题
				idx_for_df1 = df1['imei'].isin(df2['imei'])
				print(len(idx_for_df1))
				for x in range(len(idx_for_df1)):
					if idx_for_df1[x]==True:
						#print("x:" + str(x) +" "+ str(idx_for_df1[x]))
						#print(df1.iloc[x,:])
						meta_10.append(df1.iloc[x,:])#将满足条件的行加入到列表中
				pd_10=pd.DataFrame(meta_10)#将列表转换为DataFrame格式
				pd_10.to_csv(distname,index=None)

	






