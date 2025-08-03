// Copyright (c) 2025, ltl and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Salary Sheet Bangla"] = {
    "filters": [
        // {
		// 	"fieldname":"from_date",
		// 	"label": __("From"),
		// 	"fieldtype": "Date",
		// 	// "default": frm.doc.start_date,
		// 	"reqd": 0,
		// 	"width": "100px"
		// },
		// {
		// 	"fieldname":"to_date",
		// 	"label": __("To"),
		// 	"fieldtype": "Date",
		// 	// "default": filters.get(from_date),
		// 	"reqd": 0,
		// 	"width": "100px"
		// },
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "জানুয়ারি\nফেব্রুয়ারি\nমার্চ\nএপ্রিল\nমে\nজুন\nজুলাই\nআগস্ট\nসেপ্টেম্বর\nঅক্টোবর\nনভেম্বর\nডিসেম্বর",
			"default": [
				"জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন", "জুলাই",
				"আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"
			][new Date(frappe.datetime.now_date()).getMonth()]
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"reqd": 1
		},

		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"reqd": 0,
			"options": "Employee",
			"width": "100px"
		},

		{
            "fieldname":"docstatus",
            "label":__("Document Status"),
            "fieldtype":"Select",
            "options":["Draft", "Submitted", "Cancelled"],
            "default": "Draft",
            "width": "100px"
        },
			{
				"fieldname": "company",
				"fieldtype": "Link",
				"label": "Company",
				"mandatory": 0,
				"default": frappe.defaults.get_user_default("Company"),
				"options": "Company",
				"wildcard_filter": 0
			},

			{
			 "fieldname": "department",
			 "fieldtype": "Link",
			 "label": "Department",
			 "mandatory": 0,
			 "options": "Department",
			 "wildcard_filter": 0
			},
			{
			 "fieldname": "designation",
			 "fieldtype": "Link",
			 "label": "Designation",
			 "mandatory": 0,
			 "options": "Designation",
			 "wildcard_filter": 0
			},
			// {
			// 	"fieldname": "Sub-Department",
			// 	"fieldtype": "Data",
			// 	"label": "Sub-Department",
			// 	"mandatory": 0,
			// 	// "options": "Designation",
			// 	"wildcard_filter": 0
			//    },
			{
				"fieldname": "section",
				"fieldtype": "Link",
				"label": "Section",
				"mandatory": 0,
				"options": "Section",
				"wildcard_filter": 0
			   },	
			   {
				"fieldname": "group_name",
				"fieldtype": "Link",
				"label": "Employee Group",
				"mandatory": 0,
				"options": "Group",
				"wildcard_filter": 0
			   },
			   
			   {
				"fieldname": "facility_or_line",
				"fieldtype": "Link",
				"label": "Facility/Line",
				"mandatory": 0,
				"options": "Facility or Line",
				"wildcard_filter": 0

			   },

			   {
				"fieldname": "floor",
				"fieldtype": "Link",
				"label": "Floor",
				"mandatory": 0,
				"options": "Floor",
				"wildcard_filter": 0

			   },
			   {
				"fieldname": "grade",
				"fieldtype": "Link",
				"label": "Grade",
				"mandatory": 0,
				"options": "Employee Grade",
				"wildcard_filter": 0

			   },
			   {
				"fieldname":"mode_of_payment",
				"label":__("Bank/Cash"),
				"fieldtype":"Select",
				"options":["Bank","Cash",""],
				"default": "",
				"width": "100px"
			},
			{
				"fieldname": "bank",
				"fieldtype": "Link",
				"label": "Bank Name",
				"mandatory": 0,
				"options": "Bank",
				"wildcard_filter": 0,
				"depends_on": "eval:doc.mode_of_payment == 'Bank'"
			   },
			{
				"fieldname":"employee_type",
				"label":__("Employee Type"),
				"fieldtype":"Select",
				"options":["Active","New Join","Left",""],
				"default": "Active",
				"width": "100px"
			},
			   

			// {
			// 	"fieldname": "shift",
			// 	"fieldtype": "Link",
			// 	"label": "Shift",
			// 	"mandatory": 0,
			// 	"options": "Shift Type",
			// 	"wildcard_filter": 0
			// },

	],
	onload: function() {
		return  frappe.call({
			method: "erpbee_bangla_report.erpbee_bangla_report.report.pay_slip_bangla.pay_slip_bangla.get_salary_slip_years",
			callback: function(r) {
				var year_filter = frappe.query_report.get_filter('year');
				year_filter.df.options = r.message;
				year_filter.df.default = r.message[0];

				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});
	}
};




