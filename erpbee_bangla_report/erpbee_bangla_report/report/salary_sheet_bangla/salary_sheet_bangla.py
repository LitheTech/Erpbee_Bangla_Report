from datetime import datetime, timedelta
import frappe
from frappe.utils import flt
from frappe import _
from frappe.utils import add_days, cstr, date_diff, get_first_day, get_last_day, getdate

def to_bangla_number(number):
    en_to_bn = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')
    return str(number).translate(en_to_bn)

def execute(filters = None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_data(filters= None):
	type = frappe.db.get_value('User', frappe.session.user, 'type')
	if type is None or float(type)>11:
		hours_for_ot=34
	else:
		hours_for_ot=float(type)
	
	bangla_to_english_months = {
    "জানুয়ারি": "Jan",
    "ফেব্রুয়ারি": "Feb",
    "মার্চ": "Mar",
    "এপ্রিল": "Apr",
    "মে": "May",
    "জুন": "Jun",
    "জুলাই": "Jul",
    "আগস্ট": "Aug",
    "সেপ্টেম্বর": "Sep",
    "অক্টোবর": "Oct",
    "নভেম্বর": "Nov",
    "ডিসেম্বর": "Dec"
	}

	english_month = bangla_to_english_months[filters["month"]]
	from_date = get_first_day(english_month + "-" + filters["year"])
	to_date = get_last_day(english_month + "-" + filters["year"])
	if not filters:
		filters = {}
	data = []
	total_result=[]
	departments = frappe.db.get_list("Department", fields=["name", "department_in_bangla"], order_by="name")
	# frappe.publish_realtime('msgprint',departments)
	for department in departments:
		department_eng=department["name"]
		salary_slips = get_salary_slip(from_date,to_date,filters,department_eng)
		if len(salary_slips)==None:
			continue
		

		
		if len(salary_slips) >= 1:
			data.append({"বিভাগ": department["department_in_bangla"]})
		# else:
		# 	row = frappe._dict({"leave_type": department})
		result=[]

		for ss in salary_slips:
			allowance = 0
			acctual_basic,salary_slip_basic = get_basic(ss.name)
			if acctual_basic is None:
				acctual_basic = 0
			# salary_slip_basic = get_salary_basic(ss.name)
			if salary_slip_basic is None:
				salary_slip_basic = 0
			actual_allowance= (get_default_medical(ss.name) or 2375)+(acctual_basic/2)
			allowance = get_allowance(ss.name)
			acctual_lunch=get_lunch_tr_allowance(ss.name)+get_lunch(ss.name)+get_convanse(ss.name)
			if acctual_lunch is None:
				acctual_lunch=0
			leaves=frappe.db.sql('''select lt.name leave_name, ifnull(tot_lv,0) total_leaves from `tabLeave Type` lt left join  (select lti.name, count(a.attendance_date) tot_lv from `tabLeave Type` lti join tabAttendance a on lti.name = a.leave_type where a.employee=%s and a.status="On Leave" and a.attendance_date between %s and %s group by lti.name) ali on lt.name = ali.name;''',(ss.employee,ss.start_date,ss.end_date), as_dict=1)
			CL,EL,ML,SL,OL=0,0,0,0,0
			for l in leaves:
				if l.leave_name=="CL":
					CL=l.total_leaves
				elif l.leave_name=="EL":
					EL=l.total_leaves
				elif l.leave_name=="ML":
					ML=l.total_leaves
				elif l.leave_name=="SL":
					SL=l.total_leaves
				elif l.leave_name=="OL":
					OL=l.total_leaves

			
			if hours_for_ot>=10:
				overtime_hours=ss.overtime_hours
				ot_amount=ss.total_overtime_pay
				holiday_allowance=0 #it will deduct from gross and net pay so if acctual it is 0 and if buyer all its amount will deduct.
				# lunch=float(acctual_lunch)


			else:
				ot_hours = frappe.db.sql("""SELECT SUM(case when rounded_ot>%s then %s else rounded_ot end) FROM `tabAttendance` where status not in ('Holiday','Weekly Off') and employee=%s AND attendance_date between %s and %s group by employee""",
				(hours_for_ot,hours_for_ot,ss.employee, ss.start_date, ss.end_date))
				overtime_hours = ot_hours[0][0] if ot_hours else 0  
				ot_amount=(ot_hours[0][0] if ot_hours else 0  )*float(ss.overtime_rate)
				holiday_allowance=ss.holiday_allowance or 0 
				# if ss.present_days!=0:
				# 	lunch=(float(acctual_lunch)*ss.present_days/(ss.present_days+max(ss.late_days,ss.working_holidays)))#previously we count working_holidays in late_days 




			row = [
				None,
				#ss.name,
				ss.employee,
				ss.name_in_bangla,
				to_bangla_number(ss.date_of_joining),
				# ss.branch,
				# ss.department,
				# ss.designation,
				ss.designation_in_bangla,
				# ss.company,
				# ss.start_date,
				# ss.end_date,
				to_bangla_number(round(acctual_basic,0)),
				to_bangla_number(round(actual_allowance,0)-round((get_default_medical(ss.name) or 2375),0)),
				to_bangla_number(round((get_default_medical(ss.name) or 2375),0)),
				to_bangla_number(round(acctual_basic + actual_allowance,0)),
				to_bangla_number(ss.present_days),
				to_bangla_number(off_days(ss.employee, ss.start_date, ss.end_date)),
				to_bangla_number(CL),
				to_bangla_number(EL),
				to_bangla_number(ML),
				to_bangla_number(SL),
				to_bangla_number(OL),


				to_bangla_number(ss.absent_days),
				# ss.gross_pay,
				to_bangla_number(round(float((salary_slip_basic+allowance) or 0),0)),
				to_bangla_number(round(float(overtime_hours or 0),1)),
				#ss.total_overtime_pay,
				to_bangla_number(round(float(ot_amount or 0),0)),
				to_bangla_number(get_attendance_bonus(ss.name)),
				# get_lunch_tr_allowance(ss.name),
				to_bangla_number(float(acctual_lunch)),
				to_bangla_number(ss.night_days),
				to_bangla_number(get_night_allowance(ss.name)),
				to_bangla_number(ss.arear),
				to_bangla_number(round(ss.gross_pay-float(ss.total_overtime_pay)-float(acctual_lunch)-float(holiday_allowance)+float(acctual_lunch)+float(ot_amount),0)),
				to_bangla_number(round(ss.absent_deduction or 0,0)),
				to_bangla_number(round(get_pf(ss.name),0)),
				to_bangla_number(round(get_late_amt(ss.name),0)),
				to_bangla_number(get_stamp(ss.name)),
				to_bangla_number(round(ss.income_tax,0)),
				to_bangla_number(round(ss.other_deduction,0)),

				
				
			]

			
			row += [to_bangla_number(round(ss.total_loan_repayment,0)),
		   to_bangla_number((round(ss.total_deduction,0)+round(ss.total_loan_repayment,0))),
			to_bangla_number( round((ss.net_pay-float(ss.total_overtime_pay)-float(acctual_lunch)-float(holiday_allowance)+float(acctual_lunch)+float(ot_amount)),0)), None]
			

			
			# for i in range(len(row)): 
			# 	if i>15 and i<len(row)-1: # Use the length of 'row' to avoid accessing out of bounds
			# 		result.append(0)  # Initialize result with 0s or use an already initialized result list
			# 		result[i] = result[i] + row[i]
			# 	else:
			# 		result.append(None)
			
			data.append(row)
			# for index, p in enumerate(products):
  			# 	if index == len(products) - 1:
			# 		result[0]="Total"
			# 	data.append(result)
		# for index, ss in enumerate(salary_slips):
		# 	if index == len(salary_slips) - 1:
		# 		result[0]="Total"
		# 		result[1]="Total"
		# 		result[2]=len(salary_slips)
		# 		data.append(result)



	return data
	


def get_columns():
	columns = [
	_("বিভাগ") + "::150",
	_("কর্মচারী") + "::80",
	_("কর্মচারীর নাম") + "::40",
	_("যোগদানের তারিখ") + "::12",
	_("পদবি") + "::40",
	# _("শুরু তারিখ") + "::80",
	# _("শেষ তারিখ") + "::80",
	_("মূল বেতন") + "::10",
	_("বাড়িভাড়া ভাতা") + "::10",
	_("চিকিৎসা ভাতা") + "::10",
	_("মোট বেতন") + "::10",
	_("উপস্থিত") + ":Integer:5",
	_("কাজের ছুটি") + ":Integer:5",
	_("নৈ. ছুটি") + ":Integer:5",     # Casual Leave
	_("উপা.ছুটি") + ":Integer:5",   # Earned Leave → উপার্জিত ছুটি
	_("মা.ছুটি") + ":Integer:5",    # Maternity Leave
	_("অ.ছুটি") + ":Integer:5",     # Sick Leave
	_("বে.হীন ছুটি") + ":Integer:5",  # Long Leave / Leave Without Pay
	_("অনুপস্থিতি") + ":Integer:5",
	_("মোট বেতন") + ":Integer:10",
	_("ও.টি (ঘণ্টা)") + ":%.2Float:7",
	_("ও.টি পরিমাণ") + "::10",
	_("উপস্থিতি বোনাস") + ":Integer:5",
	_("দুপুরের ভাতা") + ":Integer:20",
	_("রাত্রি ভাতা (দিন)") + ":Integer:5",
	_("রাত্রি ভাতা (পরিমাণ)") + ":Integer:20",
	_("বকেয়া") + ":Integer:10",
	_("মোট প্রাপ্য") + ":Integer:20",


	]


	columns = (
		columns
		+ [
			_("অনুপস্থিতি কর্তন") + ":Integer:10",
			_("পিএফ") + ":Integer:10",
			_("বিলম্ব কর্তন") + ":Integer:10",
			_("স্ট্যাম্প") + ":Integer:10",
			_("কর") + ":Integer:10",
			_("অন্যান্য কর্তন") + ":Integer:10",
			_("অগ্রিম") + ":Integer:10",
			_("মোট কর্তন") + ":Integer:20",
			_("নেট পে") + ":Integer:20",
			_("স্বাক্ষর ও সিল") + ":Text:10",

		]
		
	)

	return columns




def get_salary_slip(from_date,to_date,filters,department):
	conditions, filters = get_conditions(from_date,to_date,filters,department)
	

	filters.update({"from_date": filters.get("from_date"), "to_date": filters.get("to_date")})
	conditions, filters = get_conditions(from_date,to_date,filters,department)
	

	salary_slips = frappe.db.sql("""select ss.*,e.status,e.relieving_date,e.lunch_rate,e.travel_rate,e.night_rate,e.designation_in_bangla,e.name_in_bangla from `tabSalary Slip` as ss inner join tabEmployee as e on ss.employee=e.name WHERE %s ORDER BY ss.department,employee
	""" 
	%conditions, filters, as_dict=1)


	return salary_slips or []




def get_conditions(from_date,to_date,filters,department):
	conditions="" 
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	if filters.get("docstatus"):
		conditions += "ss.docstatus = {0}".format(doc_status[filters.get("docstatus")])

	if department: conditions += " and ss.department= '%s'" % department

	if from_date: conditions += " and ss.start_date>= '%s'" % from_date
	if to_date: conditions += " and ss.end_date<= '%s'" % to_date
	if filters.get("employee"): conditions += " and ss.employee= '%s'" % filters["employee"]
	if filters.get("company"): conditions += " and ss.company= '%s'" % filters["company"]
	if filters.get("department"): conditions += " and ss.department= '%s'" % filters["department"]
	if filters.get("designation"): conditions += " and ss.designation='%s'" % filters["designation"]
	# if filters.get("shift"): conditions += " and att.shift='%s'" % filters["shift"]
	if filters.get("section"): conditions += " and ss.section='%s'" % filters["section"]
	if filters.get("floor"): conditions += " and ss.floor='%s'" % filters["floor"]
	if filters.get("facility_or_line"): conditions += " and ss.facility_or_line='%s'" % filters["facility_or_line"]
	if filters.get("group_name"): conditions += " and ss.group='%s'" % filters["group_name"]
	if filters.get("grade"): conditions += " and ss.grade='%s'" % filters["grade"]
	if filters.get("mode_of_payment"): conditions += " and ss.mode_of_payment='%s'" % filters["mode_of_payment"]
	if filters.get("bank"): conditions += " and ss.bank_name='%s'" % filters["bank"]
	if filters.get("employee_type"):
		if (filters["employee_type"]=="New Join"):
			conditions += " and ss.date_of_joining between ss.start_date and ss.end_date"
		if (filters["employee_type"]=="Active"):
			conditions += " and e.status='Active' "
		if (filters["employee_type"]=="Left"):
			conditions += " and e.status='Left' and e.relieving_date between ss.start_date and ss.end_date"


	return conditions, filters

def get_basic(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'B'}, ['default_amount','amount'])

# def get_salary_basic(ss):
	# return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'B'}, 'amount')

def get_allowance(ss):
	#return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'HR'}, 'SUM(amount)')
	return frappe.db.sql("""SELECT SUM(amount) FROM `tabSalary Detail` where parent=%s and abbr IN('M', 'HR')""", ss)[0][0]

def get_default_medical(ss):
	return frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'DM'}, ['default_amount'])

def off_days(employee, start_date, end_date):
	return frappe.db.sql("""SELECT COUNT(*) FROM `tabAttendance` as a where a.employee='%s' and status IN('Weekly Off', 'Holiday') and a.attendance_date BETWEEN '%s' AND '%s'""" % (employee, start_date, end_date))[0][0]


# def on_leave(employee, start_date, end_date):
# 	return frappe.db.sql("""SELECT COUNT(*) FROM `tabAttendance` as a where a.employee='%s' and status IN('Weekly Off', 'Holiday') and a.attendance_date BETWEEN '%s' AND '%s'""" % (employee, start_date, end_date))[0][0]


def get_attendance_bonus(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'AB'}, 'amount') or 0)

def get_lunch_tr_allowance(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'LT'}, 'amount') or 0)

def get_lunch(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'Lunch Allowance'}, 'amount') or 0)

def get_night_allowance(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'NA'}, 'amount') or 0)

def get_convanse(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'CNV'}, 'amount') or 0)

def get_pf(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'PF'}, 'amount') or 0)

def get_late_amt(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'LD'}, 'amount') or 0)

def get_stamp(ss):
	return (frappe.db.get_value('Salary Detail', {'parent': ss, 'abbr': 'ST'}, 'amount') or 0)