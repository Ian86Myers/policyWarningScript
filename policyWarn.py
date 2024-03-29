#!/usr/bin/env /filepath/to/python/goes/here

import argparse
import collections
import pandas as pd
import pandasql as ps
import pymysql as sql
import sys

from collections import namedtuple
from datetime import datetime
from pandas import option_context
from subprocess import Popen, PIPE

### Policy 1,2,3 time limit on graphs ######Three days
policyOneLimit= 3
policyTwoWarningTime = '408'
policyTwoLimit= '480'
policyThreeWarning = '48'
policyThreeLimit = '120'

### SQL Test DB 
#db = "IANgraph"
db = "graph"

### parse input parms
parser = argparse.ArgumentParser(description='Policy Warning Report')
parser.add_argument('-email'  , '-e', '--email'  , dest='email', action='store', required=True, help='Enter email to generate a report on active graphs.')
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-mail','-m','--mail', dest='mail', action='store_true', help='Send report to your e-mail.')
group.add_argument('-stdout', '-s', '--stdout', dest='stdout', action='store_false', help='Print report to stdout.')
args = parser.parse_args()
email = args.email
stdout = args.stdout
send_mail = args.mail

### read database password
f = open("/filepath_to_my_passwd/u/imyers/.../","r")
dbpwd = f.read().strip()

### make connection to parent database
def db_connect(user, passwd):
  return sql.connect(host='...ibm.com', user=user, passwd=passwd , db='graph')
db9 = db_connect('imyers', dbpwd)
cursor = db9.cursor()
### Set options on Pandas DataFrame
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'left')
pd.set_option('display.precision', 3)
def make_lalign_formatter(dfGetPolicy1Indx, cols=None):
    """
    Construct formatter dict to left-align columns.

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        The DataFrame to format
    cols : None or iterable of strings, optional
        The columns of df to left-align. The default, cols=None, will
        left-align all the columns of dtype object

    Returns
    -------
    dict
        Formatter dictionary

    """
    if cols is None:
       cols = dfGetPolicy1Indx.columns[dfGetPolicy1Indx.dtypes == 'object'] 

    return {col: f'{{:<{dfGetPolicy1Indx[col].str.len().max()}s}}'.format for col in cols}

### Policy 1 - select group by email, cell, and mode having a count of three or more. Input email into WHERE clause from argparse.
# Order by oldest indx then cell,mode alphabetical.
cmd = "SELECT COUNT(*) as cnt, email, cell, mode FROM "+db+".registry \
 WHERE http IS NOT NULL AND email = "+ "'" + email + "'" +"  AND email NOT LIKE 'protected%' AND email NOT LIKE 'cohenm0%' AND email NOT LIKE 'lich@%'\
 GROUP BY email, cell , mode HAVING (cnt >=3) ORDER BY cnt DESC, cell, mode ASC ; "

outer_tuple = namedtuple('processGroupBy', ['count', 'e_mail', 'cell', 'mode'] )

cursor.execute(cmd)
res = cursor.fetchall()
print("Policy 1 Check - 3 Versions of Cell/Mode Max - The following is a list of your active servers\n")
### return a table for each GROUP BY then get list of indices
for itm in res:
  inner_tuple = (outer_tuple(*itm))
  cmd = "SELECT cell,mode,indx,dt,run_name FROM  "+db+".registry r \
  WHERE http IS NOT NULL AND email = "+ "'" + str(inner_tuple.e_mail) + "'" +" \
  AND cell = "+ "'" + str(inner_tuple.cell) + "'" +" AND mode = "+ "'" + str(inner_tuple.mode) + "'" +" \
  GROUP BY cell, mode, dt ORDER BY cell,mode,dt ASC; " 
  dfGetPolicy1Indx = pd.read_sql(cmd, db9)
  indxList = dfGetPolicy1Indx['indx'].tolist()

# find indx items that match error condition, bring back each row
  for indx in indxList:
    dfHead = dfGetPolicy1Indx.head(inner_tuple.count-policyOneLimit)
# Check for warning condition bring back warning condition table
  if inner_tuple.count <= policyOneLimit:
      with option_context('display.max_colwidth', 400):
        print("\tWarning: Maximum number of servers reached for"
            ,inner_tuple.cell,inner_tuple.mode,"\n")
        # Left align all columns
        print(dfGetPolicy1Indx[['indx','dt','run_name']].to_string(formatters=make_lalign_formatter(dfGetPolicy1Indx), 
                   index=False, 
                   justify='left'),"\n")
# if it exists, print "Error" condition with table
  if not dfHead.empty:
      with option_context('display.max_colwidth', 400):
          print("\tError: Exceeded Maximum number of servers for"
                   ,inner_tuple.cell,inner_tuple.mode,"\n")
            # Left align all columns
          print(dfGetPolicy1Indx[['indx','dt','run_name']].to_string(formatters=make_lalign_formatter(dfGetPolicy1Indx), 
                   index=False,
                   justify='left'),"\n")

### Policy 2

# Return most recent date per indx in registry WHERE http IS NOT NULL
# Get indx for the specified email into a list
cmd="SELECT indx, Max(dt)  FROM "+db+".registry WHERE http IS NOT NULL \
AND email = "+ "'" + email + "'" +" GROUP BY indx ORDER BY dt DESC ;" 
dfGetPolicy2Indx = pd.read_sql(cmd,db9)
policy2Indx = dfGetPolicy2Indx['indx'].tolist()
print("Policy 2 Check - Max Inactive Server\n")

# For each item in specified list calculate elapsed max(dt) and capture in a variable from graph.history indx
# Inside the same loop bring back a slice of data from conditionals, policyTwoLimit and policyTwoWarning based on graph.registry indices
# for each mode,cell in the dataframe set to_string to be output in warning string w/out index.
# calcuate hours remaining / days remaining
for indx in policy2Indx:
  # Error warning conditional for policyTwoLimit
  cmd="SELECT indx, MAX(dt), (unix_timestamp(now()) - unix_timestamp(MAX(dt)))/3600 as elapsed \
  FROM "+db+".history WHERE indx=" "'"+ str(indx) + "'" +" \
  HAVING elapsed >= "+ "'" + policyTwoLimit + "'" +"  ;"
  dfPolicy2Limit = pd.read_sql(cmd, db9)
  cmd="SELECT indx, mode, cell \
      FROM "+db+".registry \
      WHERE http IS NOT NULL AND indx=" "'"+ str(indx) + "'" +"; "
  dfGetMetaData2 = pd.read_sql(cmd,db9)
  mode = dfGetMetaData2['mode'].to_string(index=False)
  cell = dfGetMetaData2['cell'].to_string(index=False)
  elapsed2= dfPolicy2Limit['elapsed'].to_string(index=False)
  if not dfPolicy2Limit.empty:
    print("\tError: Exceeded max inactive time for graph ID:" 
          ,indx,cell,mode,"-- spin down imminent.\n")
    
for i in policy2Indx:
  # Warning conditional for policyTwoWarning, 2nd for loop breaks DRY principle but needed for print order.
  cmd="SELECT indx, MAX(dt), (unix_timestamp(now()) - unix_timestamp(MAX(dt)))/3600 as elapsed \
      FROM "+db+".history \
      WHERE indx=" "'"+ str(i) + "'" +" \
      HAVING elapsed >= "+ "'" + policyTwoWarningTime + "'" +" \
      AND elapsed < "+ "'" + policyTwoLimit + "'" +" ;"
  dfPolicy2Warn = pd.read_sql(cmd, db9)
  elapsed22 = dfPolicy2Warn['elapsed'].to_string(index=False)
  cmd="SELECT indx, mode, cell \
      FROM "+db+".registry \
      WHERE http IS NOT NULL AND indx=" "'"+ str(i) + "'" +"; "
  dfGetMetaData = pd.read_sql(cmd,db9)
  mode = dfGetMetaData['mode'].to_string(index=False)
  cell = dfGetMetaData['cell'].to_string(index=False)
  if not dfPolicy2Warn.empty:
    hoursRemaining = round((float(policyTwoLimit)-round(float(elapsed22),2)),2)
    daysRemaining = round(hoursRemaining/24,2)
    
    print("\tWarning: Approaching max inactive time for graph ID:"
          ,i,cell,mode,"--",daysRemaining,"days left to spin down.")
    print("\tHours remaining: ",hoursRemaining,"\n")

    ### Policy 3
# Find active graphs — Query registry on email and indx data & bring back a 
# list in indices WHERE http IS  NOT NULL AND label = 'timing';
cmd="SELECT indx FROM "+db+".registry \
    WHERE http IS NOT NULL AND label = 'timing' AND email ="+ "'" + email + "'" +" ;"
dfGetIngestedIndx = pd.read_sql(cmd,db9)
policy3IndxList = dfGetIngestedIndx['indx'].tolist()
print("Policy 3 Check - Max(",int(policyThreeLimit)/24,"days or",policyThreeLimit,"hours ) inactive server for unreferenced server")

# Check if activity is equal to 1 rows --COUNT(*) then GROUP BY indx HAVING indx = 1, then turn results into list
for indx in policy3IndxList:
    cmd="SELECT COUNT(*) as cnt, indx \
        FROM "+db+".history \
        WHERE indx ="+ "'" + str(indx) + "'" +"  \
        GROUP BY indx HAVING cnt = 1 ; "
    dfActiveIndxCnt = pd.read_sql(cmd,db9)
    
    # If indx exists return a list, look at the dt for proximity to policy limit.
    if not dfActiveIndxCnt.empty:
        activeIndxList = dfActiveIndxCnt['indx'].tolist()

        #  Loop through list, calculates elapsed time & Returns Policy3Warning conditional
        for innerIndx in activeIndxList:
            cmd="SELECT dt,indx,MAX(dt),\
                (unix_timestamp(now()) - unix_timestamp(MAX(dt)))/3600 as elapsed \
                FROM "+db+".registry \
                WHERE indx ="+ "'" + str(innerIndx) + "'" +"   \
                HAVING elapsed >= "+ "'" + policyThreeWarning + "'" +" ;"
            dfResults3 = pd.read_sql(cmd,db9)
            #elapsed3 = dfResults3['elapsed'].to_string(index=False)
            dfResults3['elapsed'] = dfResults3['elapsed'].astype(float)
            elapsed3 = dfResults3['elapsed'].to_string(index=False)
            if not dfResults3.empty:
              elapsed3 = round(float(elapsed3),2)

        # if dfResults is not empty, return time calculations
        if not dfResults3.empty:
            hoursRemaining = round((float(policyThreeLimit) \
                                    -round(float(elapsed3),2)),2)
            daysRemaining = round(hoursRemaining/24,2)

        # Return elapsed time and indx between both conditionals
        cmd="SELECT indx,MAX(dt),\
            (unix_timestamp(now()) - unix_timestamp(MAX(dt)))/3600 as elapsed \
            FROM "+db+".registry \
            WHERE indx ="+ "'" + str(innerIndx) + "'" +" \
            HAVING elapsed >= "+ "'" + policyThreeWarning + "'" +" \
            AND elapsed <= "+ "'" + policyThreeLimit + "'" +" ;"
        dfWarning3 = pd.read_sql(cmd, db9)
        elapsedWarning = dfWarning3.to_string(index=False)
        
        if not dfWarning3.empty:
            print("\tWarning graph ID:",innerIndx,", has",elapsed3,"hours inactive,",hoursRemaining,"hours until spin down.")
            
        # Return indx and Error message after Policy3Limit conditional
        cmd="SELECT indx, MAX(dt), \
            (unix_timestamp(now()) - unix_timestamp(MAX(dt)))/3600 as elapsed \
            FROM "+db+".registry WHERE indx ="+ "'" + str(innerIndx) + "'" +" \
            HAVING  elapsed > "+ "'" + policyThreeLimit + "'" +" ;"
        dfLimit3 = pd.read_sql(cmd,db9)
        elapsedLimit = dfLimit3.to_string(index=False)
        
        if not dfLimit3.empty:
            print("\tError graph ID:",innerIndx,"has",hoursRemaining,"hours remaining -- spin down imminent.")
            
        if dfResults3.empty:
            print("\tNo warnings to report on graph ID:",innerIndx)
