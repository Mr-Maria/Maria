import io
from .models import Company
import requests
import xml.etree.ElementTree as ET
import re


def download_and_temp_save(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    if not response.content:
        raise ValueError("No content downloaded")
    content = io.BytesIO(response.content)
    return content, None


def process_xml(zip_file, companies_dict):
    first = zip_file.infolist()[0]
    with zip_file.open(first, 'r') as data:
        xml_data = data.read().decode('Windows-1250')
        root = ET.fromstring(xml_data)
        for item in root.findall('.//ITEM'):
            crn = item.find('ICO').text if item.find('ICO') is not None else None
            tax_id = item.find('DIC').text if item.find('DIC') is not None else None
            vat_id = item.find('IC_DPH').text if item.find('IC_DPH') is not None else None
            if crn and re.match(r'^\d{8}$', crn):
                if crn not in companies_dict:
                    companies_dict[crn] = {'tax_id': tax_id, 'vat_id': vat_id}
                else:
                    if tax_id:
                        companies_dict[crn]['tax_id'] = tax_id
                    if vat_id:
                        companies_dict[crn]['vat_id'] = vat_id


def save_companies_to_db(companies_dict):
    for crn, data in companies_dict.items():
        crn_value = None if crn is None else crn
        tax_id_value = None if data['tax_id'] == "null" else data['tax_id']
        vat_id_value = None if data['vat_id'] == "null" else data['vat_id']

        Company.objects.get_or_create(
            crn=crn_value,
            defaults={
                'tax_id': tax_id_value,
                'vat_id': vat_id_value
            }
        )

