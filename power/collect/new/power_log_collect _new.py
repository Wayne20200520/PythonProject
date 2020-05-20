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
#from unrar import rarfile

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
#	f.close()

#获取dir路径下的所有文件/文件夹路径
def get_filelist(dir):
		fullnamelist=[]
		for home, dirs, files in os.walk(dir):
				for filenamelist in files:
						fullnamelist.append(os.path.join(home, filenamelist))
		return fullnamelist

#创建保存文件
def start_parse_log(path):
	if path == None or len(path)==0:
		print(">>>>>not exists rar/zip/tar file,we will parse current file<<<<<")
		path=log_path

	for x in range(len(path)):		
		#输出log到文件
		print(path[x])
		log_file_list=get_filelist(path[x])
		if os.path.exists(path[x]+'\\summary.txt')==True:
			print(path[x]+" "+"has been parsed yet！")
			continue
		saveout = sys.stdout
		saveerr = sys.stderr 
		outputfile=open(path[x]+'\\summary.txt',"w") #"a"可在文本末继续写入
		sys.stdout=outputfile
		sys.stderr=outputfile
		parse_android_log(log_file_list)
		parse_event_log(log_file_list)
		parse_kernel_log(log_file_list)
		#parse batterystates
		parse_batterysttes(log_file_list,path[x])
		sys.stdout=saveout
		sys.stderr=saveerr    
		print("parse_state:"+parse_state+"\n")

#解析android log
def parse_android_log(path):
	global key_log_buff
	global parse_state
	exsit_flag=False
	key_log_buff = ''
	#print("文件数量：",len(log_file_list))
	for i in range(len(path)):
		if "logcat" in path[i] or "android-" in path[i]:
			android_log=open(path[i],"r",encoding='iso-8859-1') #该种格式打开，无法处理中文字符
			#android_log=open(log_file_list[i],"rb") #以二进制格式打开
			print("\nandroid log path >>>",path[i])
			while True:
				line = android_log.readline()
				if not line: break
				#if str.encode("PowerMonitor") in line: #如果以二进制形式打开问题文件，需要将PowerMonitor转成二进制
				for l in range(len(android_key_word)):
					if android_key_word[l-1]=='':break
					if (android_key_word[l-1] in line):	
						if android_key_word[l-1] == "OppoPowerMonitor":			
							if "OppoPowerMonitor: Actual current" in line:
									exsit_flag=True
									key_log_buff += '\n' + path[i] + '\n\n'

							if "OppoPowerMonitor: VminCount" in line:
								try:
									print ("\t",line,end="")
									exsit_flag=False
									key_log_buff += '\n' + path[i] + '\n\n'
								except:
									pass

							if exsit_flag==True:
								try:
									print ("\t",line,end="")
									key_log_buff += '\n' + log_file_list[i] + '\n\n'
								except:
									pass
							if "md_log on..." in line:
								try:
									print ("\t",line,end="")
									key_log_buff += '\n' + log_file_list[i] + '\n\n'
								except:
									pass
						else:
							try:
								print ("\t",line,end="")
								key_log_buff += '\n' + log_file_list[i] + '\n\n' 
							except:
								pass
	if key_log_buff == '':
		print ("parse android fail!") 
		parse_state='parse failed'
		return parse_state
	else:
		print ("parse android sucessful!") 
		parse_state='parse sucessful'
		return parse_state

#解析event log
def parse_event_log(path):
	global key_log_buff
	global parse_state
	key_log_buff = ''
	#print("文件数量：",len(log_file_list))
	for i in range(len(path)):	
		if "events" in path[i]:
			event_log=open(path[i],"r",encoding='iso-8859-1') #该种格式打开，无法处理中文字符
			#android_log=open(log_file_list[i],"rb") #以二进制格式打开
			print("\nevents log path >>>",path[i])
			while True:
				line = event_log.readline()
				if not line: break
				for l in range(len(event_key_word)):
					if event_key_word[l-1]=='':break	
					if event_key_word[l-1] in line:
						try:
							print ("\t",line,end="")
							key_log_buff += '\n' + path[i] + '\n\n'
						except:
							pass							 
	if key_log_buff == '':
		print ("event_log parse fail!") 
		parse_state='parse failed'
		return parse_state
	else:
		print ("event_log parse sucessful!") 
		parse_state='parse sucessful'
		return parse_state

#解析kernel log
def parse_kernel_log(path):
	global key_log_buff
	global parse_state
	global screen_state
	global Utc_time
	Utc_time=''
	screen_state = 0  #默认息屏状态
	key_log_buff = ''
	#print("文件数量：",len(path))
	for i in range(len(path)):
		if "dmesg" in path[i] or "kinfo" in path[i]:
			kernel_log=open(path[i],"r",encoding='iso-8859-1') #该种格式打开，无法处理中文字符
			#android_log=open(path[i],"rb") #以二进制格式打开
			print("\nkernel log path >>>",path[i])
			while True:
				line = kernel_log.readline()
				if not line: break
				if "ws_fb_notify_callback, UNBLANK" in line:  #亮屏状态
					screen_state=1;
					print ("\tScreen_state>>>on:",Utc_time,line,end="")                            
				elif "ws_fb_notify_callback, POWERDOWN" in line: #息屏状态
					screen_state=0;	
					print ("\tScreen_state>>>off:",Utc_time,line,end="")	    
				for l in range(len(kernel_key_word)):
					if kernel_key_word[l-1]=='':break	
					if kernel_key_word[l-1] in line:
						if (kernel_key_word[l-1] == "active wakeup source") and screen_state==1:
							continue
						elif (kernel_key_word[l-1] == "crtc_commit") and (line.find("wakeup")<0):
							continue
						elif (kernel_key_word[l-1] == "UTC"):
							#line1=line.strip()  #去掉换行符
							line1=re.split(' ',line)
							Utc_time = line1[l-4]+" "+line1[l-3]+" "+line1[l-2]
							if (line.find("WatchDog")>0):
								print ("\t",line,end="")
						else:
							try:
								print ("\t",line,end="")
								key_log_buff += '\n' + path[i] + '\n\n'
							except:
								pass												 
	if key_log_buff == '':
		print ("kernel_log parse fail!") 
		parse_state='parse failed'
		return parse_state
	else:
		print ("kernel_log parse sucessful!") 
		parse_state='parse sucessful'
		return parse_state

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
			change_to_realtime(savepath,input_file,path[i])
		elif "batterystats_oppoCheckin.txt" in path[i]:
			file_exist=True
			input_file = open(path[i], "r",encoding='iso-8859-1')
			change_to_realtime(savepath,input_file,path[i])
		elif "dumpsys_batterystats.txt"in path[i]:
			file_exist=True
			input_file = open(path[i], "r",encoding='iso-8859-1')
			change_to_realtime(savepath,input_file,path[i])
		elif "batterystats.txt"in path[i]:
			file_exist=True
			input_file = open(path[i], "r",encoding='iso-8859-1')
			change_to_realtime(savepath,input_file,path[i])
	if file_exist !=True:
		print("error! can not find batterystats file!")
		return -1

#将battersystats转换成真实时间，并重新输出到另外一个文件
def change_to_realtime(save_path,bat_path,write_path):
  global real_time
  real_time=""
  while True:
	  try:
	    line=bat_path.readline()
	  except Exception as e:
	    pass
	  if not line: break
	  if line.startswith("Battery History"):
	    print("Good Battery History File")
	    outputfile=open(save_path+'\\battersystats_realtime.txt',"a",encoding='utf-8')  #保存文件
	    outputfile.write("\n"+ "batterystates_log_path >>> "+ write_path +"\n"+"\n")
	  #获取起始时间
	  line_time=get_init_time(line)
	 
	  #获取转换后的时间
	  real_time=get_real_time(line,line_time)

	#重组写入文件
	  s = '%s %s' % (real_time,line)
	  try:
	    outputfile.write(s)
	  except Exception as e:
	    pass  
	  #print(s)     #2020-01-15 18:01:29                     0 (14) RESET:TIME: 2020-01-15-18-01-29
  outputfile.close()

#获取起始时间
def get_init_time(line):
	  global epoch_time
	  if "RESET:TIME:" in line:
	    #print (line)      #0 (14) RESET:TIME: 2020-01-15-18-01-29
#	    line=line.split()
#	    print (line)       #['0', '(14)', 'RESET:TIME:', '2020-01-15-18-01-29']
#	    init_time=line[3]
#	    print (init_time)
#	    init_time = datetime.datetime.strptime(init_time,'%Y-%m-%d-%H-%M-%S').strftime('%Y-%m-%d %H:%M:%S')
#	    print (init_time)
	    line_arr=re.split('\W+',line) #以非字符/数字进行分割 
	    line_arr=line_arr[1:-1]   #去掉前后两个字符 ['0', '14', 'RESET', 'TIME', '2020', '01', '15', '18', '01', '29']
	    #datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
	    epoch_time=datetime.datetime(int(line_arr[4]),int(line_arr[5]),int(line_arr[6]),int(line_arr[7]),int(line_arr[8]),int(line_arr[9]),0).timestamp()
	  #  print(epoch_time)      #1579082489.0 该值为起始时间的时间戳
	    #print (line_arr)       #['0', '14', 'RESET', 'TIME', '2020', '01', '15', '18', '01', '29'] 
	    time=datetime.datetime.fromtimestamp(epoch_time)
	  #  print (time)   #2020-01-15 18:01:29
	  elif "TIME:" in line and line.find("TOTAL")<0:
	  	line_arr=re.split('\W+',line)
	  	line_arr=line_arr[1:-1]
	  	#print("wayne:",line_arr) #['18h51m16s035ms', '14', 'TIME', '2020', '02', '29', '13', '09', '53']
	  	epoch_time=datetime.datetime(int(line_arr[3]),int(line_arr[4]),int(line_arr[5]),int(line_arr[6]),int(line_arr[7]),int(line_arr[8]),0).timestamp()
	  	#print(epoch_time)
	  line_time=re.split('\W+',line) #以非字符/数字进行分割 
	  line_time=line_time[1:-1]
	  #print(line_time)  #['0', '14', 'RESET', 'TIME', '2020', '01', '15', '18', '01', '29']
	  return line_time


#获取转换后的时间
def get_real_time(line,line_time):
	  global epoch_time	 
	  if line.isspace()!=True and line_time[0].find("ms")>=0:#该行非空格和且包含ms才进行时间分割
	    model = re.compile("[0-9]+")  #过滤非0-9的字符
	    retlist = model.findall(line_time[0]) 
	    #print(retlist)               #['4', '30', '25', '304']   [h,min,s,ms]
	    if len(retlist)==1:
	        add_time=int(retlist[0])/1000
	    elif len(retlist)==2:
	        add_time=int(retlist[0])+int(retlist[1])/1000
	    elif len(retlist)==3:
	        add_time=int(retlist[0])*60+int(retlist[1])+int(retlist[2])/1000
	    elif len(retlist)==4:
	        add_time=int(retlist[0])*60*60+int(retlist[1])*60+int(retlist[2])+int(retlist[3])/1000
	    elif len(retlist)==5:
	        add_time=int(retlist[0])*60*60*24+int(retlist[1])*60*60+int(retlist[2])*60+int(retlist[3])+int(retlist[4])/1000
	    else:
	        print("格式出错")
	        real_time=" "

	    if ("RESET:TIME:" in line) or ("TIME:" in line and line.find("TOTAL")<0):
	    	real_time=datetime.datetime.fromtimestamp(epoch_time)
	    	epoch_time=epoch_time-add_time
	    else:
	    	real_time=add_time+epoch_time
	    	real_time=datetime.datetime.fromtimestamp(real_time)
	  elif line.isspace()!=True and line.strip().split(' ')[0]=='0':   #开始几行时间为0的
	    real_time=datetime.datetime.fromtimestamp(epoch_time)  
	  else:
	    real_time=" "
	  return real_time

#############################parse_batterystates###################################

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


if __name__ == "__main__":
		config_path=os.path.join(os.getcwd(),"config")
		get_config(config_path)
		log_path = get_log_path()   
		for z in range(len(log_path)):
			creat_log_path=un_zip(log_path[z])
			print("creat_log_path:",creat_log_path)
			start_parse_log(creat_log_path)


