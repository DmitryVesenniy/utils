#!/usr/bin/python3

prefixes = {
	"Ведущий специалист": "FR_SSD", 
	"Начальник управления": "FR_HD", 
	"Заместитель начальника управления": "FR_DHD", 
	"Главный специалист": "FR_CSD", 
	"Начальник отдела": "FR_HoD", 
	"Специалист-координатор": "FR_SD",
	"Заместитель начальника отдела": "FR_DHoD", 
	"Инженер проектов отдела": "FR_PE",
	"Руководитель проектов": "FR_PM",
}

prefix_label = {
	"Отдел": "отдела",
	"Управление": "управления"
}

def createRoles(name, label = None):
	labels_prefix = ""

	if label:
		labels_list = label.split(" ")
		if labels_list[0] in prefix_label:
			labels_prefix = prefix_label[labels_list[0]]

	n = name[3:]

	for key in prefixes:
		if labels_prefix:
			if labels_prefix not in key:
				info = key + " " + labels_prefix + " " + " ".join(labels_list[1:])
			else:
				info = key + " " + " ".join(labels_list[1:])
		else:
			info = key
		print(info, " >> ", prefixes[key] + n)