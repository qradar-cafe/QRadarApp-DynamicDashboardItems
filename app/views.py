# Licensed Materials - Property of IBM
# 5725I71-CC011829
# (C) Copyright IBM Corp. 2015, 2020. All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.

from flask import Blueprint, render_template, current_app, send_from_directory
from qpylib import qpylib

from flask import request, send_file
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from docxtpl import DocxTemplate, InlineImage, RichText
from openpyxl import Workbook, load_workbook
import matplotlib.pyplot as plt
from docx.shared import Mm
import io
import re
import math
import os.path
from glob import glob
from string import Template


# pylint: disable=invalid-name
viewsbp = Blueprint('viewsbp', __name__, url_prefix='/')

###########################################################################################
# This is a proof of concept app and it is provided as-is. There is no support of any kind.
###########################################################################################

def api_get(api):
    try:
        headers = {'content-type' :  'application/json', 'SEC':'86b98e92-5214-474f-aba4-28ed496f06a3'}
        #qpylib.log("api_get: " + api, level='ERROR')
        response = qpylib.REST('GET', api, headers=headers)
        result = response.json()
    except Exception as e:
        qpylib.log(str(e), level='ERROR')
        result = {'message': str(e)}
    return result

def getDataFromAPI():
    # get data from API
    #result = api_get('/api/reference_data/sets/UBA : Dormant Accounts')
    #df=pd.json_normalize(result['data'])
    result = api_get('/api/config/event_sources/log_source_management/log_sources')
    df=pd.json_normalize(result)
    df = df.rename(columns={'identifier':'Log Source Identifier', 'status.status':'Status', 'enabled':'Enabled'})

    # merge data if needed
    #df = pd.merge(df_left, df_right, how='left',left_on=['Log Source Identifier'], right_on=['ip_address'])
    
    # some cleaning
    df.fillna("NOT SET", inplace=True)
    df['Count']=1

    return df

_df = getDataFromAPI()

@viewsbp.route('/reload')
def reload():
    global _df
    _df=getDataFromAPI()
    return {'result':'DataFrame reloaded'}

@viewsbp.route('/query')
def query():
    df=_df

    # get parameters 
    query = request.args.get('query')
    fields = request.args.get('fields')
    columns = request.args.get('columns')
    groupBy = request.args.get('groupBy')
    head = int(request.args.get('top')) if request.args.get('top') else None
    format = request.args.get('format') or 'json'
    
    # apply parameters if provided
    if fields and fields != 'NONE':
        #qpylib.log('fields before: ' + fields, level='ERROR')
        fields = ' and '.join([i for i in fields.split('|') if not (i.endswith("'ANY'") or i.endswith(' ANY'))])
        fields = fields.replace('Enabled == true', 'Enabled == True').replace('Enabled == false','Enabled == False')
        if fields: df = df.query(fields)
        #qpylib.log('fields after: ' + fields, level='ERROR')
    if columns and columns != 'NONE':
        df = df[columns.split(",")]
    if query and query != 'NONE': 
        query = query.strip(' and ').strip(' and')
        df = df.query(query)
    if groupBy and groupBy != 'NONE': 
        df = pd.pivot_table(df,index=groupBy,values='Count', aggfunc=len).reset_index()
    if head and head != 'NONE': 
        df = df.head(head)

    # return data
    if format == 'html':
        return df.to_html()
    elif format == 'excel':
        buffer = io.BytesIO()
        df.to_excel(buffer)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, attachment_filename='output.xlsx', mimetype='application/xlsx')
    elif format == "summary":
        return f' [ {{ "Download": "excel", "groupBy": "{groupBy}", "query": "{query}", "fields": "{fields}" }} ] '
    else:
        return df.to_json(orient='records')



# The presence of this endpoint avoids a Flask error being logged when a browser
# makes a favicon.ico request. It demonstrates use of send_from_directory
# and current_app.
@viewsbp.route('/favicon.ico')
def favicon():
    return send_from_directory(current_app.static_folder, 'favicon-16x16.png')
