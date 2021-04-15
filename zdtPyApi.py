# The Module contains functions used by zdtVcreate, zdtVresize and zdtmsg. 
# It is not called directly.
#  
# 
# 
#
#


import sys
import os
import getpass
import subprocess
import uuid 
import time
import pwd
import re
import socket
from subprocess import PIPE
from time import gmtime, strftime




# This very impressive and lengthy function prints text in Red .. I know eh .... you're blown away.
def prRed(prt):
    print("\033[91m {}\033[00m" .format(prt))



# You won't believe it is possible, but, this prints text in Cyan... no b.s.  
def prCyan(prt):
    print("\033[96m {}\033[00m" .format(prt))


# Used for stopZos to check if a task is still running or not
def chkEndTask():
    global zosIsUp 
    chkStat = str('d a,'+endTask)
    foundTask = 'no'
    zosIsUp = 'yes'
    sendOprMsg(chkStat, curLogFile, slpTime, 't')
    for lines in trapMsg.splitlines():
        if endTask+" NOT FOUND" in lines:
            zosIsUp = 'no'
    if "%NETV" not in shutCmd and zosIsUp == 'yes':
        sendOprMsg("$DJES2", curLogFile, 1, 't')
        for lines in trapMsg.splitlines():
            if "$HASP608" in lines and "STC" in lines:
                pass
            else:
                sendOprMsg("$PJES2", curLogFile, 1, 't')


# Check to see who is logged on and ensure can access zPDT .. typically ibmsys1.
def getLoggedUser():
    global loggedUser
    loggedUser = pwd.getpwuid( os.getuid() ).pw_name
    try:
        subprocess.check_output("awsstat") 
    except subprocess.CalledProcessError as awserr:
        if b"1090 instance is not active" in awserr.output:
            pass       
    except:
        prRed("Warning: This Utility must be executed from the an account that has access")
        prRed("         to the z1090 binaries. This is typically the account used to start the zPDT Emulator")
        prRed("         Please switch to an appropriate user.")
        sys.exit()




# Getting into this function means you need help. How seriously you need help, well I can't tell, maybe visit a doctor.
def printHelp():
    if 'zdtVresize' in sys.argv[0]:
        prCyan("** zdtVresize Input Requirements: **")
        print("Run this utility from within the directory containing your zPDT Disk Volumes, or use the -d option")
        print(" ")
        print("-i Disk-File-Name   Required: Existing Linux Disk File to Resize")
        print("-s New_Size         Required: New Larger Size (Acceptable are 3,9,27,or 54)")
        print(" ")
        print("-d Volume Directory Optional: zPDT Volume Directory, Default will be current working Directory")
        print("-ipaddr x.x.x.x     Optional: Valid only when using -ssh option. Use to specify z/OS host IP Address if not default 10.1.1.2")
        print("-m                  Optional: No automatic ICKDSF REFVTOC processing")
        print("-port               Optional: When using -ssh, specify alternate z/OS SSH Port, if z/OS is not using default port 22")
        print("-ssh                Optional: Use SSH to submit JCL and retreive output from z/OS.")
        print("                              Using an SSH key between Linux and z/OS is recommended. It will still work")
        print("                              without a key, however, you will be prompted several times for password.")
        print("                              Default option is to use awsrdr and awsprt stanzas for JCL submission/output retrieval")
        print("-u userid           Optional: z/OS Userid for submitting JCL. Default is IBMUSER")
        print("-v Volser           Optional: z/OS Volser Name (only needed if Linux File Name and Volser are NOT equal)")
        print(" ")
        print("EXAMPLES: ")
        print("   zdtVresize -i TEST01 -s 27                                     Resize TEST01 to Mod 27, TEST01 currently mounted volume")
        print("   zdtVresize -i -d /z/volumes ZDTVOLUME1 -v TEST01 -s 27         Linux Disk file is not same a z/OS volume so -v argument required")
    elif 'stopZos' in sys.argv[0]:
        prCyan("** stopZos Input Requirements: **")
        print("Run this utility with linux user that starts zPDT and IPLs z/OS")
        print(" ")
        print("-c z/OS Shutdown Command      Optional: The z/OS Console command to shutdown z/OS. Default is %netv shutsys, which only works for ADCD")
        print("-z Final z/OS Subsystem       Optional: Task to check to ensure z/OS is completely down. Default is JES2")
        print("-t Timeout (seconds)          Optional. Default is 300 Seconds.")
        print("-awsstop                      Optional. If specified then zPDT command awsstop will be executed after timeout or after z/OS is down.")

    elif 'zdtVcreate' in sys.argv[0]:
        prCyan("** zdtVcreate Input Requirements: **")
        print("Run this utility from within the directory containing your zPDT Disk Volumes, or use the -d option")
        print(" ")
        print("-v Disk-File      Required: Linux Disk File/Volser to Create. Must be length 6 (Alpha/Numeric/@/#/$)")
        print(" ")
        print("-d Vol Directory  Optional: zPDT Volume Directory, Default will be current working Directory")
        print("-m                Optional. Manual processing, No mounting of new Disk to zPDT, nor vary online to z/OS.")
        print("-nodmap           Optional: Do NOT update DEVMAP file")          
        print("-sms              Optional: Create an SMS volume. Default is Non-SMS")
        print("-s Volume_Size    Optional: New Disk Volume Size. (Acceptable 1,3,9,27,54) Default is 1")
        print("                            Default size is 1113 Cylinders (Mod 1)")
        print("                            Mod size examples:" )
        print("                            A 3390 Mod 1 is 1113 Cylinders." )
        print("                            A 3390 Mod 3 is 3339 Cylinders. (Mod 1 times 3)")
        print("                            A 3390 Mod 27 is 30051 Cylinders. (Mod 1 times 27)")
        print("EXAMPLES: ")
        print("   zdtVcreate -v USER01 -s 9 -sms        ; SMS Mod 9 volume")
        print("   zdtVcreate -v TEST00 -d /z -s 27      ; Non SMS Mod 27 volume to be created in directory /z")
        print("   zdtVcreate -v TEST02 -s 27            ; nodmap   - do not update Devmap file")
        print("   zdtVcreate -v TEST02 -m -s 27         ; Just create the new file, no automatic mounting etc")
    elif 'zdtpdsu' in sys.argv[0]:
        prCyan("** zdtpdsu Input Requirements: **")
        print("Run this utility with linux user that starts zPDT and IPLs z/OS. zdtpdsu is really just a 'wrapper' for the pdsUtil zPDT command")
        print(" ")
        print("-d Volume Directory           Optional: will default to current directory")
        print("-v Volume Name                Required: Volume containing the PDS to be updated")
        print("-p PDS Name                   Required: PDS Name containing the Member to be updated")
        print("-q Member Name                Required: Member Name to be updated.")
        print("-r Search String              Optional: Quoted Search String to be replaced by Replacement String.")
        print("-x Replacement String         Optional: Quoted Replacement string which will replace Search String.")

    else:
        prCyan("** zdtmsg Input Requirements: **")
        print("-w       Optional: time to wait for messages, default is .5 seconds, supported with Python 3.3 or greater")
        print(" ")
        print("EXAMPLES: ")
        print("   oprmsg 'd a,l'")
        print("   oprmsg 'd a,l' -w 10   - wait 10 seconds for messages")




# Here were are starting to do some stuff .. ICKDSF is pretty powerful .. hopefully I didn't make any coding errors and happen 
# to wipe out your disk... if so .. sorry .. but you gave me the password.
# This funcion will submit the below JCL to the 00C "hot" reader on z/OS. In ADCD (JES2) this is configured as RDR(1)
def subIckdsfJcl(zosVol,zosStat):
    global zdtJFile, fndOut, jclFile, prtFile
    upzosVol = zosVol.upper()
    ickUid = str(uuid.uuid4())
    ickFile = ickUid + str('.txt')
    prtFile = ickUid + str('_out.txt')
    if sshSub != 'y':
        jclFile = devRdrDir+ickFile
    else:
        jclFile = str('/tmp/')+ickFile
        zdtJFile = str('/tmp/')+prtFile
    pwd = '1'
    pwd2 = '2'
    if sshSub != 'y':
        while (pwd != pwd2):
            pwd = getpass.getpass(prompt='\033[91m Enter '+inUid+' TSO ID Password, it will be hidden from display:\033[00m ').upper()
            pwd2 = getpass.getpass(prompt='\033[91m RE-Enter Password for verification: \033[00m').upper()
            if pwd != pwd2:
                prRed("Passwords do not match.. retry")
    if zosStat == 'up' and sshSub != 'y':        
        sendOprMsg('$tprt1,writer=awsprt,f=std,fcb=ex01,class=p,setup=nohalt', curLogFile, 1, 'n')
        try:
            if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
                subprocess.run(["awsmount", "00E", "-u"],stderr=PIPE, stdout=PIPE)
            else:
                subprocess.call(["awsmount", "00E", "-u"],stderr=PIPE, stdout=PIPE)
        except:
            pass
        
                   
    # Mount the awsprt device with the file to receive output 
    if zdtPRT == 'y' and sshSub != 'y':
        zdtJFile = prtDir+ickFile
        subprocess.call(["awsmount", "00E", "-m", zdtJFile])
        # Start printer
        sendOprMsg('$sprt1', curLogFile, 1, 'n')
            
    # Create the ICKDSF REFVTOC JCL. Once written to the awsrdr directory JES2 should process automatically
    j = open(jclFile, "w+")
    j.write("//ZDTRVTOC JOB CLASS=A,MSGCLASS=H,REGION=0M,\n")
    if sshSub == 'y':
        j.write("//         NOTIFY=&SYSUID\n")
    else:
        j.write("//         NOTIFY=&SYSUID,\n")
        j.write("//         USER="+inUid+",PASSWORD="+pwd+"\n")
        j.write("//ZDTOUT   OUTPUT WRITER=AWSPRT\n")
    j.write("//S1 EXEC PGM=ICKDSF,PARM='NOREPLYU'\n")
    if sshSub == 'y':
        j.write("//SYSPRINT DD DSN=&&SYSPRT,DISP=(,PASS),\n")
        j.write("//         SPACE=(TRK,(1,1),RLSE),UNIT=SYSALLDA,\n")
        j.write("//         LRECL=125,RECFM=VBA,BLKSIZE=629\n")
    else:
        j.write("//SYSPRINT DD SYSOUT=P,OUTPUT=*.ZDTOUT\n")
    j.write("//DASD1    DD VOL=SER="+upzosVol+",UNIT=SYSALLDA,DISP=SHR\n")
    j.write("//SYSIN    DD *\n")
    j.write("  RFMT DDNAME(DASD1) RVTOC VERIFY("+upzosVol+")\n")
    j.write("/*\n")
    if sshSub == 'y':
        j.write("//S2 EXEC PGM=IEBGENER\n")
        j.write("//SYSPRINT DD SYSOUT=*\n")
        j.write("//SYSIN DD DUMMY\n")
        j.write("//SYSUT1 DD DSN=&&SYSPRT,DISP=OLD,\n")
        j.write("//       LRECL=125,BLKSIZE=629,RECFM=VBA\n")
        j.write("//SYSUT2 DD PATHDISP=(KEEP,KEEP),\n")
        j.write("//  PATHOPTS=(OWRONLY),\n")
        j.write("//  PATH='"+zdtJFile+"'\n")
    j.close()
    
    if sshSub != 'y':    
        prCyan("ICKDSF JCL File "+ickFile+" written to awsrdr directory: "+devRdrDir)
        prCyan("If Devmap is configured to use this directory for the awsrdr Stanza then JES2 should process this thru RDR(1) device")
        prCyan("If z/OS is currently down, this job will be executed automatically next time z/OS successfully Starts")
        prCyan("Waiting up to 40 seconds for JCL Execution to complete")
    else:
        prCyan("ICKDSF JCL File will be submitted via SSH. JCL Written to /tmp directory as: "+ickFile)
        try:
            subCmd = "submit '"+jclFile+"'"
            # Make the Pipe for sending output
            subprocess.run(["ssh", inUid+"@"+zosIp, "mkfifo -m 755 "+zdtJFile])
            # Transfer the JCL fiel over to z/OS 
            subprocess.run(["scp", jclFile, inUid+"@"+zosIp+":"+jclFile])
            # Submit the JCL
            subprocess.run(["ssh", inUid+"@"+zosIp, subCmd])
            # JCL will write to a pipe .. so we have to initiate a read 
            prCyan("Waiting up to 40 seconds for JCL Execution to complete")
            catCmd = str("cat "+zdtJFile)
            # Open output file so we can obtain pipe read directly to file
            fjF = open(zdtJFile, 'w')
            # Initiate Pipe read
            subprocess.run(["ssh", inUid+"@"+zosIp, catCmd],timeout=20,check=True,stdout=fjF)
            fjF.close()
        except Exception as e:
            print(e)
            print(OSError)
            print(sys.exc_info()[0])
            
    # Lets wait for the output from the ICKDSF Job so we can verify if REFVTOC was successful
    cl = 0
    fndOut = 'n'
    if (zdtPRT == 'y' or sshSub == 'y') and zosStat == 'up':
        while cl < 10:
            if os.stat(zdtJFile).st_size==0:
                cl += 1
                time.sleep(4)
            else:
                fndOut = 'y'
                prCyan("Finished Waiting, Output received and verifying")
                time.sleep(2)
                if sshSub != 'y':
                    try:
                        if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
                            subprocess.run(["awsmount", "00E", "-u"])
                        else:
                            subprocess.call(["awsmount", "00E", "-u"])
                    except:
                        pass
                break
    if zosStat == 'up' and sshSub == 'y':
        prCyan("Checking Job Output")
    if fndOut == 'n':
        prRed("Cannot retrieve output from ICKDSF REFVTOC. Please verify JOB ZDTRVTOC Manually")



# Obtain Jes2 Output from zPDT awsprt device or from PIPE via SSH 
def checkIckOut(expVol):
    try:
        volFnd = 'n'
        if sshSub == 'y':
            prCyan("Attempting to retrieve ICKDSF JCL output for verification")
            
        jout = open(zdtJFile, "r")
        for lines in jout:
            if 'RVTOC VERIFY('+expVol+')' in lines:
                volFnd = 'y'
            if 'ICK00001I FUNCTION COMPLETED, HIGHEST CONDITION CODE WAS 0' in lines and volFnd == 'y':
                prCyan("ICKDSF REFVTOC Successful !!")
                volFnd = 'v'
        if volFnd == 'y':
            prRed("ICKDSF REFVTOC was submitted successfully, however could not be verified or failed. Check output: "+zdtJFile)
        if volFnd == 'n':    
            prRed("ICKDSF REFVTOC was NOT submitted or output not found. Check ZDTRVTOC job completed on z/OS")
    except Exception as e:
        prRed("Error opening/reading output file, cannot verify ICKDSF REFVTOC status")
        print(e)
        print(OSError)
        print(sys.exc_info()[0])




# Arguments, Arguments, Arguments .. I do loath confrontation, can't everyone just get along. 
def readArgs():
    if 'zdtVresize' in sys.argv[0]:
        pfunc = 'zdtVresize'
        arglist = ['-i','-s','-d','-v','-m','-u','--help','-ssh','-ipaddr','-port']
    elif 'zdtVcreate' in sys.argv[0]:
        pfunc = 'zdtVcreate'
        arglist = ['-s','-v','-d','-m','-nodmap','-sms','--help']
    elif 'zdtpdsu' in sys.argv[0]:
        pfunc = 'zdtpdsu'
        arglist = ['-d','-v','-p','-q','-r','-x','--help']
    elif 'stopZos' in sys.argv[0]:
        pfunc = 'stopZos'
        arglist = ['-c','-z','-t','-awsstop','-noverify','--help']
    else:
        pfunc = 'zdtmsg'
        arglist = ['-w','--help']
    arg_len = len(sys.argv)
    if arg_len < 2 and 'stopZos' not in sys.argv[0]:
        printHelp()
        sys.exit()
    size_list = ['1','3','9','27','54']
    global stopTime, shutCmd, endTask, progPath, subJcl, newSize, volSer, smsFlag, inVol, autoMnt, inUid, volDir, upDmap, slpTime, sshSub, zosIp, awsstop, noverify, pdsName, memName, searchStr, replStr
    progPath = os.path.realpath(__file__).strip('zdtPyApi.py')
    progPath = os.path.realpath(__file__).strip('zdtPyApi.pyc')
    try:
        x = 0
        arg_len -= 1
        slpTime = 2
        smsFlag = ''
        subJcl = ''
        volSer = ''
        inVol = ''
        autoMnt = 'y'
        stopTime = 480
        shutCmd = 'null'
        pdsName = ''
        memName = ''
        searchStr = ''
        replStr = 'null'
        awsstop = 'no'
        noverify = 'N'
        endTask = 'JES2'
        upDmap = 'y'
        newSize = '1'
        inUid = 'IBMUSER'
        sshSub = ''
        zosIp = '10.1.1.2'
        zosSSHPort = 22
        #volDir = '/home/ibmsys1/zdt/volumes/'
        volDir = os.getcwd()+'/'
        
        while x < arg_len:
            x += 1
            if sys.argv[x] not in arglist:
                if 'stopZos' in sys.argv[0] and x == 0:
                    pass
                elif 'zdtmsg' in sys.argv[0] and x == 1:
                    pass
                else:
                    prRed("Invalid Arg passed")
                    printHelp()
                    sys.exit()
            if sys.argv[1] == '--help':
                printHelp()
                sys.exit()
            elif sys.argv[x] == '-c':
                shutCmd = sys.argv[x+1]
                x += 1
            elif sys.argv[x] == '-z':
                endTask = sys.argv[x+1].upper()
                x += 1
            elif sys.argv[x] == '-t':
                stopTime = int(sys.argv[x+1])
                x += 1
            elif sys.argv[x] == '-s':
                newSize = sys.argv[x+1]
                x += 1
                if newSize not in size_list:
                    raise ValueError('New volume size specified must be 1, 3, 9, 27 or 54')

            elif sys.argv[x] == '-noverify':
                noverify = 'Y'
            elif sys.argv[x] == '-awsstop':
                awsstop = 'Y'
            elif sys.argv[x] == '-sms':
                smsFlag = 'y'
            elif sys.argv[x] == '-d':
                volDir = sys.argv[x+1]
                x += 1
                if volDir.endswith('/'):
                    pass
                else:
                    volDir = volDir+'/'
            elif sys.argv[x] == '-r':
                searchStr = sys.argv[x+1]
                x += 1
            elif sys.argv[x] == '-x':
                replStr = sys.argv[x+1]
                x += 1
            elif sys.argv[x] == '-q':
                memName = sys.argv[x+1]
                x += 1
            elif sys.argv[x] == '-p':
                pdsName = sys.argv[x+1]
                x += 1
            elif sys.argv[x] == '-u':
                inUid = sys.argv[x+1]
                x += 1
            elif sys.argv[x] == '-w':
                slpTime = float(sys.argv[x+1])
                x += 1
            elif sys.argv[x] == '-m':
                autoMnt = 'n'
            elif sys.argv[x] == '-nodmap':
                upDmap = 'n'
            elif sys.argv[x] == '-i':
                inVol = sys.argv[x+1]
                x += 1
            elif sys.argv[x] == '-ssh':
                if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] <= 3):
                    raise ValueError("-ssh is only support when using Python 3.3 or higher")
                else:
                    sshSub = 'y'
            elif sys.argv[x] == '-ipaddr':
                zosIp = sys.argv[x+1]
                x += 1
            elif sys.argv[x] == '-port':
                zosSSHPort = int(sys.argv[x+1])
                x += 1
            elif sys.argv[x] == '-v':
                volSer = sys.argv[x+1]
                x += 1
                volLen = len(volSer)
                if volLen != 6:
                    prCyan("If volume name contains a $, place volume in single quotes")
                    raise ValueError('Volume Length Invalid. Must be length = 6 but found only to be length = '+str(volLen))
                valVol = re.match(r"^[A-Z0-9@#$']",volSer)
                if valVol == None:
                    prCyan("If volume name contains a $, place volume in single quotes")
                    raise ValueError('Volume contains invalid characters/symbols. May contain only 0-9, A-Z, @,#,or $') 
                    
        #if not os.path.exists(volDir) and pfunc != 'zdtmsg':
        if not os.path.exists(volDir+inVol) and pfunc != 'zdtmsg' and pfunc != 'zdtVcreate':
            raise ValueError('Volume not found in current working directory or directory specified, switch to correct directory or use appropriate -d option')       
        if inVol == '' and pfunc == 'resize':
            raise ValueError('Required Input Disk File parameter missing .. -i xxxxxxx')        
        if volSer == '' and pfunc == 'create':
            raise ValueError('Required Volume parameter missing .. -v xxxxxxx')       
        if sshSub == 'y':
            try:
                sTest = socket.socket()
                sTest.settimeout(10)
                sTest.connect((zosIp, zosSSHPort))
            except Exception as socke:
                print("Error connecting to ssh Port: "+str(zosSSHPort)+" Cannot continue with -ssh option")  
                print("Verify SSH is active on z/OS and you are specifying the correct port. Use -port option is necessary")
                print(OSError)
                print(socke)
                print(sys.exc_info()[0])
                sTest.close()
                sys.exit()
            finally:
                sTest.close()
    except SystemExit:
        sys.exit()
    except ValueError as ve:
        prRed("Error:")
        print( ve )
        sys.exit()
    except:
        print( "Exception: Argument Error")
        print(OSError)
        print(sys.exc_info()[0])
        sys.exit()


def getIplInfo():
    global shutCmd
    sendOprMsg('D IPLINFO', curLogFile, 1, 't')
    if "USED LOADAU IN SYS1.IPLPARM" in trapMsg:
        shutCmd = '%NETV SHUTSYS'
    elif "USED LOADNZ IN SYS1.IPLPARM" in trapMsg:
        shutCmd = '%NETV SHUTSYS'
    elif "USED LOADNV IN SYS1.IPLPARM" in trapMsg:
        shutCmd = '%NETV SHUTSYS'
    elif "USED LOADCS IN SYS1.IPLPARM" in trapMsg:
        shutCmd = 'S SHUTCS'
    elif "USED LOADAL IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUTALL'
    elif "USED LOADDB IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUTDB'
    elif "USED LOADCI IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUTCI'
    elif "USED LOADIM IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUTIM'
    elif "USED LOADIZ IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUTIZ'
    elif "USED LOADWA IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUTWA'
    elif "USED LOADDC IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUTDC'
    elif "USED LOADDW IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUTALL'
    elif "USED LOADWS IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUTCS'
    elif "USED LOAD00 IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUT00'
    elif "USED LOADZE IN SYS1.IPLPARM" in trapMsg:  
        shutCmd = 'S SHUTZE'
      



#Make CKD File for zdtVcreate. Ensure you are not trying to create something that already exists. 
def makeCkdVol(volSer, newSize, progPath):
    if os.path.exists(volDir+volSer):
                prRed("Severe ERROR: File "+volDir+volSer+" Already exists.. program aborting")
                sys.exit()
    else:
            try:
                subprocess.call(["alcckd", "-d", "3390-"+newSize, volDir+volSer])
                subprocess.call(["dd", "if="+progPath+"mod"+newSize+"stub", "of="+volDir+volSer, "bs=16M", "conv=notrunc", "status=progress"])
            except:
                print("Error creating or updating new CKD File: "+volDir+volSer)
                sys.exit()



def pdsUfile(volDir, volSer, pdsName, memName, searchStr, replStr):
    lastrc = 0
    pdsUstr=str(pdsName+"/"+memName+" /tmp/"+memName+" --extract")
    try:
        if os.path.exists("/tmp/"+memName):
            subprocess.run(["rm", "/tmp/"+memName])
        if memName == '' or pdsName == '' or volSer == '':
            raise ValueError("Invalid Parms. Member name, PDS name or volume not specfied. Check parms")
        if os.path.exists(volDir+volSer):
            pdsExtr = subprocess.run(["pdsUtil", volDir+volSer, pdsName+"/"+memName, "/tmp/"+memName, "--extract"],capture_output=True)
            if pdsExtr.stderr != b'':
                print(pdsExtr.stderr)
                print("Return Code: "+str(pdsExtr.returncode)) #typically RC 40 (no member) or 20 (no pds) here 
                sys.exit(pdsExtr.returncode)
                #raise ValueError(pdsExtr.stderr)
            else:
                subprocess.run(["cp", "/tmp/"+memName, "/tmp/"+memName+"_original"],stderr=None,stdout=None,capture_output=False)
        else:
            print("Volume not found in directory, ensure you specify -d to point to volume directory or run command from that directory")
            lastrc = 41
            print("Return Code: "+str(lastrc))
            sys.exit(lastrc) #raise ValueError("Volume not found")
    except subprocess.CalledProcessError as pdsUerr:
        print("Error extracting member "+memName+" from PDS "+pdsName+" on volume "+volDir+volSer)
        print(pdsUerr.output)
        lastrc = 42
        print("Return Code: "+str(lastrc))
        sys.exit(lastrc)
    if os.path.exists("/tmp/"+memName):
        infile = "/tmp/"+memName
        rdFile = open(infile, 'r')
        foundStr = ''
        strFnd = 0
        for line in rdFile:
            if searchStr in line:
                print("Match Found "+line)
                foundStr = 'yes'
                strFnd += 1
                nxl = ''
                metas = ['.', '^', '$', '&', '*', '+', '?', '{', '}', '[', ']', '\\', '|', '(', ')']
                if replStr != 'null':
                    for xl in replStr:
                        if xl in metas:
                            nxl = (nxl+"\\"+xl)
                        else:
                            nxl = nxl+xl
        rdFile.close()
        if foundStr == 'yes' and replStr != 'null':
            try:
                subprocess.run(["sed", "-i", "s/"+searchStr+"/"+nxl+"/", "/tmp/"+memName])
                pdsOlay = subprocess.run(["pdsUtil", volDir+volSer, pdsName+"/"+memName, "/tmp/"+memName, "--overlay"],capture_output=True)
                #print(pdsOlay.stderr)
                if pdsOlay.stderr != b'':
                    print(pdsOlay.stderr)
                    print("Return Code: "+str(pdsOlay.returncode))
                    sys.exit(pdsOlay.returncode) #raise ValueError(pdsOlay.stderr)
                else:
                    print ("String "+searchStr+" replaced with "+replStr)
                    print("Return Code: "+str(pdsOlay.returncode))
            except subprocess.CalledProcessError as pdsUerr2:
                print("Error during overlay for "+memName+" from PDS "+pdsName+" on volume "+volDir+volSer)
                print(pdsUerr2.output)
                lastrc = 0
        elif foundStr == '' and replStr != 'null':
            print("Search string "+searchStr+" not found in PDS member.")
            print("No updates/replacements performed")
            lastrc = 13
        elif foundStr == 'yes' and replStr == 'null':
            if strFnd > 1:
                prRed("Warning .. multiple lines found matching string: "+searchStr)
            print("Search String was found: "+str(strFnd)+" Times.") 
            print("Replacement String was not specified so no updates/replacements performed.")
            lastrc = 14
        elif foundStr == '':
            print("Search String was not found in specified member")
            lastrc = 15
    else:
        print("Member extraction output file not found.. likely error extracting member from PDS or member not found.")
        lastrc = 16
    sys.exit(lastrc)


# Check if zPDT Emulator is running. If it is not then this isn't a failure but some automagic turns to manual labor. 
def checkZpdt():
    global zdtStat, zosStat, zdtConf, zdtRDR, zdtPRT
    zdtConf = ''
    zdtRDR = ''
    zdtPRT = ''
    zosStat = 'down'
    try:
        zdt_stat = subprocess.check_output("awsstat")
        zdtStat = 'up'
        for line in zdt_stat.splitlines():
            if b'Config file' in line: 
                zdtConf = line.split()[2]
                zdtConf = zdtConf.strip(b',')
            if b'AWSRDR' in line:
                zdtRDR = 'y'
            if b'AWSPRT' in line:
                zdtPRT = 'y'
    except subprocess.CalledProcessError:
        prCyan('Warning, zPDT not started or an error was encountered checking zPDT status via awsstat')
        zdtStat = 'down'
    if zdtStat == 'up':
        try:
            zosChk = subprocess.check_output(["query", "0"])
            for line in zosChk.splitlines():
                if b"Running" in line:
                    zosStat = 'up'
        except subprocess.CalledProcessError as zose:
            print(zose.output)
            zosStat = 'down'
    else:
        zosStat = 'down'




# find out if there are free devices in devmap we can mount new files to. 
def findFreeDev():
    #Obtain list of AWSCKD Devices.
    global freeDevList
    freeDevList = [] 
    zdt_Devlist = subprocess.check_output("awsstat")
    for line in zdt_Devlist.splitlines():
        devno = line.split()[0]
        if line.split()[2] == b'AWSCKD':
            try:
                subprocess.check_output(["awsmount", devno, "-q"])
            except subprocess.CalledProcessError as zck:
                if b'No file mounted' in zck.output:
                    freeDevList.append(devno)




# Resizing Function
def resizeVol(wrtHxSize, ofile):
        try:
                nwrtHxSize = wrtHxSize
                f = open(ofile, "r+b")
                f.seek(18,0)
                f.write(nwrtHxSize)
                f.seek(22,0)
                f.write(nwrtHxSize)
                f.close()
        except Exception as ex:
                print(ex)
                print("Error updating Disk file with enlarged size.. aborting")
                sys.exit()



# get New Size values for writing device file
def getSizes(modType):
    global newHxSize, compSize
    if modType == '1':
        pass
    if modType == '2':
        newHxSize = b'\xb2\x08\x00\x00'
        compSize = 1897620992
    elif modType == '3':
        newHxSize = b'\x0b\x0d\x00\x00'
        compSize = 2846431232
    elif modType == '9':
        newHxSize = b'\x21\x27\x00\x00'
        compSize = 8539292672
    elif modType == '27':
        newHxSize = b'\x63\x75\x00\x00'
        compSize = 25617876992
    elif modType == '54':
        newHxSize = b'\xc6\xea\x00\x00'
        compSize = 51235753472
    else:
        # We should never get into here since we validate modType during readArgs()
        prRed("Invalid 3390 Mod Value passed")
        raise ValueError('Invalid 3390 Model Value Specified: '+modType)




# Update Devmap File
def updateDevmap(device, conFile, diskDir, diskFile):
    try:
        newFile = conFile.decode()+"_new"
        bkFile = conFile.decode()+"_orig"
        n = open(newFile, "w")
        c = open(conFile, "r")
        for line in c:
            if device.upper().decode() in line or device.lower().decode() in line:
                newLine = "device "+device.decode()+" 3390 2107 "+diskDir+diskFile+'\n'
                n.write(newLine)
            else:
                n.write(line)
        c.close()
        n.close()
        subprocess.call(["mv", conFile, bkFile]) 
        subprocess.call(["mv", newFile, conFile])
        prCyan("Devmap Updated!. Note: Original Devmap file retained as: "+conFile.decode()+"_orig")
    except:
        print(OSError)
        print(sys.exc_info())
        print("Error updating Devmap")




# get some Info from Devmap
def findDmInfo(loggedUser, zdtConf):
    global curLogFile, devRdrDir, prtDir
    curLogFile = ''
    devRdrDir = ''
    c = open(zdtConf, "r")
    for line in c:
        if 'oprmsg_file' in line and not line.startswith('#'):
            curLogFile = line.split()[1]
        if '2540' in line:
            devRdrDir = line.split()[4]
            devRdrDir = devRdrDir.strip('*')
        if ( '00E' in line or '00e' in line ) and '1403' in line:
            prtDir = line.split()[4]
            if prtDir.endswith('/'):
                pass
            else:
                prtDir = prtDir+'/'

    if curLogFile == '':
        try:
            if os.path.exists('/home/'+loggedUser+'/z1090/logs'): 
                consLogs = subprocess.check_output(["ls", "-lt", "/home/"+loggedUser+"/z1090/logs/"])
                for line in consLogs.splitlines():
                    if b'log_console' in line:
                        for words in line.split():
                            if b'log_console' in words:
                                curLogFile = b'/home/'+loggedUser.encode()+b'/z1090/logs/'+words
                        break
                    
            else:
                prRed("Cannot find current log directory")
                raise

        except:
            print(OSError)
            print(sys.exc_info())




# send commands to zPDT and retrieve responses
def sendOprMsg(oprStr, logFile, slpTime, prtOpt):
    global trapMsg
    nowTme = strftime("%H:%M:%S",gmtime())
    conOn = 'v cn(*),act'
    conOff = 'v cn(*),deact'
    subprocess.call(["oprmsg", conOn],stderr=None,stdout=None)
    time.sleep(1)
    lf = open(logFile, "a")
    lf.write("zdtmsg-"+nowTme+"\n")
    lf.write("zdtmsg-"+oprStr+"\n")
    lf.close()
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
        subprocess.run(["oprmsg", oprStr])
    else:
        subprocess.call(["oprmsg", oprStr])
    time.sleep(2)
    prFlag1 = 'n'
    prFlag2 = 'n'
    trapMsg = ''
    if prtOpt == 'y' or prtOpt == 't':
        oprmsgs = subprocess.check_output(["tail", "-n", "500", logFile])
        for lines in oprmsgs.splitlines():
            if b'zdtmsg-'+nowTme.encode() in lines: 
                prFlag1 = 'y'
            if oprStr.encode() in lines and prFlag1 == 'y' :
                prFlag2 = 'y'
            if prFlag2 == 'y':
                if b'IEE763I' in lines or b'IEC816I' in lines or b'zdtmsg-' in lines:
                    pass
                else:
                    if prtOpt == 'y':
                        print(lines.decode())
                    else:
                        trapMsg += lines.decode()
        if slpTime > 3 and sys.version_info[0] >= 3 and sys.version_info[1] >= 3:
                    try:
                            subprocess.run(["tail", "-f", "-n", "0", logFile], timeout=slpTime)
                    except subprocess.TimeoutExpired:
                            pass
                    except KeyboardInterrupt:
                            pass
    #if noConOff == 'no':
    #    if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
    #       subprocess.run(["oprmsg", conOff])
    #    else:
    #        subprocess.call(["oprmsg", conOff])
    if prtOpt == 't':
        return trapMsg
