/* REXX */ 
                                                                                                                  
  '/web/home/websrv/bin/cgiutils -status 200 -ct text/html -expires now' 
                                                                                                                  
  DB2_MAIN = 'DBCG' 
  DB2_LOC  = 'DALLASC' 
                                                                                                                  
  SAY "<HTML>" 
  SAY "<META HTTP-EQUIV='CACHE-CONTROL' CONTENT='NO-CACHE'>" 
  SAY "<META HTTP-EQUIV='PRAGMA' CONTENT='NO-CACHE'>" 
  SAY "<META HTTP-EQUIV='EXPIRES' CONTENT='0'>" 
  SAY "<BODY BGCOLOR='BLACK' TEXT='WHITE'>" 
  SAY "<hr>" 
  SAY "<br>" 
                                                                                                                  
  SQLFTCH = "SELECT LPARNAME,date(DATETIME) as DATE,TIME(DATETIME) as TIME,LBUSY from S390ADM.CPUUTIL WHERE ", 
        "DATE(DATETIME) >= CURRENT DATE ORDER BY DATETIME DESC" 
                                                                                                                  
  Address MVS "SUBCOM DSNREXX" 
                                                                                                                  
  IF RC THEN 
    S_RC = RXSUBCOM('ADD','DSNREXX','DSNREXX') 
                                                                                                                  
  Address DSNREXX "CONNECT "DB2_MAIN 
  Address DSNREXX "EXECSQL CONNECT TO "DB2_LOC 
  ADDRESS DSNREXX "EXECSQL DECLARE C2 CURSOR FOR S2" 
  ADDRESS DSNREXX "EXECSQL PREPARE S2 INTO :OUTSQLDA FROM :SQLFTCH" 
  ADDRESS DSNREXX "EXECSQL OPEN C2" 
xp = 0 
Do Until(SQLCODE <> 0) 
  ADDRESS DSNREXX "EXECSQL FETCH C2 USING DESCRIPTOR :OUTSQLDA" 
  If SQLCODE = 0 Then 
  DO 
    TitLine = '' 
    Line = '' 
    xp = xp + 1 
    Do I = 1 To OUTSQLDA.SQLD 
      Line = Line OUTSQLDA.I.SQLDATA 
    End I 
    outline.xp = Line 
  END 
END 
                                                                                 
say "<table cellpadding='3' border='0'>" 
say "<tr align='center'>" 
say "<th>CPC/Host</th>" 
say "<th>Date</th>" 
say "<th>Time</th>" 
say "<th>CPU Utilization </th>" 
say "</tr>" 
do lp2 = 1 to xp 
  parse var outline.lp2 CPCNAME DTE TME UTILV 
  parse var UTILV UTILV"."JUNK 
                                                                                 
  utilvstr = '' 
  do hp = 1 to utilv 
    utilvstr = utilvstr || '||' 
  end 
    utilvstr = utilvstr ||" "utilv"%" 
    if utilvstr = '' then utilvstr = ' 0% ' 
                                                                               
    say "<tr align='left'>" 
    say "<td align='left'>"CPCNAME"</td>" 
    say "<td align='left'>"DTE"</td>" 
    say "<td align='left'>"TME"</td>" 
    select 
    when UTILV > 89 then 
      colspec = 'red' 
    when UTILV > 79 then 
      colspec = 'darkorange' 
    when UTILV > 69 then 
      colspec = 'yellow' 
    otherwise 
      colspec = 'green' 
    end 
    say "<td align='left'><font color='"colspec"'>"utilvstr"</td></font>" 
    say "</tr>" 
  end 
  say "</table>" 
                                                                           
  SAY "</BODY></HTML>" 
  ADDRESS DSNREXX "EXECSQL CLOSE C2" 
  ADDRESS DSNREXX "DISCONNECT" 
                                                                               
EXIT 
