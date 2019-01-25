from __future__ import unicode_literals
from collections import defaultdict
from datetime import date
from datetime import datetime
from datetime import timedelta
from erpnext.accounts.utils import get_fiscal_year
from erpnext.controllers.accounts_controller import get_taxes_and_charges
from frappe import throw, msgprint, _
from frappe.client import delete
from frappe.desk.notifications import clear_notifications
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, get_gravatar, format_datetime, now_datetime,add_days,today,formatdate,date_diff,getdate,add_months
from frappe.utils.password import update_password as _update_password
from frappe.utils.user import get_system_managers
import collections
import frappe
import frappe.permissions
import frappe.share
import json
import logging
import math
import random
import re
import string
import time
import traceback
import urllib
import urllib2





@frappe.whitelist()
def taskDateUpdate(self,method=None):
	if len(self.depends_on)>=1:
		childtask=frappe.db.sql("""select task from `tabTask Depends On` where parent=%s""",self.name)
		task_list=[]
		conditions=''
		conditions+="name in("
		for task in childtask:
			task_list.append(task[0])
			conditions+="'"+str(task[0])+"',"
		conditions+= "'b'"+')'
		minimum_date=frappe.db.sql("""select min(exp_start_date) from `tabTask` where {0}""".format(conditions))
		maximum_date=frappe.db.sql("""select max(exp_end_date) from `tabTask` where {0}""".format(conditions))
		if len(minimum_date)>0:
			if not minimum_date[0][0]==None:
				frappe.db.set_value("Task",self.name,"exp_start_date",str(minimum_date[0][0]))
		if len(maximum_date)>0:
			if not maximum_date[0][0]==None:
				frappe.db.set_value("Task",self.name,"exp_end_date",str(maximum_date[0][0]))



@frappe.whitelist()
def dateUpdateBasedOnChild(self,method):
	parent_task=frappe.db.sql("""select parent from `tabTask Depends On` where task=%s""",self.name)
	if len(parent_task)>0:
		task_doc=frappe.get_doc("Task",parent_task[0][0])
		if len(task_doc.depends_on)>=1:
			childtask=frappe.db.sql("""select task from `tabTask Depends On` where parent=%s""",self.name)
			conditions=''
			conditions+="name in("
			for task in childtask:
				conditions+="'"+str(task[0])+"',"
			conditions+= "'b'"+')'
			minimum_date=frappe.db.sql("""select min(exp_start_date) from `tabTask` where {0}""".format(conditions))
			maximum_date=frappe.db.sql("""select max(exp_end_date) from `tabTask` where {0}""".format(conditions))
			if len(minimum_date)>0:
				if not minimum_date[0][0]==None:
					task_doc.exp_start_date=str(minimum_date[0][0])
			if len(maximum_date)>0:
				if not maximum_date[0][0]==None:
					task_doc.exp_start_date=str(maximum_date[0][0])
		task_doc.save()
	changeProjectDate(self)

	

def changeProjectDate(self):
	if frappe.db.get_value("Project",self.project,"name"):
		project_doc=frappe.get_doc("Project",self.project)
		if len(project_doc.tasks)>=1:
			task_list=frappe.db.sql("""select task_id from `tabProject Task` where parent=%s""",self.project)
			conditions=''
			conditions+="name in("
			for task in task_list:
				conditions+="'"+str(task[0])+"',"
			conditions+= "'b'"+')'
			minimum_date=frappe.db.sql("""select min(exp_start_date) from `tabTask` where {0}""".format(conditions))
			maximum_date=frappe.db.sql("""select max(exp_end_date) from `tabTask` where {0}""".format(conditions))
			if len(minimum_date)>0:
				if not minimum_date[0][0]==None:
					project_doc.expected_start_date=str(minimum_date[0][0])
			if len(maximum_date)>0:
				if not maximum_date[0][0]==None:
					project_doc.expected_end_date=str(maximum_date[0][0])
			project_doc.save()


@frappe.whitelist()
def changeProjectDateBasedOnTask(self,method):
	if len(self.tasks)>=1:
		task_list=frappe.db.sql("""select task_id from `tabProject Task` where parent=%s""",self.name)
		if len(task_list)>=1:
			conditions=''
			conditions+="name in("
			for task in task_list:
				conditions+="'"+str(task[0])+"',"
			conditions+= "'b'"+')'
			minimum_date=frappe.db.sql("""select min(exp_start_date) from `tabTask` where {0}""".format(conditions))
			maximum_date=frappe.db.sql("""select max(exp_end_date) from `tabTask` where {0}""".format(conditions))
			if len(minimum_date)>0:
				if not minimum_date[0][0]==None:
					frappe.db.set_value("Project",self.name,"expected_start_date",minimum_date[0][0])
			if len(maximum_date)>0:
				if not maximum_date[0][0]==None:
					frappe.db.set_value("Project",self.name,"expected_end_date",maximum_date[0][0])
		
			
			
	

		


	
