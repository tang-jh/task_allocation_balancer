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
    
#recursive function to select next minimum load value (2nd method)
def recursive_search(loads, taskname):
    subset = staff[(staff['staffload'] == loads[0]) & [taskname not in e for e in staff['assignedcat']]]
    if subset.empty:
        loads = loads[1:]
        return recursive_search(loads, taskname)
    else:
        return subset.iloc[0, 0]

num_task = 0 #counter to check if task loop is completed
#Round robin allocation selecting staff with current min load.
for t in range(len(tasks.index)):
    curr_min = staff['staffload'].min()
    curr_idx = staff['staffload'].idxmin()
    if tasks.iloc[t, 1] not in staff.iloc[curr_idx, 4]:
        staff.iloc[curr_idx, 2] += tasks.iloc[t, 2]
        staff.iloc[curr_idx, 3].append(tasks.iloc[t, 0])
        staff.iloc[curr_idx, 4].append(tasks.iloc[t, 1])
        tasks.iloc[t, 3] = staff.iloc[curr_idx, 1]
        num_task += 1
    else:
        loads = staff['staffload'].unique()
        loads.sort()
        selected = staff[staff['staffid'] == recursive_search(loads, tasks.iloc[t, 1])].index.item()
        staff.iloc[selected, 2] += tasks.iloc[t, 2]
        staff.iloc[selected, 3].append(tasks.iloc[t, 0])
        staff.iloc[selected, 4].append(tasks.iloc[t, 1])
        tasks.iloc[t, 3] = staff.iloc[selected, 1]
        num_task += 1
        
if num_task != len(tasks):
    raise Exception('WARNING: Not all tasks have been assigned.')

end = timer()
print(end - start) #check runtime

excel = pd.ExcelWriter(r'../export/allocated_list.xlsx', date_format='yyyy-mm-dd')
staff.to_excel(excel, index=False, sheet_name='staff')
tasks.to_excel(excel, index=False, sheet_name='tasks')

excel.save()

