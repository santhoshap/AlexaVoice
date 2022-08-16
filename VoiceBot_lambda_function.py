#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import json
import os
import pymysql
import sys
import smtplib
import boto3
import math
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from email.header import Header
from email import encoders
from getpass import getpass
from smtplib import SMTP_SSL

REGION = 'us-east-1'

rds_host = 'mysql-instance1.cgicnt0oac3v.us-east-1.rds.amazonaws.com'
name = 'sanhack12'
password = 'sanhack12'
db_name = 'Sanhack'
port = 3306


def lambda_handler(event, context):

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId'
                           ]}, event['session'])

    if event['request']['type'] == 'LaunchRequest':
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == 'IntentRequest':
        return on_intent(event['request'], event['session'], event,
                         context)
    elif event['request']['type'] == 'SessionEndedRequest':

        # return on_intent(event, context)

        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    print 'Starting new session.'

###################################################
def on_launch(launch_request, session):

    print 'on_launch requestId=' + launch_request['requestId'] \
        + ', sessionId=' + session['sessionId']
    return get_welcome_response()


def get_welcome_response():

    session_attributes = {}
    card_title = 'Welcome'
    speech_output = \
        'Welcome to the Fidelity Workplace Solutions Voice Assistant. How can I help you today?'
    reprompt_text = ''
    should_end_session = True
    return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))

###################################################

def on_intent(
    intent_request,
    session,
    event,
    context,
    ):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == 'GetAccountBalanceIntent':
        return get_account_balance_status(event, context)
    elif intent_name == 'GetMyTaxFormIntent':
        return get_my_tax_form(event, context)
    elif intent_name == 'GetLoanQueryIntent':
        return get_query_intent(event, context)
    elif intent_name == 'GetWithdrawlQueryIntent':
        return get_withdrawl_intent(event, context)
    elif intent_name == 'GetNBNavigationIntent':
        return get_nb_navigation_intent(event, context)
    elif intent_name == 'GetLoanStatus':
        return get_loan_status(event, context)
    elif intent_name == 'GetNotifications':
        return get_notifications(event, context)
    elif intent_name == 'GetElevatedPitch':
        return get_elevated_pitch(event, context)
    elif intent_name == 'GetWelcomeIntent': 
        return welcome_intent()
    elif intent_name == 'UnhandledIntent':
        return unhandled()
    elif intent_name == 'AMAZON.HelpIntent':
        return get_welcome_response()
    elif intent_name == 'AMAZON.CancelIntent' or intent_name \
        == 'AMAZON.StopIntent':
        return handle_session_end_request()
    else:
        raise ValueError('Invalid intent')


############################

def openConn():
    global conn
    print 'trying to connect.'
    try:
        conn = pymysql.connect(rds_host, user=name, passwd=password,
                               db=db_name, connect_timeout=30)
        print 'connect.'
    except Exception, e:
        print e
        print 'ERROR: Unexpected error: Could not connect to MySql instance.'
        raise e


#############################

def get_account_balance_status(event, context):
    session_attributes = {}
    card_title = 'FidVoice A/C Balance Status'
    reprompt_text = ''
    should_end_session = True

    dialog_state = event['request']['dialogState']

    if dialog_state in ('STARTED', 'IN_PROGRESS'):
        print 'dialogState in STARTED'
        return continue_dialog()
    elif dialog_state == 'COMPLETED':

        print 'dialogState in COMPLETED'
        json_obj = json.dumps(event)
        json1 = json.loads(json_obj)
        pin = json1['request']['intent']['slots']['Pin']['value']
        print pin
        openConn()
        with conn.cursor() as cur2:
            sql = 'select password(%s)' 
            args=[[pin]] 
            response1 = cur2.execute(sql,args)
            print response1
    for row in cur2.fetchall():
        ipin = row[0]
        print ipin

        openConn()
        with conn.cursor() as cur:
            response = cur.execute('select * from p_person')
    for row in cur.fetchall():
        alx_pin = row[5]
        print alx_pin
        
    if (ipin == alx_pin):
        openConn()
        with conn.cursor() as cur1:
            rest = cur1.execute('select * from p_per_acc_bal')
        for row in cur1.fetchall():
            amount = row[1]
            date = row[2]
            print amount
            speech_output = 'You current account balance is ' \
                + str(amount) + ' dollars as per the last update date ' \
                + str(date)
            print speech_output    
    else:
        speech_output = 'The pin is incorrect. Please try again'

    return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))

####################################
   
def get_my_tax_form(event, context):

    session_attributes = {}
    card_title = 'FidVoice tax form Status'
    reprompt_text = ''
    should_end_session = True
    
    dialog_state = event['request']['dialogState']
    
    if dialog_state in ('STARTED', 'IN_PROGRESS'):
        print 'dialogState in STARTED'
        return continue_dialog()
    elif dialog_state == 'COMPLETED':
        print 'dialogState in COMPLETED'
        json_obj = json.dumps(event)
        json1 = json.loads(json_obj)
        quarter = json1['request']['intent']['slots']['Quarter']['value']
        print quarter

        openConn()
        with conn.cursor() as cur:
            response = cur.execute('select * from p_per_tax_form_dets')
    for row in cur.fetchall():
        p_quarter = row[2]
        p_form_url = row[4]
        print p_quarter
        
    if (quarter == p_quarter):
        openConn()
        with conn.cursor() as cur1:
            resp = cur1.execute('select * from p_person')
            
        for resp in cur1.fetchall():
            fname = resp[1]
            userid = resp[3]
            domain = resp[4]
        targets = userid + '@' + domain
        
        smtp_ssl_host = 'smtp.gmail.com'  # smtp.mail.yahoo.com
        smtp_ssl_port = 465
        username = 'fidvoice2018@gmail.com'
        password = 'welcome12*'
        sender = 'FidVoice'

        msg = MIMEMultipart()
        msg['Subject'] = 'Tax Form'
        msg['From'] = sender
        msg['To'] = ', '.join(targets)
        body = 'Hello ' + fname + ',' +'\n' +'\nPFA your requested tax 1099 form\n'+ '\nRegards,\n' + 'Team FidVoice'

        msg.attach(MIMEText(body, 'plain'))
        filename = 'Tax Form-2017_Q4.pdf'
        req = urllib2.Request(p_form_url)
        attachment = urllib2.urlopen(req)

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename= %s'
                        % filename)

        msg.attach(part)
        server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
        print 'connected to smtp'
        server.login(username, password)
        server.sendmail(sender, targets, msg.as_string())
        server.quit()
        #numberdigits = spellDigitOutput(1099)
        speech_output = \
            'Your ' + quarter + ' tax form has been sent to your registered e-mail account'
        
    else:
        speech_output = 'Your ' + quarter + ' 1099 form is not available. Please try later'

    return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))

##########################################################

def get_query_intent(event, context):

    session_attributes = {}
    card_title = 'FidVoice loan query'
    reprompt_text = ''
    should_end_session = True

    dialog_state = event['request']['dialogState']

    if dialog_state in ('STARTED', 'IN_PROGRESS'):
        print 'dialogState in STARTED'
        return continue_dialog()
    elif dialog_state == 'COMPLETED':

        print 'dialogState in COMPLETED'
        json_obj = json.dumps(event)
        json1 = json.loads(json_obj)
        slot = json1['request']['intent']['slots']['Account']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']

        if slot == 'Loan':
           openConn()
           with conn.cursor() as cur:
                res = cur.execute('select * from p_per_loan_info')
           
           if res == 1:
                speech_output = \
                    'Loan is not available. Your plan allows only one loan per year and that has already been exhausted'
           else:
             speech_output = 'No information avaiable on loans currently. Please try later'  
        else:
            speech_output = 'No information avaiable on loans currently. Please try later'
            
        return build_response(session_attributes,
                              build_speechlet_response(card_title,
                              speech_output, reprompt_text,
                              should_end_session))
    else:
        return statement('loan_intent', 'No dialog')

#####################################

def get_withdrawl_intent(event, context):

    session_attributes = {}
    card_title = 'FidVoice withdrawl query'
    reprompt_text = ''
    should_end_session = True

    smtp_ssl_host = 'smtp.gmail.com'  # smtp.mail.yahoo.com
    smtp_ssl_port = 465
    username = 'fidvoice2018@gmail.com'
    password = 'welcome12*'
    sender = 'FidVoice'
    
    dialog_state = event['request']['dialogState']

    if dialog_state in ('STARTED', 'IN_PROGRESS'):
        print 'dialogState in STARTED'
        return continue_dialog()
    elif dialog_state == 'COMPLETED':

        openConn()
        with conn.cursor() as cur:
            response = cur.execute('select * from p_person')
        for row in cur.fetchall():
            fname = row[1]
            userid = row[3]
            domain = row[4]
    
        targets = userid + '@' + domain

        msg = MIMEMultipart()
        msg['Subject'] = 'Withdrawl'
        msg['From'] = sender
        msg['To'] = ', '.join(targets)
        body = 'Hello ' + fname + ',' +'\n' +'\nPlease refer the attached document for withdrawl details\n'+ '\nRegards,\n' + 'Team FidVoice'
            
        msg.attach(MIMEText(body, 'plain'))
        filename = 'Terms and Conditions.pdf'
        req = \
        urllib2.Request('https://s3.amazonaws.com/mynvirgbuck/Terms+and+Conditions.pdf'
                        )
        attachment = urllib2.urlopen(req)

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename= %s'
                    % filename)

        msg.attach(part)
        server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
        print 'connected to smtp'
        server.login(username, password)
        server.sendmail(sender, targets, msg.as_string())
        server.quit()
        speech_output = 'You can do a partial withdrawl of rollover type. Please refer to the details sent on your registered e-mail account'
        return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))
    else:
        return statement('loan_intent', 'No dialog')
                          
############################################

def get_nb_navigation_intent(event, context):

    session_attributes = {}
    card_title = 'FidVoice withdrawl query'
    reprompt_text = ''
    should_end_session = True

    smtp_ssl_host = 'smtp.gmail.com'  # smtp.mail.yahoo.com
    smtp_ssl_port = 465
    username = 'fidvoice2018@gmail.com'
    password = 'welcome12*'
    sender = 'FidVoice'

    # targets = ['santhosh.puttaraju@fmr.com']

    openConn()
    with conn.cursor() as cur:
        response = cur.execute('select * from p_person')
    for row in cur.fetchall():
        fname = row[1]
        userid = row[3]
        domain = row[4]
    targets = userid + '@' + domain

    msg = MIMEMultipart()
    msg['Subject'] = 'Add Dependent on NetBenefits'
    msg['From'] = sender
    msg['To'] = ', '.join(targets)
    body = 'Hello ' + fname + ',' +'\n' +'\nPlease refer the attached document for NetBenefits navigation for adding a dependent\n'+ '\nRegards,\n' + 'Team FidVoice'

    msg.attach(MIMEText(body, 'plain'))
    filename = 'Terms and Conditions.pdf'
    req = \
        urllib2.Request('https://s3.amazonaws.com/mynvirgbuck/Terms+and+Conditions.pdf'
                        )
    attachment = urllib2.urlopen(req)

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename= %s'
                    % filename)

    msg.attach(part)
    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    print 'connected to smtp'
    server.login(username, password)
    server.sendmail(sender, targets, msg.as_string())
    server.quit()

    speech_output = \
        'Please use the NetBenefits navigation instructions sent to your registered e-mail account for adding a dependent'

    return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))

###################################################                          
def get_loan_status(event, context):
    session_attributes = {}
    card_title = 'FidVoice A/C Balance Status'
    reprompt_text = ''
    should_end_session = True

    dialog_state = event['request']['dialogState']

    if dialog_state in ('STARTED', 'IN_PROGRESS'):
        print 'dialogState in STARTED'
        return continue_dialog()
    elif dialog_state == 'COMPLETED':
        print 'dialogState in COMPLETED'
        json_obj = json.dumps(event)
        json1 = json.loads(json_obj)
        loanid = json1['request']['intent']['slots']['LoanID']['value']
        print loanid
        openConn()
        with conn.cursor() as cur:
            response = cur.execute('select * from p_per_loan_info')
    
    for row in cur.fetchall():
        per_loan_id = row[1]
        print per_loan_id
    if (loanid == per_loan_id):
        openConn()
        with conn.cursor() as cur1:
            rest = cur1.execute('select * from p_per_loan_info')
        for row in cur1.fetchall():
            status = row[3]
            sent_dt = row[4]
            
            speech_output = 'Your loan has been ' \
                + status + '. The cheque has been sent on ' \
                + str(sent_dt) + ' through US mail and you should be receiving within 10 days.'
            print speech_output    
    else:
        speech_output = 'Your loan ID does not exist. Please try again'

    return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))
                          
############################################
def get_notifications(event, context):

    session_attributes = {}
    card_title = 'FidVoice Notifications'
    reprompt_text = ''
    should_end_session = True

    openConn()
    with conn.cursor() as cur:
        response = cur.execute('select * from p_per_notificatins')
    for row in cur.fetchall():
        notifs = row[2]
        
    speech_output = \
        'These are the notifications. ' + notifs
        
    return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))
                          
############################################
def get_elevated_pitch(event, context):

    session_attributes = {}
    card_title = 'FidVoice Notifications'
    reprompt_text = ''
    should_end_session = True

    speech_output = 'Sure Santhosh. Let me do this for you since you and your team are too exhausted at this point. Haha! Hello everyone! Welcome to the WS Hackathan! Our idea is to solve the bane of many industries, which is the huge call volumes. Over the past few years we’ve added a huge number of participants which has accentuated our call volumes and the people needed to support them. With the projected addition of millions of more participants, it is only going to increase the call volumes. The available communication channels today might not be enough to support them. Our proposed idea is to build a self-service interaction channel, which is voice based. This can cater across different demographies; from a millennial to an octogenarian. We are mainly looking to address the queries which are informational, educational and  navigational in nature. This would help us reduce a good amount of call volumes which do not need human intervention. Also, we are creating a channel with no wait time and which is available 24 by 7. The tech behind our solution is entirely cloud based. We are using the Amazon Web Services like VPC, Lambda, R D S, S3 and the Amazon Skills Kit which will interact with the Amazon Echo. With that, lets get to the demo. We will be presenting some real life use cases without the user having to make a phone call.'
    return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))

################################################### 
def continue_dialog():
    session_attributes = {}
    message = {}
    message['shouldEndSession'] = False
    print 'In continue_dialog routine'
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return build_response1(message)


def build_response1(message, session_attributes={}):
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = message
    return response


def statement(title, body):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = True
    return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))

#########################
def welcome_intent():
    session_attributes = {}
    card_title = 'FidVoice welcome_intent'
    reprompt_text = ''
    should_end_session = True

    speech_output = 'Welcome distinguished guests; its a pleasure'
    return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))

##############################
def unhandled():
    session_attributes = {}
    card_title = 'FidVoice unhandled'
    reprompt_text = ''
    should_end_session = True

    speech_output = "I'm sorry, what's that?"
    return build_response(session_attributes,
                          build_speechlet_response(card_title,
                          speech_output, reprompt_text,
                          should_end_session))


def build_speechlet_response(
    title,
    output,
    reprompt_text,
    should_end_session,
    ):
    return {
        'outputSpeech': {'type': 'PlainText', 'text': output},
        'card': {'type': 'Simple', 'title': title, 'content': output},
        'reprompt': {'outputSpeech': {'type': 'PlainText',
                     'text': reprompt_text}},
        'shouldEndSession': should_end_session,
        }


def build_response(session_attributes, speechlet_response):
    return {'version': '1.0', 'sessionAttributes': session_attributes,
            'response': speechlet_response}



			
			