#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from requests.auth import HTTPBasicAuth
import json


# In[2]:


HOST = 'http://95.216.44.142/app/mgz/bpm'
AUTH = HTTPBasicAuth('???????', '???????')


# In[3]:


answer = requests.get(HOST + '/runtime/process-instances?size=99999', auth=AUTH)
data = json.loads(answer.text)


# In[4]:


def get_tasks(entityId, historic):
    params = {"processVariables":[{"name":"EntityIdVar",
                                   "value":entityId,
                                   "operation":"equals",
                                   "type":"string"}],
              "size":1000000,
              "includeProcessVariables":False}
    
    url = HOST + '/query/' + ('historic-task-instances' if historic else 'tasks')
    answer = requests.post(url, json=params, auth=AUTH)
    return json.loads(answer.text)['data']


# In[5]:


def get_processes(entityId, historic):
    params = {"variables":[{"name":"EntityIdVar",
                            "value":"b1923954-3123-4af8-9911-00e2d0bb0bc7",
                            "operation":"equals","type":"string"}],
              "size":1000000,
              "includeProcessVariables":False}

    url = HOST + '/query/' + ('historic-process-instances' if historic else 'process-instances')
    answer = requests.post(url, json=params, auth=AUTH)
    return json.loads(answer.text)['data']


# In[6]:


def delete_process_instance(id, historic):
    if historic:
        url = '/history/historic-process-instances/'
    else:
        url = '/runtime/process-instances/'
    answer = requests.delete(HOST + url + id, auth=AUTH)
    if not answer.ok:
        print(id, answer.text)


# In[7]:


def delete_by_project_hist(projectId, historic):
    processes = get_processes(projectId, historic)
    for p in processes:
        delete_process_instance(p['id'], historic)
    
    
def delete_by_project(projectId):
    delete_by_project_hist(projectId, False)
    delete_by_project_hist(projectId, True)


# In[8]:


projectId = "b1923954-3123-4af8-9911-00e2d0bb0bc7"
delete_by_project(projectId)


# tasks = get_tasks(projectId, True)
# len(tasks)

# assignee = set(list(map(lambda x: x['assignee'], tasks)))
# assignee
