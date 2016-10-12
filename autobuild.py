# -*- coding: utf-8 -*-
import os
import sys
import time
import hashlib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

#===============================================参数配置begin==================================================================================
# 项目是否使用cocoaPods:1-是 0-不是
userCocoaPods = 1
# 项目工程文件名字:比如：JZGDetectionPlatform.xcodeproj（非cocoaPods） 或者 JZGDetectionPlatform.xcworkspace（cocoaPods）
project_name = "JZGERSecondPhase"
# 项目scheme名字：比如：JZGDetectionPlatformForOffice 或者JZGDetectionPlatformForPgs
scheme_name = "JZGERSecondPhase"
# 归档类型：Release版或者Debug版
configuration = "Debug"
# 证书概要文件：
# 机构端   #Debug：JZGDetectionPlatform         #Release：JZGDetectionPlatformForAppStore
# 评估师端 #Debug：JZGDetectionPlatformForPgs   #Release：JZGDetectionPlatformForPgsForAppStore
ProvisioningProfile = "JZGNormalERP"
#===============================================
# 项目根目录:xcodebuild命令必须进入的项目目录   绝对目录
project_path = "/Users/duweixin/Desktop/JZGERSecondPhase"
# 编译后项目的app根目录：即build的.app所在的根目录
build_root_path = project_path
# 编译成功后.app所在目录
build_app_path = "%s/build/Build/Products/Release-iphoneos/%s.app" %(build_root_path,scheme_name)
# 指定项目下编译目录
#build_path = "build"
build_path = "%s/build" %(build_root_path)
#===============================================
# 打包后ipa存储目录
targetIPA_path = "/Users/duweixin/Desktop/dabao"
#===============================================
#蒲公英网站的两个key和上传路径
API_Key = "a327ec8f8caa3xxxx9a2bc9bbffd7621"
User_Key = "bfa400a07cb7aac72432191719375672"
pgyUploadUrl = "https://www.pgyer.com/apiv1/app/upload"
#===============================================
#邮件参数配置
from_addr = "xxxx@126.com"
password = "您的邮箱密码"
smtp_server = "smtp.126.com"
to_addr = ''
#==============================================参数配置end===================================================================================


#==============================================具体操作的方法begin===================================================================================
# 清理项目 创建build目录*****************************************************************
def clean_project_mkdir_build():
    if userCocoaPods == 1 :#使用cocoaPods，才需要创建目录
        os.system('cd %s;xcodebuild clean -workspace %s.xcworkspace -configuration %s -target %s' % (project_path,project_name,configuration,scheme_name)) # clean 项目
        os.system('cd %s;mkdir build' % project_path) # 创建build目录
    else:
        #xcodebuild clean -project ${PROJECT_NAME}.xcodeproj -configuration ${CONFIGURATION} -alltargets
        os.system('cd %s;xcodebuild clean -project %s.xcodeproj -configuration %s  -target %s' % (project_path,project_name,configuration,scheme_name)) # clean 项目

# 编译工程为.app或者.xcarchive*****************************************************************
def build_project():
    print("build %s start"%(configuration))
    os.system ('xcodebuild -list')
    
    if userCocoaPods == 1 :#使用cocoaPods
#        build_string = "cd %s;xcodebuild -workspace %s.xcworkspace  -scheme %s -configuration %s -derivedDataPath %s ONLY_ACTIVE_ARCH=NO || exit" % (project_path,project_name,scheme_name,configuration,build_path)
        build_string = "cd %s;xcodebuild -workspace %s.xcworkspace -scheme %s -configuration %s -archivePath build/%s.xcarchive archive" % (project_path,project_name,scheme_name,configuration,scheme_name)
        print("使用cocoaPods：编译命令：%s" %(build_string));
        os.system (build_string)
    else:#使用非cocoaPods
#        build_string = "cd %s;xcodebuild -project %s.xcodeproj  -scheme %s -configuration %s -derivedDataPath %s ONLY_ACTIVE_ARCH=NO || exit" % (project_path,project_name,scheme_name,configuration,build_path)
        build_string = "cd %s;xcodebuild  -scheme %s -configuration %s -archivePath build/%s.xcarchive archive" % (project_path,scheme_name,configuration,scheme_name)
        print("不使用cocoaPods：编译命令：%s" %(build_string));
        os.system (build_string)

# 打包ipa 并且保存在桌面*****************************************************************
def build_ipa():
    global ipa_filename
    ipaName = scheme_name;
    ipa_filename = ipaName + "_" + configuration + time.strftime('_%Y-%m-%d-%H-%M-%S.ipa',time.localtime(time.time()))
#    os.system ('xcrun -sdk iphoneos PackageApplication -v %s -o %s/%s'%(build_app_path,targetIPA_path,ipa_filename))
#    os.system ('xcrun -sdk iphoneos xcodebuild -exportArchive  %s  %s/%s'%(build_app_path,targetIPA_path,ipa_filename))

    build_ipa_string = "xcodebuild  -exportArchive -exportFormat IPA -archivePath %s/%s.xcarchive -exportPath %s/%s -exportProvisioningProfile %s" % (build_path,scheme_name,targetIPA_path,ipa_filename,ProvisioningProfile)
    print("编译ipa包命令：%s" %(build_ipa_string));
    os.system (build_ipa_string)


# 上传ipa包到蒲公英服务器*****************************************************************
def upload_pgy():
    if os.path.exists("%s/%s" % (targetIPA_path,ipa_filename)):
        print('watting...')
        # 直接使用fir 有问题 这里使用了绝对地址 在终端通过 which fir 获得
        codeStr = "curl -F file=@%s/%s -F uKey=%s -F _api_key=%s %s" % (targetIPA_path,ipa_filename,User_Key,API_Key,pgyUploadUrl)
        print("上传命令：%s" %codeStr);
        ret = os.system(codeStr)
    else:
        print("没有找到ipa文件")
# 发邮件
def send_mail():
    msg = MIMEText('xx iOS测试项目已经打包完毕，请前往 http://fir.im/xxxxx 下载测试！', 'plain', 'utf-8')
    msg['From'] = _format_addr('自动打包系统 <%s>' % from_addr)
    msg['To'] = _format_addr('xx测试人员 <%s>' % to_addr)
    msg['Subject'] = Header('xx iOS客户端打包程序', 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

#main方法，依次调用上面的几个方法
def main():
    # 清理并创建build目录
    clean_project_mkdir_build()
    # 编译coocaPods项目文件并 执行编译目录
    build_project()
    # 打包ipa 并制定到桌面
    build_ipa()
    #上传到蒲公英服务器
    upload_pgy()
    #发送邮件
    send_mail()
#==============================================具体操作的方法end===================================================================================


# 执行
main()










