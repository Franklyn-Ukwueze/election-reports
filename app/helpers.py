import os
from datetime import datetime, timedelta, date
#from app import reports
from pymongo import MongoClient
from functools import wraps
from flask import request

client = MongoClient(os.getenv("MONGO_URI"))
db = client.election_reports
reports = db.reports

urgent2k_token = os.environ.get("URGENT_2K_KEY")
#base_url = os.getenv("SAFEPAY_URL")

# decorator function frequesting api key as header
def urgent2k_token_required(f):
    @wraps(f)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return {"status": False, "message": "Access token is missing at " + request.url, "data": None}, 401

        if token == urgent2k_token:
            return f(*args, **kwargs)
        else:
            return {"status": False, "message": "Invalid access token at " + request.url, "data": None}, 401

    return decorated

def stamp():
    return str(datetime.utcnow() + timedelta(hours=1))

def send_report(userphone, PU, delimit, report, desc, no_of_registered_voters=None, no_of_accreditedvoters=None, no_of_total_valid_votes=None, NNPPvotes=None, APCvotes=None, PDPvotes=None, LPvotes=None):
    stamptime = stamp()

    if report == "result":
        data = {userphone:True, "PU":PU, delimit:True, "report":report, "desc":desc, "more":{"number_of_voters_on_register":no_of_registered_voters, "number_of_accredited_voters":no_of_accreditedvoters,"number_of_total_valid_votes":no_of_total_valid_votes, "number_of_votes_for_NNPP": NNPPvotes, "number_of_votes_for_APC":APCvotes, "number_of_votes_for_LP":LPvotes,"number_of_votes_for_PDP": PDPvotes}, "datetime":stamptime}
    else:
        data = {userphone:True, "PU":PU, delimit:True, "report":report, "desc":desc, "more":dict(), "datetime":stamptime}

    reports.insert_one(data)
    return "report submitted successfully"


def retrieve_reports():
    data = reports.find().sort("datetime", -1)
    report_list = []
    for report in data:
        report_list.append(report)
    return report_list



def get_report_number(userphone):
    if userphone.isdigit() and len(userphone) == 11:
        data = retrieve_reports()
        for i in data:
            if i.get(userphone):
                return i

    else:
          return "invalid number"
    
def get_report_PU(PU):
    data = retrieve_reports()
    for i in data:
        if i.get("PU") == PU:
            return i
        
def get_report(report):
    data = retrieve_reports()
    for i in data:
        if i.get("report") == report:
            return i
        
def get_report_per_PU(phone_or_pu, report):
    data = retrieve_reports()
    for i in data:
        if (i.get("PU") == phone_or_pu or i.get(phone_or_pu) == True) and i.get("report") == report :
            return i


            


#send_report("09015889838", "idl pu", "02-05-17-009", "result", "governorship", "2758", "2700", "2500", "1000", "600","400", "500" )
print(retrieve_reports())
#print(get_report_number("08034555775"))