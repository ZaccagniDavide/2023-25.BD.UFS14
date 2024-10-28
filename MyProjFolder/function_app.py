import azure.functions as func
import datetime
import json
import logging
from bs4 import BeautifulSoup
import requests

app = func.FunctionApp()

def get_pdf_link(report_url):
    response = requests.get(report_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        link_tags = soup.find_all('a', string=lambda text: text and 'Report' in text)
        if link_tags:
            first_pdf_link = link_tags[0]['href']
            return f"https://cir-reports.cir-safety.org{first_pdf_link.replace('..', '')}"
        else:
            return 'N/A: link non trovati'
    else:
        print(f"Errore nella richiesta del report: {response.status_code} - {response.reason}")
        return 'N/A: status code non 200'

@app.route(route="MyHttpTrigger", auth_level=func.AuthLevel.ANONYMOUS)
def MyHttpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    report_url = req.params.get('report_url')
    if not report_url:
        return func.HttpResponse("report_url: parametro obbligatorio")
    
    # return func.HttpResponse(f"report_url: {report_url}")

    pdf_data=get_pdf_link(report_url)
    
    return func.HttpResponse(f"pdf_data: {pdf_data}")



