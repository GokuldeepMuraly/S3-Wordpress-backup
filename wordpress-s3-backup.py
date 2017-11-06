import os
import sys
import re
import subprocess
import tarfile

#####CODE TO PARSE WORDPRESS CONFIG FILE #######

def WPConfigParser(homedirpath):
 wpconfigfile = os.path.normpath(homedirpath+"/wp-config.php")
 with open(wpconfigfile) as fh:
  wpconfigcontent=fh.read()
  DBNAME = re.search(r'\s*define\(\'DB_NAME\'\,\s*\'(.*?)\'\)',wpconfigcontent).group(1)
  DBUSERNAME = re.search(r'\s*define\(\'DB_USER\'\,\s*\'(.*?)\'\)',wpconfigcontent).group(1)
  DBPASSWORD = re.search(r'\s*define\(\'DB_PASSWORD\'\,\s*\'(.*?)\'\)',wpconfigcontent).group(1)
  DBHOST = re.search(r'\s*define\(\'DB_HOST\'\,\s*\'(.*?)\'\)',wpconfigcontent).group(1)
  WordpressDict = {'Database':DBNAME,'Databaseusername':DBUSERNAME,'Databasepassword':DBPASSWORD,'Databasehost':DBHOST}
  return(WordpressDict)


##### CODE TO TAKE DATABASE BACKUP ########

def WPDBDump(db_details):
  USER = db_details['Databaseusername']
  PASSWORD = db_details['Databasepassword']
  HOST = db_details['Databasehost']
  DATABASE = db_details['Database']
  DUMPNAME = os.path.normpath(os.path.join(HOMEPATH,db_details['Database']+'.sql'))        
  cmd = "mysqldump  -u {} -p{} -h {} {}  > {} 2> /dev/null".format(\
                                    USER,PASSWORD, HOST, DATABASE, DUMPNAME)
  subprocess.check_output(cmd,shell=True)
  print('Completed')
  return DUMPNAME

#######TAKE ZIP FILE ############
def WPBackupTar(homedirpath):
 BACKUPPATH="/tmp/"
 tar = tarfile.open(BACKUPPATH+'backupfile.tar.gz','w:gz')
 tar.add(homedirpath)
 backupfile="/tmp/backupfile.tar.gz"
 tar.close()
 print(backupfile)
 return(backupfile)

########COPY FILE TO S3 BACKUP ########
def BackupMoveS3(backupfilename):
 command = "aws s3 mv /tmp/backupfile.tar.gz s3://wordpressbackupsteven/ 2> /dev/null"
 subprocess.call(command,shell=True) 
 print("COPYING COMPLETED")

#############DELETE BACKUP FILE ##############
def RemoveBackupFile():
 command = "rm -rf /tmp/backupfile.tar.gz 2> /dev/null"
 subprocess.call('command',shell=True) 

#######MAIN CODE ################
HOMEPATH = input("Enter the path which the Wordpress is installed:")
if os.path.exists(HOMEPATH):
 print("")
 print("")
 print("Enter the  path is correct and Processing request")
 DBINFO= WPConfigParser(HOMEPATH)
 WPDBDump(DBINFO)
 ZIPFILE= WPBackupTar(HOMEPATH)
 BackupMoveS3(ZIPFILE)   
 RemoveBackupFile() 
else:
 print("GIVEN NON EXITENT PATH")
