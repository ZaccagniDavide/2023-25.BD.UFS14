import azure.functions as func
import datetime
import json
import logging
from bs4 import BeautifulSoup
import requests
import os

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
    
def download_pdf(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        pdf_path = 'report.pdf'
        with open(pdf_path, 'wb') as file:
            file.write(response.content)
        return pdf_path
    else:
        print(f"Errore nel download del PDF: {response.status_code} - {response.reason}")
        return None

@app.route(route="MyHttpTrigger", auth_level=func.AuthLevel.ANONYMOUS)
def MyHttpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    report_url = req.params.get('report_url')
    if not report_url:
        return func.HttpResponse("report_url: parametro obbligatorio")
    
    # return func.HttpResponse(f"report_url: {report_url}")
    try:
        pdf_data=get_pdf_link(report_url)
    except Exception as error:
        return func.HttpResponse(f"pdf_data error: {error}")
    
    if 'N/A' in pdf_data:
        return func.HttpResponse("pdf_data: senza non si procede")
    

    try:
        response_download=download_pdf(pdf_data)

    except Exception as error:
        return func.HttpResponse(f"pdf_data error: {error}")
    report_path=os.path.abspath(response_download)
    response_payload = {"pdf_data": pdf_data, "report_url ": report_url, "report_path": report_path}
    return func.HttpResponse(
        json.dumps(response_payload),
        mimetype="application/json",
    )
    


