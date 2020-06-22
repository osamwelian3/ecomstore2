import xml
from xml.dom.minidom import Document
from xml.dom import minidom


# messages1
def get_messages_result_code(doc=''):
    if doc.getElementsByTagName('resultCode'):
        resultcode = doc.getElementsByTagName('resultCode')
        return resultcode[0].firstChild.data


def get_messages_message1_code(doc=''):
    if doc.getElementsByTagName('code'):
        code = doc.getElementsByTagName('code')
        return code[0].firstChild.data


def get_messages_message1_text(doc=''):
    if doc.getElementsByTagName('text'):
        text = doc.getElementsByTagName('text')
        return text[0].firstChild.data


# transaction Response
def get_tr_response_code(doc=''):
    if doc.getElementsByTagName('responseCode'):
        responsecode = doc.getElementsByTagName('responseCode')
        return responsecode[0].firstChild.data


def get_tr_auth_code(doc=''):
    if doc.getElementsByTagName('authCode'):
        authcode = doc.getElementsByTagName('authCode')
        return authcode[0].firstChild.data


def get_tr_avsresult_code(doc=''):
    if doc.getElementsByTagName('avsResultCode'):
        avsresultcode = doc.getElementsByTagName('avsResultCode')
        return avsresultcode[0].firstChild.data


def get_tr_cvvresult_code(doc=''):
    cvvresultcode = doc.getElementsByTagName('cvvResultCode')
    return cvvresultcode[0].firstChild.data


def get_tr_cavvresult_code(doc=''):
    if doc.getElementsByTagName('cavvResultCode'):
        cavvresultcode = doc.getElementsByTagName('cavvResultCode')
        return cavvresultcode[0].firstChild.data


def get_tr_trans_id(doc=''):
    if doc.getElementsByTagName('transId'):
        transid = doc.getElementsByTagName('transId')
        return transid[0].firstChild.data


def get_tr_reftrans_id(doc=''):
    if doc.getElementsByTagName('refTransId'):
        reftransid = doc.getElementsByTagName('refTransId')
        return reftransid[0].firstChild.data


def get_tr_trans_hash(doc=''):
    if doc.getElementsByTagName('transHash'):
        transhash = doc.getElementsByTagName('transHash')
        return transhash[0].firstChild.data


def get_tr_account_number(doc=''):
    if doc.getElementsByTagName('accountNumber'):
        accountnumber = doc.getElementsByTagName('accountNumber')
        return accountnumber[0].firstChild.data


def get_tr_account_type(doc=''):
    if doc.getElementsByTagName('accountType'):
        account_type = doc.getElementsByTagName('accountType')
        return account_type[0].firstChild.data


def get_tr_msgs_msg_code(doc=''):
    if doc.getElementsByTagName('code'):
        code = doc.getElementsByTagName('code')
        return code[1].firstChild.data


def get_tr_msgs_msg_desc(doc=''):
    if doc.getElementsByTagName('description'):
        description = doc.getElementsByTagName('description')
        return description[0].firstChild.data


def get_trans_hash_sha2(doc=''):
    if doc.getElementsByTagName('transHashSha2'):
        transhash2 = doc.getElementsByTagName('transHashSha2')
        return transhash2[0].firstChild.data


def get_network_trans_id(doc=''):
    if doc.getElementsByTagName('networkTransId'):
        networktransid = doc.getElementsByTagName('networkTransId')
        return networktransid[0].firstChild.data


def get_tr_errors_error_code(doc=''):
    if doc.getElementsByTagName('errorCode'):
        errorcode = doc.getElementsByTagName('errorCode')
        return errorcode[0].firstChild.data


def get_tr_errors_error_text(doc=''):
    if doc.getElementsByTagName('errorText'):
        errortext = doc.getElementsByTagName('errorText')
        return errortext[0].firstChild.data
