import logging, requests, re
import azure.functions as func
from ics import Calendar

name = re.compile(r"\s*(?P<key>.*?)\s*:\s*(?P<value>.*?)\s*(,|$)")

def entry_to_info(val):
    result = {}
    for m in name.finditer(val):
        value = m['value']
        if value == '_NN':
            continue
        key = m['key'].replace(',', '')
        result[key] = value
    return result

def get_calendar(calendar_url):
    url = "https://cloud.timeedit.net/itu/web/public/" + calendar_url
    c = Calendar(requests.get(url).text)

    for e in c.events:
        summary = entry_to_info(e.name)
        result = ""
        if 'Study Activity' in summary:
            result +=  re.sub(r"\.\s*[A-Z0-9]*", '', summary['Study Activity']) + ' - '
        if 'Activity' in summary:
            result += summary['Activity']
        e.name = result
        e.location = name.search(e.location)['value']
    
    return c

def main(req: func.HttpRequest) -> func.HttpResponse:
    calendar_url = req.route_params.get('calendar_url') 
    logging.info(f'Request for: {calendar_url}')

    return func.HttpResponse(str(get_calendar(calendar_url)))
