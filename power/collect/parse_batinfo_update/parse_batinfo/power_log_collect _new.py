#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import re
import shutil
from glob import glob
import pickle
import zipfile
import tarfile
import rarfile
import time
import datetime
import pandas as pd
#from unrar import rarfile

#############################常用函数###################################
#去除text中包含keys的内容
def remove_char(keys, text):
#    NEW=re.split('|'.join(keys), text)  #源文件text（1.zip）
#    print(NEW)   #['1', '']
    flags = [i for i in re.split('|'.join(keys), text) if i]
    #print(flags) #['1']
    if flags:
        text = flags[0]   # .zip
    return text

# 利用os.listdir()、os.walk()获取文件夹和文件名
def GetFileName(fileDir):
    list_name = []
    for dir in os.listdir(fileDir):  # 获取当前目录下所有文件夹和文件(不带后缀)的名称
        filePath = os.path.join(fileDir, dir)  # 得到文件夹和文件的完整路径
        if os.path.isdir(filePath):
        	list_name.append(filePath)
    return list_name
           
#############################常用函数###################################


#获取log的地址
def get_log_path():
	if os.path.exists("log_address.txt"):
		all_path=os.path.join(os.getcwd(),"log_address.txt")
		address_file=open(all_path,"r",encoding='utf-8')
		log_path=address_file.read().splitlines()
		print(log_path)
		return log_path
	else:	
		log_path= os.getcwd()
		#print(log_path)    #C:\Users\Wayne\Desktop\python\power_log_collect&parse_new\extract_log
		log_path=re.split('\n',log_path) #字符串转成数组
		#print(log_path)    #['C:\\Users\\Wayne\\Desktop\\python\\power_log_collect&parse_new\\extract_log']				
		return log_path

#创建log保存路径
def extract_log_path(log_address):
	extract_path= os.path.join(log_address+"\\extract_log")
	if os.path.exists(extract_path):
		return extract_path
	else:
		os.makedirs(extract_path,exist_ok=True)#当 exists_ok=False 时，若目录已存在，报 FileExistsError：当文件已存在时，无法创建该文件，exists_ok=True 时，不会报错。
		return extract_path


#读取关键字及需提取文件 
def get_config(config_path):
		global extract_file_type
		global android_key_word
		global event_key_word
		global kernel_key_word
		config_file=open(config_path,"r",encoding='iso-8859-1')
		print(config_file)
		while True:
				line = config_file.readline()
				print(line)
				if not line: break
				line.strip()

				#提取压缩包里需要提取的文件
				if "extract_file_type" in line:
						file_type = line
						#extract_file_type=re.split('\,|\[|\]',extract_file_type)
						#file_type=re.split('\W+',file_type)
						#extract_file_type=file_type[1:-1]
						p1=re.compile(r'[\[](.*?)[\]]', re.S)  #截取[]里面的内容
						extract_file_type=re.findall(p1, file_type) #['apps,battersystats_for_bh,dumpsys_batterystats,kinfo,powermonitor_backup,log.rar']
						extract_file_type=re.split(',',extract_file_type[0]) #['apps', 'battersystats_for_bh', 'dumpsys_batterystats', 'kinfo', 'powermonitor_backup', 'log.rar']
						print("\nextract_file_type is",extract_file_type)
				elif "android_key_word" in line:
						file_type = line
						p1=re.compile(r'[\[](.*?)[\]]', re.S)  #截取[]里面的内容
						android_key_word=re.findall(p1, file_type) #['apps,battersystats_for_bh,dumpsys_batterystats,kinfo,powermonitor_backup,log.rar']
						android_key_word=re.split(',',android_key_word[0]) #['apps', 'battersystats_for_bh', 'dumpsys_batterystats', 'kinfo', 'powermonitor_backup', 'log.rar']
						print("\nandroid_key_word is",android_key_word)
				elif "event_key_word" in line:
						file_type = line
						p1=re.compile(r'[\[](.*?)[\]]', re.S)  #截取[]里面的内容
						event_key_word=re.findall(p1, file_type) #['apps,battersystats_for_bh,dumpsys_batterystats,kinfo,powermonitor_backup,log.rar']
						event_key_word=re.split(',',event_key_word[0]) #['apps', 'battersystats_for_bh', 'dumpsys_batterystats', 'kinfo', 'powermonitor_backup', 'log.rar']
						print("\nevent_key_word is",event_key_word)
				elif "kernel_key_word" in line:
						file_type = line
						p1=re.compile(r'[\[](.*?)[\]]', re.S)  #截取[]里面的内容
						kernel_key_word=re.findall(p1, file_type) #['apps,battersystats_for_bh,dumpsys_batterystats,kinfo,powermonitor_backup,log.rar']
						kernel_key_word=re.split(',',kernel_key_word[0]) #['apps', 'battersystats_for_bh', 'dumpsys_batterystats', 'kinfo', 'powermonitor_backup', 'log.rar']
						print("\nkernel_key_word is",kernel_key_word)
				elif "battery_key_word" in line:
						file_type = line
						p1=re.compile(r'[\[](.*?)[\]]', re.S)  #截取[]里面的内容
						battery_key_word=re.findall(p1, file_type) #['apps,battersystats_for_bh,dumpsys_batterystats,kinfo,powermonitor_backup,log.rar']
						battery_key_word=re.split(',',battery_key_word[0]) #['apps', 'battersystats_for_bh', 'dumpsys_batterystats', 'kinfo', 'powermonitor_backup', 'log.rar']
						print("\nbattery_key_word is",battery_key_word)				
#获取压缩包
def un_zip(filepath_arr):
		global creat_file
		#创建解压放置文件夹
		global extract_path
		global all_log_path
		all_log_path=[]#用来存放所有新建用来存放log的文件夹
		if len(filepath_arr)!=0:
			extract_path=extract_log_path(filepath_arr)
			if os.path.exists(os.path.join(extract_path+"\\extract_sucessful.txt")) == True:
				print("--->>>>>>>>>>>>>>>>>>>>>>>log have been extracted yet")
				all_log_path=GetFileName(extract_path) #获取当前路径下所有文件夹路径  ['W:\\dcs\\test\\extract_log\\A00000A3D149AD@POWER.BATTERYSTATS@', 'W:\\dcs\\test\\extract_log\\A00000A5122A98@POWER.BATTERYSTATS@']
				return all_log_path 
			list = os.listdir(filepath_arr) #列出文件夹下所有的目录与文件
			print("extract_path",extract_path)

			for i in range(len(list)):
				if '.rar' in list[i] or '.zip' in list[i] or '.tar' in list[i]:
						print("--->>>>>>>>>>>>>>>>>>>>>>>log_path is exist")
						rar_path = os.path.join(filepath_arr, list[i])
						keys=['.rar','.zip','.tar']
						new_file=remove_char(keys,list[i]) #移除.rar,.zip,.tar 后缀
						if len(new_file) > 35:             #防止路径过长报错
							new_file=new_file[0:34]
						if os.path.exists(extract_path +"\\" + new_file) == False:
							os.mkdir(extract_path +"\\" + new_file)
						log_path1 = os.path.join(extract_path+"\\"+new_file) #解压的位置
						all_log_path.append(log_path1)
						#print(all_log_path)
						creat_file = os.path.join(extract_path,"extract_sucessful.txt") 
						extract_log(rar_path,log_path1,creat_file)
						print ("--->>>>>>>>>>>>>>>>>>>>>>>un_zip log sucessful\n")
			if all_log_path=='':
				return all_log_path.append(filepath_arr)
			else:
				return all_log_path 

#解压提取的需要文件
def extract_log(filename,filepath,flag_file):
#	zip_file = zipfile.ZipFile(filename)
#	a_name=zip_file.namelist()
	global Pos_unzip
	Pos_unzip=filepath  #解压的文件位置
	zip_file = "null"
	a_name = "null"
	if (filename.find(".zip")) > -1:
		zip_file = zipfile.ZipFile(filename)
		a_name=zip_file.namelist()
		i=0
	if (filename.find(".tar")) > -1:
		zip_file = tarfile.open(filename)
		a_name=zip_file.getnames()
		i=0
	if (filename.find(".rar")) > -1:
		zip_file = rarfile.RarFile(filename)
		a_name=zip_file.namelist()
		i=0
	for names in a_name:
#		print("--->names",names)
#		print ("--->Pos_unzip",Pos_unzip)
		for l in range(len(extract_file_type)):
			#print ("wayne,---",len(extract_file_type),extract_file_type[l-1])
			if (names.find(extract_file_type[l-1]) > -1) and extract_file_type[l-1] !='':
				if (i == 0):
					f=open(flag_file,"a")
					i=i+1
				try:
					zip_file.extract(names,Pos_unzip)
					name=os.path.join(Pos_unzip+"\\"+names)
					f.write(name+"\n")
					print("--->extract sucessful")
				except:
					print("--->extract fail ")
					pass

#获取dir路径下的所有文件/文件夹路径
def get_filelist(dir):
		fullnamelist=[]
		for home, dirs, files in os.walk(dir):
				for filenamelist in files:
						fullnamelist.append(os.path.join(home, filenamelist))
		return fullnamelist


#创建保存文件
def start_parse_log(path,csv_file):
	global Imei
	global Screen_on_time
	global Screen_off_time
	global Time
	global Chargingtime
	global csvlist
	global screenon_cur_list
	global screenoff_cur_list
	global screenoff_avg_cur
	global screenon_avg_cur
	screenon_cur_list=[0]
	screenoff_cur_list=[0]
	if path == None or len(path)==0:
		print(">>>>>not exists rar/zip/tar file,we will parse current file<<<<<")
		path=log_path

	for x in range(len(path)):		
		Imei=re.findall(r'\d+',path[x])[-1] #获取imei号
		print("Imei:{0}".format(Imei))
		log_file_list=get_filelist(path[x])
		if os.path.exists(path[x]+'\\summary.txt')==True:
			print(path[x]+" "+"has been parsed yet！")
			continue
		saveout = sys.stdout
		saveerr = sys.stderr 
		outputfile=open(path[x]+'\\summary.txt',"w") #"a"可在文本末继续写入
		sys.stdout=outputfile
		sys.stderr=outputfile
		#parse_android_log(log_file_list)
		#parse_event_log(log_file_list)
		#parse_kernel_log(log_file_list)
		#parse batterystates
		parse_batterysttes(log_file_list,path[x])
		Screen_on_time=round(screen_on_total_time/3600,2)  #取两位小数
		Screen_off_time=round(screen_off_total_time/3600,2)
		screenoff_avg_cur=sum(screenoff_cur_list)/len(screenoff_cur_list)
		screenon_avg_cur=sum(screenon_cur_list)/len(screenon_cur_list)		
		csvlist=[[Imei,Time,Screen_on_time,Screen_off_time,screenon_avg_cur,screenoff_avg_cur,Chargingtime]]
		dateframe=pd.DataFrame(csvlist)
		dateframe.to_csv(csv_file,mode='a+',index = False,header=False)  # a+追加写入数据
		sys.stdout=saveout
		sys.stderr=saveerr    
		#print("parse_state:"+parse_state+"\n")
		

#############################parse_batterystates###################################
#获取batterysttes文件，并调用解析函数
def parse_batterysttes(path,savepath):
	global input_file
	file_exist=""
	#print(filelist)
	for i in range(len(path)):
		if "battersystats.txt" in path[i]:
			file_exist=True
			input_file = open(path[i], "r",encoding='iso-8859-1')
			parse_log(savepath,input_file,path[i])
		elif "batterystats_oppoCheckin.txt" in path[i]:
			file_exist=True
			input_file = open(path[i], "r",encoding='iso-8859-1')
			parse_log(savepath,input_file,path[i])
		elif "dumpsys_batterystats.txt"in path[i]:
			file_exist=True
			input_file = open(path[i], "r",encoding='iso-8859-1')
			parse_log(savepath,input_file,path[i])
		elif "batterystats.txt"in path[i]:
			file_exist=True
			input_file = open(path[i], "r",encoding='iso-8859-1')
			parse_log(savepath,input_file,path[i])
	if file_exist !=True:
		print("error! can not find batterystats file!")
		return -1

#将battersystats转换成真实时间，并重新输出到另外一个文件
def parse_log(save_path,bat_path,write_path):
  global real_time
  global timestamp
  global screen_off_time
  global screen_on_total_time
  global screen_off_total_time
  global screen_change_time
  global screenstate
  global screen_off_realtime
  global screen_on_realtime
  global Time
  global screenon_cur_list
  global screenoff_cur_list
  global charge_times
  global charge_change_time
  global screen_change_flag
  global bat_lev_time
  global charge_end_time
  global charge_start_time
  global batterylevel
  global charge_state
  global bat_lev_before
  global bat_lev
  bat_lev=0
  charge_state=""
  batterylevel=0
  charge_end_time=0
  charge_start_time=0
  bat_lev_time=0
  screen_change_flag=0
  screenon_cur_list=[0]
  screenoff_cur_list=[0]
  charge_change_time=0
  screen_off_time=0
  screen_on_time=0
  screen_on_total_time=0
  screen_off_total_time=0
  screen_change_time=0
  screenon_cur_list=[0]
  screenoff_cur_list=[0]
  bat_lev_before=0
  charge_times=0
  Time=0
  screenstate=""

  while True:
	  try:
	    line=bat_path.readline()
	  except Exception as e:
	    pass
	  if not line: break
	  line_list=re.split('\W+',line) #以非字符/数字进行分割 
	  line_list=line_list[1:-1]
	  if line.startswith("Battery History"):
	    print("Good Battery History File")
	    outputfile=open(save_path+'\\battersystats_realtime.txt',"a",encoding='utf-8')  #保存文件
	    outputfile.write("\n"+ "batterystates_log_path >>> "+ write_path +"\n"+"\n")
	  #获取起始时间及获取转换后的时间
	  (real_time,timestamp)=gettime(line,line_list)
	  getchargeinfo(line,line_list)
	  screen_summary(line,line_list)
	  bat_lev=getbatlevel(line_list)
	  print("{0}  charge_state:{1}".format(real_time,charge_state))	
	  print("{0}  screenstate:{1}".format(real_time,screenstate))
	  print("{0}  screenchange:{1}".format(real_time,screen_change_flag==screen_change_time))
	  print("{0}  chargechange:{1}".format(real_time,charge_change_time==charge_times))	  	  	  
	  print("{0}  bat_lev_before:{1}%".format(real_time,bat_lev_before))
	  print("{0}  bat_lev:{1}%".format(real_time,bat_lev))	  
	  if bat_lev!=bat_lev_before:
	  	if charge_state=="OFF" and bat_lev_before!=0:
		  	if (bat_lev_before>bat_lev)and (screen_change_flag==screen_change_time) and (charge_change_time==charge_times) and (timestamp-bat_lev_time)!=0:
		  		if screenstate=="ON":
		  			screenon_cur=(bat_lev_before-bat_lev)*4025*3600*0.01/(timestamp-bat_lev_time)
		  			screenon_cur_list.append(screenon_cur)
		  			print("screenon_cur:{0}".format(screenon_cur))
		  		elif screenstate=="OFF":
		  			screenoff_cur=(bat_lev_before-bat_lev)*4025*3600*0.01/(timestamp-bat_lev_time)
		  			screenoff_cur_list.append(screenoff_cur)
		  			print("screenoff_cur:{0}".format(screenoff_cur))
	  	bat_lev_before=bat_lev
	  	bat_lev_time=timestamp
	  	screen_change_flag=screen_change_time
	  	charge_change_time=charge_times

	  #重组写入文件
	  s = '%s %s' % (real_time,line)
	  try:
	    outputfile.write(s)
	  except Exception as e:
	    pass
	#outputfile.close()  
	  #print(s)     #2020-01-15 18:01:29                     0 (14) RESET:TIME: 2020-01-15-18-01-29


#获取每行绝对时间(timestamp)+实际时间(real_time)
def gettime(batterystats_log,line_list):
	global epoch_time
	global timestamp
	global Time
	#获取起始时间 
	if "TIME: " in batterystats_log :
		r,t,line_arr=batterystats_log.partition('TIME: ')#第一个为分隔符左边的子串，第二个为分隔符本身，第三个为分隔符右边的子串
		if bool (re.search('[a-z]',line_arr)) == False:
			line_arr=line_arr.split('-')   #去掉前后两个字符 ['2020', '01', '15', '18', '01', '29']
			epoch_time=datetime.datetime(int(line_arr[0]),int(line_arr[1]),int(line_arr[2]),int(line_arr[3]),int(line_arr[4]),int(line_arr[5]),0).timestamp()
			time=datetime.datetime.fromtimestamp(epoch_time)
			#print("batterystats 起始时间：{0}".format(time))
		if Time==0:
			Time=time

	if batterystats_log.isspace()!=True and line_list[0].find("ms")>=0: #该行非空格和且包含ms才进行时间分割
		addtime_list=re.findall(r"\d+\.?\d*",line_list[0]) #去除非数字字符
		#print(addtime_list)#['20', '55', '315']
		if len(addtime_list)==1:
			add_time=int(addtime_list[0])/1000
		elif len(addtime_list)==2:
			add_time=int(addtime_list[0])+int(addtime_list[1])/1000
		elif len(addtime_list)==3:
			add_time=int(addtime_list[0])*60+int(addtime_list[1])+int(addtime_list[2])/1000
		elif len(addtime_list)==4:
			add_time=int(addtime_list[0])*60*60+int(addtime_list[1])*60+int(addtime_list[2])+int(addtime_list[3])/1000
		elif len(addtime_list)==5:
			add_time=int(addtime_list[0])*60*60*24+int(addtime_list[1])*60*60+int(addtime_list[2])*60+int(addtime_list[3])+int(addtime_list[4])/1000
		else:
			print("格式出错")
			real_time=" "
		if ("RESET:TIME:" in batterystats_log) or ("TIME:" in batterystats_log and batterystats_log.find("TOTAL")<0):		
			timestamp=epoch_time
			real_time=datetime.datetime.fromtimestamp(epoch_time)
			epoch_time=epoch_time-add_time
		else:
			real_time=add_time+epoch_time
			timestamp=real_time
			real_time=datetime.datetime.fromtimestamp(real_time)
			#parseline_info_after['times']=add_time+epoch_time
	elif batterystats_log.isspace()!=True and batterystats_log.strip().split(' ')[0]=='0':   #开始几行时间为0的
		timestamp=epoch_time
		real_time=datetime.datetime.fromtimestamp(epoch_time) 
	else:
		real_time=" "
	#print("实际时间戳时间：{0}".format(real_time)) #实际时间戳时间：2020-04-23 16:09:30.643000
	return real_time,timestamp


#统计屏幕状态（亮灭屏次数：screen_change_time，总亮屏时长：screen_on_total_time，总熄屏时长：screen_off_total_time）
def screen_summary(batterystats_log,line_list):
	global screen_off_time
	global screen_on_time
	global screen_on_total_time
	global screen_off_total_time
	global screen_change_time
	global screenstate
	global screen_off_realtime
	global screen_on_realtime
	if "-screen " in batterystats_log or "+screen " in batterystats_log:
		if "-screen " in batterystats_log:
			(screen_off_realtime,screen_off_time)=gettime(batterystats_log,line_list)	
			#print("rela_time:{0},screen_off_time:{1}".format(real_time,screen_off_time))
			print("{0} 熄屏".format(screen_off_realtime))
			screenstate="OFF"
			screenoff_bat_lev=getbatlevel(line_list)
			screen_change_time=screen_change_time+1					
		if "+screen " in batterystats_log:
			(screen_on_realtime,screen_on_time)=gettime(batterystats_log,line_list)
			screen_change_time=screen_change_time+1
			#print("rela_time:{0},screen_on_time:{1}".format(real_time,screen_on_time))
			screenstate="ON"
			print("{0} 亮屏".format(screen_on_realtime))
		if screen_on_time!=0 and screen_off_time!=0 and (screen_on_time-screen_off_time)>0:
			screen_off_total_time=screen_off_total_time+(screen_on_time-screen_off_time)
			print("screen_off_total_time:{0}".format(screen_off_total_time))

		if screen_on_time!=0 and screen_off_time!=0 and (screen_on_time-screen_off_time)<0:
			screen_on_total_time=screen_on_total_time+(screen_off_time-screen_on_time)
			print("screen_on_total_time:{0}".format(screen_on_total_time))	

#获取电量百分比
def getbatlevel(line_list):
	global real_time
	global batterylevel
	global bat_lev
	if len(line_list)>3 and line_list[2].isdigit()==True and len(line_list[2])==3 and (0<=int(line_list[2])<=100)==True:
		if line_list[2]!=batterylevel:
			#print("{0} 电池电量：{1}%".format(real_time,line_list[2]))
			batterylevel=line_list[2]
		return int(line_list[2])
	else:
		return bat_lev

#获取充电状态
def getchargeinfo(batterystats_log,line_list):
	global charge_start_time
	global charge_end_time
	global charge_start_real_time
	global charge_end_real_time
	global charge_state
	global charge_bat_lev
	global charge_times

	if "status=" in batterystats_log:
		if "=charging" in batterystats_log:
			charge_bat_lev=getbatlevel(line_list)
			(charge_start_real_time,charge_start_time)=gettime(batterystats_log,line_list)
			charge_state="ON"
			charge_times=charge_times+1
		if "=not-charging" in batterystats_log:
			(charge_end_real_time,charge_end_time)=gettime(batterystats_log,line_list)
			charge_state="OFF"
			charge_times=charge_times+1	
			if (charge_end_time-charge_start_time)>0 and (charge_end_time!=charge_start_time!=0):
				#print("{0}到{1}处于充电阶段,共充电 {2} min".format(charge_start_real_time,charge_end_real_time,(charge_end_time-charge_start_time)/60))
				charge_start_time=0	
#############################parse_batterystates###################################


#创建csv文件
def creat_csv(path):
	column=['IMEI','起始时间','亮屏时间(h)','息屏时间(h)','亮屏平均电流','息屏平均电流','充电时间']
	csv_file = os.path.join(path,"summary.csv")
	dateframe=pd.DataFrame(columns=column)
	dateframe.to_csv(csv_file,index = False)
	return csv_file


###########################################全局变量设置####################################

#屏幕统计状态
global screen_off_time
global screen_on_time
global screen_on_total_time
global screen_off_total_time
global screen_change_time
global screenstate
screen_off_time=0
screen_on_time=0
screen_on_total_time=0
screen_off_total_time=0
screen_change_time=0
screenstate=""

#csv文件变量定义
global Imei
global Screen_on_time
global Screen_off_time
global Time
global Chargingtime
global csvlist
global timestamp
global reset_time_flag
global screenon_cur_list
global screenoff_cur_list
global screenoff_avg_cur
global screenon_avg_cur
screenon_avg_cur=0
screenoff_avg_cur=0
screenon_cur_list=[0]
screenoff_cur_list=[0]
timestamp=0
Imei=0
Screen_on_time=0
Screen_off_time=0
Time=0
Chargingtime=0
csvlist=[[Imei,Time,Screen_on_time,Screen_off_time,screenon_avg_cur,screenoff_avg_cur,Chargingtime]]


###########################################全局变量设置####################################



if __name__ == "__main__":
		config_path=os.path.join(os.getcwd(),"config")
		get_config(config_path)
		log_path = get_log_path()
		#print("log_path:{0}".format(log_path))   
		for z in range(len(log_path)):
			creat_log_path=un_zip(log_path[z])

			#创建csv文件
			csv_file=creat_csv(extract_path)
			
			#开始解析
			start_parse_log(creat_log_path,csv_file)


