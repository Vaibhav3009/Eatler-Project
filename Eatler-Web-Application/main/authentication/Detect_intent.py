import os
import dialogflow_v2beta1 as dialogflow
from google.api_core.exceptions import InvalidArgument
import uuid
import cgi

def detect_intent(text_to_be_analyzed):


    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './eatler-tgdjdx-3ab8e4382f8f.json' #[path] of eatler-tgdjdx-3ab8e4382f8f.json

    DIALOGFLOW_PROJECT_ID = 'eatler-tgdjdx'
    DIALOGFLOW_LANGUAGE_CODE = 'en'
    SESSION_ID = uuid.uuid1()

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
    text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise

    reply=response.query_result.fulfillment_text
    intent=response.query_result.intent.display_name
    return intent,reply

def ui(text_to_be_analyzed):
    intent,reply=detect_intent(text_to_be_analyzed)
    return reply

if __name__=='__main__':
    print("mil gyi")
    form=cgi.FieldStorage()
    text_to_be_analyzed=form.getvalue("message")
    print(ui(text_to_be_analyzed))
