import os
import re
import datetime
import time
import sys
'''
1.获取file_path路径下的文件夹，返回数组
2.获取file_path路径下的文件filelist，返回数组
'''

def getfilepath(file_path):
	dirlist=[]
	filelist=[]
	#for log in os.walk(file_path):  #os.walk(file_dir) 为generator类型，不能直接打印
	#	print("os.walk:",log)
	for root, dirs, files in os.walk(file_path):
		'''
		print("root:",root)   #os.walk()所在目录
		print ("dir:",dirs)   #os.walk()所在目录的所有目录名
		print ("files:",files)   #os.walk()所在目录的所有非目录文件名
		'''
		dirlist.append(root)
		for filename in files:
			filelist.append(os.path.join(root,filename))
	print("该路径下的所有文件:{0}\n".format(filelist))
	print("该路径下的所有文件夹:{0}\n".format(dirlist))
	return filelist,dirlist

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


#获取每行绝对时间(timestamp)+实际时间(real_time)
def gettime(batterystats_log,line_list):
	global epoch_time
	global timestamp
	#获取起始时间 
	if "TIME: " in batterystats_log :
		r,t,line_arr=batterystats_log.partition('TIME: ')#第一个为分隔符左边的子串，第二个为分隔符本身，第三个为分隔符右边的子串
		if bool (re.search('[a-z]',line_arr)) == False:
			line_arr=line_arr.split('-')   #去掉前后两个字符 ['2020', '01', '15', '18', '01', '29']
			epoch_time=datetime.datetime(int(line_arr[0]),int(line_arr[1]),int(line_arr[2]),int(line_arr[3]),int(line_arr[4]),int(line_arr[5]),0).timestamp()
			time=datetime.datetime.fromtimestamp(epoch_time)
			#print("batterystats 起始时间：{0}".format(time))

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
#		parseline_info_after['times']=add_time+epoch_time
	elif batterystats_log.isspace()!=True and batterystats_log.strip().split(' ')[0]=='0':   #开始几行时间为0的
		timestamp=epoch_time
		real_time=datetime.datetime.fromtimestamp(epoch_time) 
	else:
		real_time=" "
	#print("实际时间戳时间：{0}".format(real_time)) #实际时间戳时间：2020-04-23 16:09:30.643000
	return real_time,timestamp

#计算平均电流
def avg_current(batterystats_log,line_list):
	global charge_state
	if "charge=" in batterystats_log:
		r,t,ColValue=batterystats_log.partition('charge=') #第一个为分隔符左边的子串，第二个为分隔符本身，第三个为分隔符右边的子串
		#print(batterystats_log[0:4])  #只截取charge= 后面5个字符
		Col=re.sub("\D","",ColValue[0:4]) #过滤掉非数字的字符,获取库伦值 '3840'

		if charge_state=="before":
			parseline_info_before['Col']=int(Col)
			(real_time,parseline_info_before['times'])=gettime(batterystats_log,line_list)
			charge_state="after"
		#print(parseline_info_after['Col'])
		#Collist.append(Col) #库仑计列表list
		elif charge_state=="after":
			parseline_info_after['Col']=int(Col)
			(real_time,parseline_info_after['times'])=gettime(batterystats_log,line_list)
			charge_state="before"					
		#计算平均电流
		if (parseline_info_after['Col']!=parseline_info_before['Col']) and (parseline_info_after['times']!=parseline_info_before['times']) and (parseline_info_after['Col']!=0):
			avg_current=(parseline_info_before['Col']-parseline_info_after['Col'])*3600/(parseline_info_after['times']-parseline_info_before['times'])
			print("{0} 平均电流：{1} ma".format(real_time,avg_current))

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
			screen_change_time=screen_change_time+1					
		if "+screen " in batterystats_log:
			(screen_on_realtime,screen_on_time)=gettime(batterystats_log,line_list)
			screen_change_time=screen_change_time+1
			#print("rela_time:{0},screen_on_time:{1}".format(real_time,screen_on_time))
			screenstate="ON"
			print("{0} 亮屏".format(screen_on_realtime))
		if screen_on_time!=0 and screen_off_time!=0 and (screen_on_time-screen_off_time)>0:
			screen_off_total_time=screen_off_total_time+(screen_on_time-screen_off_time)
			#print("screen_off_total_time:{0}".format(screen_off_total_time))
		if screen_on_time!=0 and screen_off_time!=0 and (screen_on_time-screen_off_time)<0:
			screen_on_total_time=screen_on_total_time+(screen_off_time-screen_on_time)
			#print("screen_on_total_time:{0}".format(screen_on_total_time))	

#统计屏幕亮度
def getbrightness(batterystats_log,line_list):
	global brightness_level
	global brightrealtimebefore
	global brighttimebefore
	if "brightness=" in batterystats_log:
		#global screen_on_time
		#global screen_off_time
		t,m,brightness=list(batterystats_log.partition("brightness="))
		brightness=brightness.strip().split(' ')
		#print(brightness[0])
		(actultime,timestamp)=gettime(batterystats_log,line_list)
		#print(screen_on_time,timestamp,screen_off_time,brightness_level)
		if (brighttimebefore<screen_off_time<screen_on_time<timestamp):
			if brightness_level==1:
				print("{0}到{1} 亮度等级1(dark) 总时长：{2}min".format(brightrealtimebefore,screen_off_realtime,(screen_off_time-brighttimebefore)/60))	
				print("{0}到{1} 亮度等级1(dark) 总时长：{2}min".format(screen_on_realtime,actultime,(timestamp-screen_on_time)/60))									
			if brightness_level==2:
				print("{0}到{1} 亮度等级2(dim) 总时长：{2}min".format(brightrealtimebefore,screen_off_realtime,(screen_off_time-brighttimebefore)/60))	
				print("{0}到{1} 亮度等级2(dim) 总时长：{2}min".format(screen_on_realtime,actultime,(timestamp-screen_on_time)/60))
			if brightness_level==3:
				print("{0}到{1} 亮度等级3(medium) 总时长：{2}min".format(brightrealtimebefore,screen_off_realtime,(screen_off_time-brighttimebefore)/60))	
				print("{0}到{1} 亮度等级3(medium) 总时长：{2}min".format(screen_on_realtime,actultime,(timestamp-screen_on_time)/60))
			if brightness_level==4:
				print("{0}到{1} 亮度等级4(light) 总时长：{2}min".format(brightrealtimebefore,screen_off_realtime,(screen_off_time-brighttimebefore)/60))	
				print("{0}到{1} 亮度等级4(light) 总时长：{2}min".format(screen_on_realtime,actultime,(timestamp-screen_on_time)/60))
			if brightness_level==5:
				print("{0}到{1} 亮度等级5(bright) 总时长：{2}min".format(brightrealtimebefore,screen_off_realtime,(screen_off_time-brighttimebefore)/60))	
				print("{0}到{1} 亮度等级5(bright) 总时长：{2}min".format(screen_on_realtime,actultime,(timestamp-screen_on_time)/60))						
			if brightness[0]=='dark':brightness_level=1
			if brightness[0]=='dim':brightness_level=2
			if brightness[0]=='medium':brightness_level=3
			if brightness[0]=='light':brightness_level=4									
			if brightness[0]=='bright':brightness_level=5
			brightrealtimebefore=actultime
			brighttimebefore=timestamp


		else:

			if brightness_level==1:
				print("{0}到{1} 亮度等级1(dark) 总时长：{2}min".format(brightrealtimebefore,actultime,(timestamp-brighttimebefore)/60))					
			if brightness_level==2:
				print("{0}到{1} 亮度等级2(dim) 总时长：{2}min".format(brightrealtimebefore,actultime,(timestamp-brighttimebefore)/60))
			if brightness_level==3:
				print("{0}到{1} 亮度等级3(medium) 总时长：{2}min".format(brightrealtimebefore,actultime,(timestamp-brighttimebefore)/60))
			if brightness_level==4:
				print("{0}到{1} 亮度等级4(light) 总时长：{2}min".format(brightrealtimebefore,actultime,(timestamp-brighttimebefore)/60))
			if brightness_level==5:
				print("{0}到{1} 亮度等级5(bright) 总时长：{2}min".format(brightrealtimebefore,actultime,(timestamp-brighttimebefore)/60))							
			if brightness[0]=='dark':brightness_level=1
			if brightness[0]=='dim':brightness_level=2
			if brightness[0]=='medium':brightness_level=3
			if brightness[0]=='light':brightness_level=4									
			if brightness[0]=='bright':brightness_level=5
			brightrealtimebefore=actultime
			brighttimebefore=timestamp


#统计app运行情况
def  app_info(batterystats_log,line_list):
	global app_close_time
	global app_open_time
	global app_open_real_time
	global app_close_real_time
	if "top=u0a" in batterystats_log:
		if "+top=u0a" in batterystats_log:
			(app_open_real_time,app_open_time)=gettime(batterystats_log,line_list)
			topname=re.findall(r'["](.*?)["]', batterystats_log)#['com.oppo.launcher']
			#print("{0} 运行 {1}".format(real_time,topname)) 
		if "-top=u0a" in batterystats_log:
			(app_close_real_time,app_close_time)=gettime(batterystats_log,line_list)
			topname1=re.findall(r'["](.*?)["]', batterystats_log)#['com.oppo.launcher']
			#print("{0} 退出 {1}".format(real_time,topname1)) 
		if (app_close_time!=app_open_time!=0) and (app_close_time-app_open_time)>0 and (app_close_time-app_open_time)>60:
			print("{0}至{1}：运行{2} {3}min\n".format(app_open_real_time,app_close_real_time,topname1,(app_close_time-app_open_time)/60))

#获取电量百分比
def getbatlevel(line_list):
	global real_time
	global batterylevel
	if len(line_list)>3 and line_list[2].isdigit()==True and len(line_list[2])==3 and (0<=int(line_list[2])<=100)==True:
		if line_list[2]!=batterylevel:
			print("{0} 电池电量：{1}%".format(real_time,line_list[2]))
			batterylevel=line_list[2]
		return line_list[2]
#获取电池温度
def getbattemp(batterystats_log):
	if "temp=" in batterystats_log:
		r,t,temp=batterystats_log.partition('temp=')
		temp=int(re.sub("\D","",temp[0:3]))/10.0 #过滤掉非数字的字符,获取温度值 '384'
		print("{0} 电池温度：{1} ℃".format(real_time,temp))
		return temp

#job锁统计
def getjobinfo(batterystats_log,line_list):
	global jobnamelist
	global jobtime
	global jobrealtime
	global jobdict
	global jobdict2
	if "job=" in batterystats_log:
		if "+job=" in batterystats_log:
			r,t,jobname=batterystats_log.partition('+job=')
			jobname=re.findall(r'["](.*?)["]', jobname)#['com.heytap.mcs/.statistics.upload.UploadJobService']
			(real_time,job_start_time)=gettime(batterystats_log,line_list)
			jobnamelist.append(jobname[0])
			jobtime.append(job_start_time)
			jobrealtime.append(real_time)
			jobdict=dict(zip(jobnamelist,jobtime))
			jobdict2=dict(zip(jobnamelist,jobrealtime))
			#print("{0} {1} job开始".format(real_time,jobname))

		if "-job=" in batterystats_log:
			r,t,jobname=batterystats_log.partition('-job=') #第一个为分隔符左边的子串，第二个为分隔符本身，第三个为分隔符右边的子串
			jobname=re.findall(r'["](.*?)["]', jobname)#['com.heytap.mcs/.statistics.upload.UploadJobService']
			(real_time,job_end_time)=gettime(batterystats_log,line_list)
			if jobname[0] in jobnamelist:
				if ((job_end_time-jobdict[jobname[0]])/60)>=1:
					print("{0}到{1} {2}持锁 总持锁时长：{3} min".format(jobdict2[jobname[0]],real_time,jobname[0],(job_end_time-jobdict[jobname[0]])/60))			
				
				del jobdict[jobname[0]]
				del jobdict2[jobname[0]]
				#print("{0} {1} job结束".format(real_time,jobname))				


#longwake持锁统计
def getlongwakeinfo(batterystats_log,line_list):
	global longwakelist
	global longwaketime
	global longwakerealtime
	global s
	global s1
	if "longwake=u0a" in batterystats_log:
		if "+longwake=u0a" in batterystats_log:
			r,t,longwakename=batterystats_log.partition('+longwake=u0a') #第一个为分隔符左边的子串，第二个为分隔符本身，第三个为分隔符右边的子串
			longwakename=re.findall(r'["](.*?)["]', longwakename)
			(real_time,longwake_start_time)=gettime(batterystats_log,line_list)
			longwakelist.append(longwakename[0])
			longwaketime.append(longwake_start_time)
			longwakerealtime.append(real_time)
			s=dict(zip(longwakelist,longwaketime))
			s1=dict(zip(longwakelist,longwakerealtime))
			#print(s)
			#print("{0} 持锁：{1}".format(real_time,longwakename))

		if "-longwake=u0a" in batterystats_log:
			r,t,longwakename=batterystats_log.partition('-longwake=u0a') #第一个为分隔符左边的子串，第二个为分隔符本身，第三个为分隔符右边的子串
			longwakename=re.findall(r'["](.*?)["]', longwakename)
			(real_time,longwake_end_time)=gettime(batterystats_log,line_list)
			if longwakename[0] in longwakelist:
				#print(s[longwakename[0]])
				print("{0}到{1} {2}持锁 总持锁时长：{3} min".format(s1[longwakename[0]],real_time,longwakename[0],(longwake_end_time-s[longwakename[0]])/60))
				del s[longwakename[0]]
				del s1[longwakename[0]]

#相机使用情况
def getcamerainfo(batterystats_log,line_list):
	global camera_on_time
	global camera_off_time
	global camera_on_real_time
	global camera_off_real_time
	global camera_on_total_time
	if "camera" in batterystats_log:
		if "+camera" in batterystats_log:
			(camera_on_real_time,camera_on_time)=gettime(batterystats_log,line_list)
			#print("rela_time:{0},screen_on_time:{1}".format(real_time,screen_on_time))
			#print("{0} 开启相机".format(camera_on_real_time))

		if "-camera" in batterystats_log:
			(camera_off_real_time,camera_off_time)=gettime(batterystats_log,line_list)	
			#print("rela_time:{0},screen_off_time:{1}".format(real_time,screen_off_time))
			#print("{0} 关闭相机".format(camera_off_real_time))
			if (camera_off_time-camera_on_time)>60:
				print("相机使用>1min的点:{0}到{1},共使用：{2} min".format(camera_on_real_time,camera_off_real_time,(camera_off_time-camera_on_time)/60))		

		if camera_on_time!=0 and camera_off_time!=0 and (camera_on_time-camera_off_time)<0:
			camera_on_total_time=camera_on_total_time+(camera_off_time-camera_on_time)
			#print("screen_on_total_time:{0}".format(screen_on_total_time))	
#充电信息
def getchargeinfo(batterystats_log,line_list):
	global charge_start_time
	global charge_end_time
	global charge_start_real_time
	global charge_end_real_time
	
	if "status=" in batterystats_log:
		if "=charging" in batterystats_log:
			(charge_start_real_time,charge_start_time)=gettime(batterystats_log,line_list)
		if "=not-charging" in batterystats_log:
			(charge_end_real_time,charge_end_time)=gettime(batterystats_log,line_list)	
			if (charge_end_time-charge_start_time)>0 and (charge_end_time!=charge_start_time!=0):
				print("{0}到{1}处于充电阶段,共充电 {2} min".format(charge_start_real_time,charge_end_real_time,(charge_end_time-charge_start_time)/60))
				charge_start_time=0	


def parse_batterystats(filepath):
	global epoch_time
	global timestamp
	global real_time
	epoch_time=0
	timestamp=0

	#平均电流变量参数
	global charge_state
	global parseline_info_before
	global parseline_info_after
	charge_state="before"
	parseline_info_before = {'Col':0,'times':0}
	parseline_info_after  = {'Col':0,'times':0}

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

	#app统计信息
	global app_close_time
	global app_open_time
	global app_open_real_time
	global app_close_real_time
	app_close_time=0
	app_open_time=0

	#电池电量统计
	global batterylevel
	batterylevel=0

	#job锁统计
	global jobnamelist
	global jobtime
	global jobrealtime
	global jobdict
	global jobdict2	
	jobnamelist=[]
	jobtime=[]
	jobrealtime=[]
	jobdict={}
	jobdict2={}

	#持锁统计信息
	global longwakelist
	global longwaketime
	global longwakerealtime
	global s
	global s1
	s={}
	s1={}
	longwakelist=[]
	longwaketime=[]
	longwakerealtime=[]

	#相机统计
	global camera_on_time
	global camera_off_time
	global camera_on_real_time
	global camera_off_real_time
	global camera_on_total_time
	camera_on_time=0
	camera_off_time=0
	camera_on_total_time=0
	camera_off_real_time=0
	camera_on_real_time=0

	#充电信息
	global charge_start_time
	global charge_end_time
	global charge_start_real_time
	global charge_end_real_time
	charge_start_time=0
	charge_end_time=0
	charge_start_real_time=0
	charge_end_real_time=0

	#屏幕亮度统计
	global brightness_level
	global brightrealtimebefore
	global brighttimebefore
	brightness_level=0
	brightrealtimebefore=0
	brighttimebefore=0

	for i in range(len(filepath)):
		if "dumpsys_batterystats.txt" in filepath[i] or "batterystats_oppoCheckin.txt" in filepath[i] \
		or "batterystats.txt" in filepath[i] or "battersystats.txt" in filepath[i] :
			#print("解析文件：{0}\n".format(filepath[i]))
			batterystats=open(filepath[i],"r",encoding='utf-8')
			while True:
				batterystats_log=batterystats.readline()
				if not batterystats_log: break #如果为空行则退出
				line_list=re.split('\W+',batterystats_log) #以非字符/数字进行分割 
				line_list=line_list[1:-1]
				#print(line_list) #['4h58m31s561ms', '2', '065', 'top', 'u0a47', 'android', 'process', 'contacts']
				(real_time,timestamp)=gettime(batterystats_log,line_list)		
				
				#获取电量百分比
				getbatlevel(line_list)
				
				#获取电池温度
				#getbattemp(batterystats_log)

				#计算平均电流
				avg_current(batterystats_log,line_list)

				#应用使用情况
				app_info(batterystats_log,line_list)

				#亮灭屏状态
				screen_summary(batterystats_log,line_list)
				
				#统计屏幕亮度
				getbrightness(batterystats_log,line_list)
				#job锁统计
				getjobinfo(batterystats_log,line_list)	
				
				#longwake统计
				getlongwakeinfo(batterystats_log,line_list)

				#相机使用情况统计
				getcamerainfo(batterystats_log,line_list)
				
				#充电情况
				getchargeinfo(batterystats_log,line_list)
				



	

						





				
			
			#print("息屏时长:{0}h,亮屏时长:{1}h,亮灭屏:{2}次".format(screen_off_total_time/3600,screen_on_total_time/3600,(screen_change_time-1)))

if __name__ == "__main__":
	log_path=get_log_path()
	for z in range(len(log_path)):
		(filelist,dirlist)=getfilepath(log_path[z])
		saveout = sys.stdout
		saveerr = sys.stderr 
		outputfile=open(log_path[z]+'\\summary.txt',"w") #"a"可在文本末继续写入
		sys.stdout=outputfile
		sys.stderr=outputfile		
		parse_batterystats(filelist)
		sys.stdout=saveout
		sys.stderr=saveerr 
















