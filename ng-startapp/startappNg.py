#!/usr/bin/python3
import os
import sys
import re
import argparse

IGNORE_TASK = ("Approve", "Dynamic", "SimpleApprove", )
VARIABLES = ("writable", "id", "required", "name", "variable")

processIdPattern = re.compile(r'<process id="(.*?)".*>', re.DOTALL)
tasksPattern = re.compile(r'<userTask (.*?)</userTask>', re.DOTALL)
taskNamePattern = re.compile(r'activiti:formKey="(.*?)"', re.DOTALL)
activitiPattern = re.compile(r'\s*<activiti:formProperty (.*?)>\s*</activiti:formProperty>\s*', re.DOTALL)

enumPattern = re.compile(r'\s*<activiti:value(.*?)>\s*</activiti:value\s*', re.DOTALL)

activitiFormPropertyPatterns = {
    "type": re.compile(r'\s*type="(.*?)"\s*', re.DOTALL),
    "id": re.compile(r'\s*id="(.*?)"\s*', re.DOTALL),
    "name": re.compile(r'\s*name="(.*?)"\s*', re.DOTALL),
    "variable": re.compile(r'\s*variable="(.*?)"\s*', re.DOTALL),
    "required": re.compile(r'\s*required="(.*?)"\s*', re.DOTALL),
    "writable": re.compile(r'\s*writable="(.*?)"\s*', re.DOTALL), 
}


def Enumtype(variable, nameVar, content):
    context = {"type" : "enum"}
    context["name"] = variable
    context["title"] = nameVar
    context["options"] = []

    vars_enum = enumPattern.findall(content)

    for s in vars_enum:
        value = activitiFormPropertyPatterns["id"].findall(s)[0]
        label = activitiFormPropertyPatterns["name"].findall(s)[0]
        context["options"].append({"label": label, "value": value})

    return context


#templates
template_ts = """import {Component, OnInit, ViewChild} from '@angular/core';
import { Observable } from 'rxjs';

@Component({
    selector: './%s',
    templateUrl: './%s',
    styleUrls: ['./%s']
})
export class %s implements OnInit {

    constructor() {
    
    }

    ngOnInit(){
    }
}"""

template_import = "import { %s } from './components/tasks/%s/%s/%s';\n"

template_doc = """
<projects-document-field #doc_MGZ_DOC_GEO
                   [project]="project"
                   [docType]="'MGZ_DOC_GEO'"
                   %s
                   [readOnly]="%s"
></projects-document-field>
"""

template_approval_list = """
import {ActivityService} from '../../../../services/activity.service';

//private activitiService: ActivityService,

approvalCycle: any;
approvalHistory: any;

  onLoaded() {
    this.activitiService.getFormData(this.task.id).subscribe(formData => {
      // Находим документ, который требуется согласовать. Он должен быть в парамтрах формы единственным документом
      const docProp = formData.formProperties.find(p => p.id.startsWith('doc_'));

      this.documentsService.getDocumentWrapper(docProp.value).subscribe(doc => {

        this.approvalCycle = angular.copy(doc.document.approval.approvalCycle);
        this.approvalHistory = angular.copy(doc.document.approvalHistory);

        this.fillBody(this.template, this.defaultBody);
        this.onLoadSuccess();

      });
    });
  }
"""

template_radio ="""
    <div class="form-group">
        <label class="col-lg-3 col-md-3 col-sm-3 control-label">Банковская гарантия</label>
        <div class="col-lg-7 col-md-8 col-sm-9">
            <table>
                <tr *ngFor="let opt of PurchaseRequisitionOptions">
                    <td style="width:30px">
                        <div class="i-checks">
                            <label class="m-t-xs our-fio-check">
                            <input cdp-icheck name="PurchaseRequisition" [(ngModel)]="PurchaseRequisition" type="radio" [value]="opt.value">
                            </label>
                        </div>
                    </td>
                    <td><span class="text-normal">{{ opt.title }}</span></td>
                </tr>
            </table>
            <br>
        </div>
    </div>
""" 

template_html = """<div class=""></div>
"""

template_rout = """
{
    name: '%s',
    url: '/%s',
    component: %s
},
"""

template_check = """
<div class="form-group">
    <label class="col-lg-3 col-md-3 col-sm-3 control-label">Необходимо дополнительное подтверждение от бухгалтерии</label>
    <div class="col-lg-1 col-md-2 col-sm-3">
        <input cdp-icheck type="checkbox" class="form-control text-left notrequire" [(ngModel)]="AdditionalConfirmation" name="AdditionalConfirmation"/>
        <br>
    </div>
</div>
"""

template_info = """
<div class="form-group">
    <label class="col-lg-3 col-md-3 col-sm-3 control-label">
        Исполнитель из МГГТ
    </label>
    <div class="col-lg-7 col-md-8 col-sm-9">
        <p>{{ formValues['performer'] }}</p>
    </div>
</div>
"""

template_date_and_numberMosEdo = """
<div class="form-group">
    <label class="col-lg-3 col-md-3 col-sm-3 control-label">Дата получения</label>
    <div class="col-lg-7 col-md-8 col-sm-9">
        <cdp-date-selector [(model)]="formValues['DateOfReceiving']" style="width:150px;" ></cdp-date-selector>
    </div>
</div>

<div class="form-group">
    <label class="col-lg-3 col-md-3 col-sm-3 control-label">Номер письма в МосЭДО<span class="our-mandatory">*</span></label>
    <div class="col-lg-7 col-md-8 col-sm-9">
      <input class="form-control bg-primary" name="NumberInMosEDO" [(ngModel)]="NumberInMosEDO" placeholder="Номер письма в МосЭДО"/>
    </div>
</div>
"""

table_approve = "<table-approval-list [project]=\"project\" [docType]="'MGZ_DOC_TermAgreeAgreeTerm'"></table-approval-list>"

template_card = "<project-card *ngIf=\"projectId\" [processId]=\"projectId\"></project-card>"
# <cdp-approval-list [model]="approvalCycle" [history]="approvalHistory.approvalCycle" *ngIf="loading === 'SUCCESS'"></cdp-approval-list>
# ng serve --proxy-config proxy.debug.json --host 192.168.2.184 --port 8080

"""
Структура работ
<div class="form-group">
    <div class="col-lg-12">
      <isr #isr *ngIf="dataForGant" [data]="dataForGant" [editor]="true"></isr>
    </div>
</div>
"""

ManageTemplateFiles = {
    "ts": lambda selector, html, css, component: template_ts%("projects-" + selector, html, css, component),
    "html": lambda selector, html, css, component: template_html,
}


def getVariables(activitiString):
    res = {}
    for var in VARIABLES:
        try:
            res[var] = re.findall(r'%s="(.*?)"'%var, activitiString, re.DOTALL)[0]
        except:
            res[var] = None
    return res


def create_nameSpace(name):
    new_name = ""
    delimeter = "-"
    title = False
    for i, ch in enumerate(name):
        if ch.istitle():
            if i == 0:
                new_name += ch.lower()
                continue
            try:
                if name[i + 1].istitle() and not title:
                    new_name += delimeter
                    title = True
            except:
                pass
            if not title:
                new_name += delimeter + ch.lower()
            else:
                new_name += ch
                try:
                    if name[i + 2].islower():
                        title = False
                except:
                    pass
            continue
        new_name += ch
        title = False
    return new_name


def createComponent(name_path):
    component = "component"
    exts = ("ts", "html", "css")
    result = []
    for ext in exts:
        result.append(".".join([name_path, component, ext]))
    return result


def createRouting(componentName, prefix = "mgzprojects", executionPath = "app.execution"):
    root_name = prefix + componentName.replace("Component", '')
    name = '.'.join([executionPath, root_name])
    return template_rout%(name, root_name, componentName)


def createImport(componentName, path, task, form):
    form = ".".join(form.split(".")[:-1])
    return template_import%(componentName, path, task, form)


def parseBpmn(file):
    procecc_name = None
    process_tasks = []

    try:
        with open(file, 'r', encoding = "utf8") as f:
            bpmn = f.read()

    except Exception as err:
        print("Ошибка чтения файла: ", err)
        sys.exit(1)

    processName = processIdPattern.findall(bpmn)

    if len(processName) > 0:
        procecc_name = processName[0].split("_")[1]

    tasks = tasksPattern.findall(bpmn)

    for task in tasks:
        task_name = taskNamePattern.findall(task)

        if len(task_name) > 0 and task_name[0] not in IGNORE_TASK:

            process_tasks.append(task_name[0])

    return (procecc_name, process_tasks)


def parseActivitiProperty(task):
    varuables = activitiPattern.findall(task)



def main(name_app = None, names_components = [], bpm=None, pathApp=None):
    postFix = "Component"

    if bpm:
        name_app, names_components = parseBpmn(bpm)

    else:
        if not name_app: 
            print("Введите название процесса!!!")
            sys.exit(1)

    name_pocess = create_nameSpace(name_app)

    imports_template = ""
    rout = ""

    if pathApp:
        name_path = os.path.join(pathApp, name_pocess)
    try:
        os.mkdir(name_path)
    except:
        pass
    for component in names_components:
        nameSpace = create_nameSpace(component)
        name_files = createComponent(nameSpace)
        path_app = os.path.join(name_path, nameSpace)

        try:
            os.mkdir(path_app)
        except:
            pass

        for file in name_files:
            with open(os.path.join(path_app, file), 'w') as f:
                ext = file.split('.')[-1]
                if ManageTemplateFiles.get(ext):
                    f.write(ManageTemplateFiles[ext](nameSpace, name_files[1], name_files[2], component + postFix))

        imports_template += createImport(component + postFix, name_pocess, nameSpace, name_files[0])
        rout += createRouting(component + postFix)
    print("Imports: \n")
    print(imports_template)
    print()
    print("routing: \n", rout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='--help')
    parser.add_argument('--path', type=str, default=os.getcwd(), required=False)
    parser.add_argument('--task', type=str, required=False)
    parser.add_argument('--components', type=str, required=False)
    parser.add_argument('--bpm', type=str, required=False)

    
    args = parser.parse_args()

    if args.bpm:
        main(None, [], args.bpm, args.path)

    else:
        main(args.task, args.components.split(","), args.bpm, args.path)
