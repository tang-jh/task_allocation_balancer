import numpy as np
import pandas as pd
from timeit import default_timer as timer

start = timer()

#import and prepare staff list as a dataframe
stafflist = pd.read_csv(r'../resources/stafflist.csv', header=None)[0].unique() #load list of staff from csv
staff = pd.DataFrame(columns=['staffid', 'staffname', 'staffload', 'assignedtask']) #construct empty staff dataframe
staff['staffname'] = stafflist  #populate staff dataframe with staff names
staff['staffid'] = staff.index  #create dummy index for reference
staff['staffload'] = 0          #set initial staff load to zero
staff['assignedtask'] = np.empty((len(staff), 0)).tolist()  #initialize assignedtask as empty lists
staff['assignedcat'] = np.empty((len(staff), 0)).tolist()   #initialize assignedcat as empty lists
staff = staff.sample(frac=1).reset_index(drop=True)         #shuffle staff order

#import and prepare task list and sorting by task load in descending order
tasks = pd.read_csv(r'../resources/tasks.csv')
tasks.insert(0, 'taskid', tasks.index)
tasks['stafffk'] = ''
tasks['taskid'] = tasks.index
tasks = tasks.sort_values(by=['load'], ascending=False).reset_index(drop=True)

#Min staff required is at least equal to the largest number of staff needed for a single taskslot
min_staff = tasks['taskslot'].value_counts().max()
if len(staff) < min_staff:
    raise Exception('Minimum staff needed should at least be equal to the highest number of staff needed for a single taskslot ({})'.format(min_staff))
    exit()

#assign all staff with task highest load for 1st round
import random

totalLoad = 0
totalStaff = len(staff)

#allocate all staff with a task for first round
for i in range(len(staff.index)):
    staff.iloc[i, 2] = tasks.iloc[i, 2]
    staff.iloc[i, 3].append(tasks.iloc[i, 0])
    staff.iloc[i, 4].append(tasks.iloc[i, 1])
    tasks.iloc[i, 3] = staff.iloc[i, 1]
    totalLoad += tasks.iloc[i, 2]

meanLoad = totalLoad/totalStaff #track mean load of all staff. This is used as benchmark for subsequent assignments

new_tasks = tasks[tasks['stafffk'] == ''] #subset dataframe to hold remaining unassigned tasks

#Random allocation checking staff load against global mean load
for t in range(len(new_tasks.index)):
    taskid = new_tasks.iloc[t, 0]
    randPick = random.randint(0, len(staff.index)-1)
    while (staff.iloc[randPick, 2] > meanLoad) or (new_tasks.iloc[t, 1] in staff.iloc[randPick, 4]):
        randPick = random.randint(0, len(staff.index)-1)
    staff.iloc[randPick, 2] += new_tasks.iloc[t, 2]
    staff.iloc[randPick, 3].append(new_tasks.iloc[t, 0])
    staff.iloc[randPick, 4].append(new_tasks.iloc[t, 1])
    tasks['stafffk'][tasks['taskid'] == taskid] = staff.iloc[randPick, 1]
    totalLoad += tasks.iloc[t, 2]
    meanLoad = totalLoad/totalStaff

end = timer()
print(end - start) #check runtime

excel = pd.ExcelWriter(r'../export/allocated_list.xlsx', date_format='yyyy-mm-dd')
staff.to_excel(excel, index=False, sheet_name='staff')
tasks.to_excel(excel, index=False, sheet_name='tasks')

excel.save()