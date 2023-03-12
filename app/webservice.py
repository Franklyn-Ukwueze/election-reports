import os
from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from app.helpers import stamp, retrieve_reports, urgent2k_token_required, reports

urgent2k_token = os.environ.get("URGENT_2K_KEY")


# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)

class Home(Resource):
    @urgent2k_token_required
    def get(self):
        return {'message': "Welcome to the homepage of this webservice."}
api.add_resource(Home,'/')

class SendReport(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('phone', 
                    type=str,
                    required=False,
                    help="Enter phonenumber of agent")
    parser.add_argument('PU', 
                    type=str,
                    required=False,
                    help="Enter polling unit of agent")
    parser.add_argument('delimit', 
                    type=str,
                    required=True,
                    help="Enter delimit of polling unit")
    parser.add_argument('report', 
                    type=str,
                    required=True,
                    help="Enter the type of report being made")
    parser.add_argument('desc', 
                    type=str,
                    required=True,
                    help="Enter description of the report")
    parser.add_argument('more', 
                    type=dict,
                    required=False,
                    help="Enter voting details if this is a result report")
    
    
    @urgent2k_token_required
    def post(self):
        payload = SendReport.parser.parse_args()
        userphone = payload["phone"]
        PU = payload["PU"]
        delimit = payload["delimit"]
        report = payload["report"]
        desc = payload["desc"]
        voting_details = payload["more"]


        stamptime = stamp()

        if report == "result":
            data = {userphone:True , "PU":PU, delimit:True, "report":report, "desc":desc, "more":voting_details, "datetime":stamptime}
        else:
            data = {userphone:True, "PU":PU, delimit:True, "report":report, "desc":desc, "more":dict(), "datetime":stamptime}

        reports.insert_one(data)
        return {"status": True, "message":"report has been submitted successfully", "data": None }, 200
api.add_resource(SendReport, "/sendreport")

class RetrieveReports(Resource):
    @urgent2k_token_required
    def get(self):
        data = reports.find({}).sort("datetime", -1)
        report_list = []
        for report in data:
            report_list.append(report)
        return {"status": True, "message":"reports have been retrieved successfully", "data": report_list }, 200
api.add_resource(RetrieveReports, "/retrievereports")        

class RetrieveByNumber(Resource):
    @urgent2k_token_required
    def get(self, phone):
        if phone.isdigit() and len(phone) == 11:
            data = retrieve_reports()
            report_list = []
            for i in data:
                if i.get(phone):
                    report_list.append(i)
            return {"status": True, "message":"reports have been retrieved successfully", "data": report_list }, 200


        else:
            return {"status": False, "message":"invalid phonenumber", "data": None }, 400
api.add_resource(RetrieveByNumber, "/retrievebynumber/<string:phone>")    

class RetrieveByPU(Resource):
    @urgent2k_token_required
    def get(self, pu):
        polling_unit = reports.find_one({"PU": pu})
        if polling_unit:
            data = retrieve_reports()
            report_list = []
            for i in data:
                if i.get("PU") == pu:
                    report_list.append(i)
            return {"status": True, "message":"reports have been retrieved successfully", "data": report_list }, 200


        else:
            return {"status": False, "message":"invalid polling unit", "data": None }, 400
api.add_resource(RetrieveByPU, "/retrievebypu/<string:pu>")    


class RetrieveByReportType(Resource):
    @urgent2k_token_required
    def get(self, report):
        
        data = retrieve_reports()
        report_list = []
        for i in data:
            if i.get("report") == report:
                report_list.append(i)
        return {"status": True, "message":"reports have been retrieved successfully", "data": report_list }, 200

api.add_resource(RetrieveByReportType, "/retrievebyreporttype/<string:report>")    

class RetrieveReportPerPUorNumber(Resource):
    @urgent2k_token_required
    def get(self, phone_or_pu, report):
            data = retrieve_reports()
            report_list = []
            for i in data:
                if (i.get("PU") == phone_or_pu or i.get(phone_or_pu) == True) and i.get("report") == report :
                    report_list.append(i)
            return {"status": True, "message":"reports have been retrieved successfully", "data": report_list }, 200

api.add_resource(RetrieveReportPerPUorNumber, "/retrievebynumber/<string:phone_or_pu>/<string:report>")    
